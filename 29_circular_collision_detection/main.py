import sys
import ctypes
import sdl2
import sdl2.sdlimage
import sdl2.sdlttf
from dataclasses import dataclass

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

@dataclass
class Circle:
    x: int = 0
    y: int = 0
    r: int = 0

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

DOT_WIDTH = 20
DOT_HEIGHT = 20
DOT_VEL = 1
@dataclass
class Dot:
    pos_x: int = 0
    pos_y: int = 0
    vel_x: int = 0
    vel_y: int = 0

    def __post_init__(self):
        self._collider = Circle(x=self.pos_x, y=self.pos_y, r=DOT_WIDTH//2)
        self.shift_colliders()

    def handle_event(self, e):
        if e.type == sdl2.SDL_KEYDOWN and e.key.repeat == 0:
            if e.key.keysym.sym == sdl2.SDLK_UP: self.vel_y -= DOT_VEL
            elif e.key.keysym.sym == sdl2.SDLK_DOWN: self.vel_y += DOT_VEL
            elif e.key.keysym.sym == sdl2.SDLK_LEFT: self.vel_x -= DOT_VEL
            elif e.key.keysym.sym == sdl2.SDLK_RIGHT: self.vel_x += DOT_VEL
    
    def move(self, square, circle):
        self.pos_x += self.vel_x
        self.shift_colliders()
        if (self.pos_x < 0
                or (self.pos_x + DOT_WIDTH > SCREEN_WIDTH)
                or check_collision(self._collider, square)
                or check_collision(self._collider, circle)):
            self.pos_x -= self.vel_x
            self.shift_colliders()

        self.pos_y += self.vel_y
        self.shift_colliders()
        if (self.pos_y < 0
                or (self.pos_y + DOT_HEIGHT > SCREEN_HEIGHT)
                or check_collision(self._collider, square)
                or check_collision(self._collider, circle)):
            self.pos_y -= self.vel_y
            self.shift_colliders()

    def shift_colliders(self):
        # NOTE: the blog post actually did not have the code for this method
        # but it's easy enough to figure it out yourself.
        self._collider.x = self.pos_x
        self._collider.y = self.pos_y

    def render(self):
        g_dot_texture.render(self.pos_x - self._collider.r, self.pos_y - self._collider.r)

    def get_collider(self): return self._collider

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

def distance_squared(x1, y1, x2, y2):
    return (x2-x1)**2+(y2-y1)**2

# NOTE: we don't have function overload in python so we dispatch
# at runtime:
def check_collision(a, b):
    if type(a) == Circle:
        if type(b) == Circle:
            total_radius_sqared = (a.r + b.r) ** 2
            return distance_squared(a.x, a.y, b.x, b.y) < total_radius_sqared
        else:
            cx = (
                b.x if a.x < b.x
                else b.x + b.w if a.x > b.x + b.w
                else a.x
            )
            cy = (
                b.y if a.y < b.y
                else b.y + b.h if a.y > b.y + b.h
                else a.y
            )
            return distance_squared(a.x, a.y, cx, cy) < (a.r**2)
    else:
        left_a = a.x
        right_a = a.x + a.w
        top_a = a.y
        bottom_a = a.y + a.h
        left_b = b.x
        right_b = b.x + b.w
        top_b = b.y
        bottom_b = b.y + b.h
        if (bottom_a <= top_b
            or top_a >= bottom_b
            or right_a <= left_b
            or left_a >= right_b): return False
        return True    

def load_media():
    success = True
    
    if not g_dot_texture.load_from_file('dot.png'):
        print(f'Failed to load dot texture')
        return False

    return success

def close():
    global g_window, g_renderer, g_font

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

            dot = Dot(DOT_WIDTH//2, DOT_HEIGHT//2)
            dot2 = Dot(SCREEN_HEIGHT//4, SCREEN_HEIGHT//4)
            wall = sdl2.SDL_Rect(x=300,y=40,w=40,h=400)
            while not quit:
                while sdl2.SDL_PollEvent(ctypes.byref(e)) != 0:
                    if e.type == sdl2.SDL_QUIT:
                        quit = True
                    dot.handle_event(e)

                dot.move(wall, dot2.get_collider())
                sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
                sdl2.SDL_RenderClear(g_renderer)

                sdl2.SDL_SetRenderDrawColor(g_renderer, 0, 0, 0, 0xff)
                sdl2.SDL_RenderDrawRect(g_renderer, wall)
                dot.render()
                dot2.render()

                sdl2.SDL_RenderPresent(g_renderer)
    
    close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
