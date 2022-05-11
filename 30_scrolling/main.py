import sys
import ctypes
import sdl2
import sdl2.sdlimage
import sdl2.sdlttf
from dataclasses import dataclass

LEVEL_WIDTH = 1280
LEVEL_HEIGHT = 960
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

class LTexture:
    def __init__(self):
        self._texture = None
        self._width = None
        self._height = None

        self._destroyed = True

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def load_from_file(self, p: str) -> bool :
        self.free()
        new_texture = None
        surface = sdl2.sdlimage.IMG_Load(p.encode())
        if not surface:
            print(f'Unable to load image {p}! SDL_image Error: {sdl2.sdlimage.IMG_GetError().decode()}')
        else:
            # NOTE: i switched to cyan here because bright magenta is killing my eyes
            sdl2.SDL_SetColorKey(surface, sdl2.SDL_TRUE, sdl2.SDL_MapRGB(surface.contents.format, 0, 0xff, 0xff))
            new_texture = sdl2.SDL_CreateTextureFromSurface(g_renderer, surface)
            if not new_texture:
                print(f'Unable to create texture from {p}! SDL Error: {sdl2.SDL_GetError().decode()}')
            else:
                self._width = surface.contents.w
                self._height = surface.contents.h
                self._destroyed = False
                self._texture = new_texture
            sdl2.SDL_FreeSurface(surface)
        return new_texture is not None

    def load_from_rendered_text(self, texture_text: str, color: sdl2.SDL_Color):
        self.free()
        text_surface = sdl2.sdlttf.TTF_RenderText_Solid(g_font, texture_text.encode(), color)
        if not text_surface:
            print(f'Unable to render text surface! SDL_ttf Error: {sdl2.sdlttf.TTF_GetError().decode()}')
        else:
            self._texture = sdl2.SDL_CreateTextureFromSurface(g_renderer, text_surface)
            if not self._texture:
                print(f'Unable to create texture from rendered text! SDL Error: {sdl2.SDL_GetError().decode()}')
            else:
                self._width = text_surface.contents.w
                self._height = text_surface.contents.h
            sdl2.SDL_FreeSurface(text_surface)
        return self._texture is not None

    def render(self,
            x: int, y: int,
            clip: sdl2.SDL_Rect = None,
            angle: float = 0,
            center: sdl2.SDL_Point = None,
            flip: sdl2.SDL_RendererFlip = sdl2.SDL_FLIP_NONE
    ):
        render_quad = sdl2.SDL_Rect(x=x,y=y,w=self._width, h=self._height)
        if clip:
            render_quad.w = clip.w
            render_quad.h = clip.h
        sdl2.SDL_RenderCopyEx(g_renderer, self._texture,
            clip,
            render_quad,
            angle, center,
            flip,
        )
    
    def set_color(self, red: int, green: int, blue: int):
        sdl2.SDL_SetTextureColorMod(self._texture, red, green, blue)

    def set_blend_mode(self, mode: sdl2.SDL_BlendMode):
        sdl2.SDL_SetTextureBlendMode(self._texture, mode)
    
    def set_alpha(self, alpha: int):
        sdl2.SDL_SetTextureAlphaMod(self._texture, alpha)
    
    def free(self):
        if not self._destroyed and self._texture:
            sdl2.SDL_DestroyTexture(self._texture)
            self._width = 0
            self._height = 0

g_window = None
g_renderer = None
g_dot_texture = LTexture()
g_bg = LTexture()

DOT_WIDTH = 20
DOT_HEIGHT = 20
DOT_VEL = 10
@dataclass
class Dot:
    pos_x: int = 0
    pos_y: int = 0
    vel_x: int = 0
    vel_y: int = 0

    def handle_event(self, e):
        if e.type == sdl2.SDL_KEYDOWN and e.key.repeat == 0:
            if e.key.keysym.sym == sdl2.SDLK_UP: self.vel_y -= DOT_VEL
            elif e.key.keysym.sym == sdl2.SDLK_DOWN: self.vel_y += DOT_VEL
            elif e.key.keysym.sym == sdl2.SDLK_LEFT: self.vel_x -= DOT_VEL
            elif e.key.keysym.sym == sdl2.SDLK_RIGHT: self.vel_x += DOT_VEL
    
    def move(self):
        self.pos_x += self.vel_x
        if self.pos_x < 0 or (self.pos_x + DOT_WIDTH > LEVEL_WIDTH):
            self.pos_x -= self.vel_x

        self.pos_y += self.vel_y
        if self.pos_y < 0 or (self.pos_y + DOT_HEIGHT > LEVEL_HEIGHT):
            self.pos_y -= self.vel_y

    def render(self, cam_x: int, cam_y: int):
        ...
        g_dot_texture.render(self.pos_x-cam_x, self.pos_y-cam_y)

def init():
    global g_window, g_renderer

    success = True
    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0:
        print(f'SDL could not initialize! SDL_Error: {sdl2.SDL_GetError()}')
        success = False
    else:
        g_window = sdl2.SDL_CreateWindow(
            "SDL Turtorial".encode('utf-8'),
            sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            sdl2.SDL_WINDOW_SHOWN,
        )
        if not g_window:
            print(f'Window could not be created! SDL_Error: {sdl2.SDL_GetError()}')
            success = False
        else:
            g_renderer = sdl2.SDL_CreateRenderer(g_window, -1, sdl2.SDL_RENDERER_ACCELERATED|sdl2.SDL_RENDERER_PRESENTVSYNC)
            if not g_renderer:
                print(f'Renderer could not be created! SDL Error: {sdl2.SDL_GetError().decode()}')
                success = False
            else:
                sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
                img_flags = sdl2.sdlimage.IMG_INIT_PNG
                if not (sdl2.sdlimage.IMG_Init(img_flags) & img_flags):
                    print(f'SDL_image could not initialize! SDL_image Error: {sdl2.sdlimage.IMG_GetError().decode()}')
                    success = False
                if sdl2.sdlttf.TTF_Init() == -1:
                    print(f'SDL_ttf could not initialize! SDL_ttf Error: {sdl2.sdlttf.TTF_GetError().decode()}')
                    success = False

    return success


def load_media():
    success = True
    
    if not g_dot_texture.load_from_file('dot.png'):
        print(f'Failed to load dot texture')
        return False
    if not g_bg.load_from_file('bg.png'):
        print(f'Failed to load bg texture')

    return success

def close():
    global g_window, g_renderer

    g_bg.free()
    g_dot_texture.free()

    sdl2.SDL_DestroyRenderer(g_renderer)
    g_renderer = None
    sdl2.SDL_DestroyWindow(g_window)
    g_window = None
    sdl2.sdlttf.TTF_Quit()
    sdl2.sdlimage.IMG_Quit()
    sdl2.SDL_Quit()

def main():
    if not init():
        print('Failed to initialize!')
    else:
        if not load_media():
            print('Failed to load media!')
        else:
            quit = False
            e = sdl2.SDL_Event()

            dot = Dot()
            camera = sdl2.SDL_Rect(x=0,y=0,w=SCREEN_WIDTH,h=SCREEN_HEIGHT)
            while not quit:
                while sdl2.SDL_PollEvent(ctypes.byref(e)) != 0:
                    if e.type == sdl2.SDL_QUIT:
                        quit = True
                    dot.handle_event(e)

                dot.move()
                camera.x = int((dot.pos_x + DOT_WIDTH/2)-SCREEN_WIDTH/2)
                camera.y = int((dot.pos_y + DOT_HEIGHT/2)-SCREEN_HEIGHT/2)
                if camera.x < 0: camera.x = 0
                if camera.y < 0: camera.y = 0
                if camera.x > LEVEL_WIDTH - camera.w: camera.x = LEVEL_WIDTH - camera.w
                if camera.y > LEVEL_HEIGHT - camera.h: camera.y = LEVEL_HEIGHT - camera.h

                sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
                sdl2.SDL_RenderClear(g_renderer)
                
                g_bg.render(0, 0, camera)
                dot.render(camera.x, camera.y)

                sdl2.SDL_RenderPresent(g_renderer)
    
    close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
