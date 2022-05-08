import sys
import enum
import ctypes
import sdl2
import sdl2.sdlimage

SDL2_SDLTTF_AVAILABLE = False
try:
    import sdl2.sdlttf
    SDL2_SDLTTF_AVAILABLE = True
except:
    pass

# NOTE: SDL_GetKeyboardState returns *the current snapshot of keyboard*

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

@enum.unique
class LSpriteClipType(enum.IntEnum):
    DEFAULT = 0
    UP = enum.auto()
    DOWN = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()
    TOTAL = enum.auto()

class LTexture:
    def __init__(self):
        self._m_texture = None
        self._m_width = None
        self._m_height = None

        self._destroyed = True

    def get_width(self):
        return self._m_width

    def get_height(self):
        return self._m_height

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
                self._m_width = surface.contents.w
                self._m_height = surface.contents.h
                self._destroyed = False
                self._m_texture = new_texture
            sdl2.SDL_FreeSurface(surface)
        return new_texture is not None

    # NOTE: yes, you can do this in python...
    if SDL2_SDLTTF_AVAILABLE:
        def load_from_rendered_text(self, texture_text: str, color: sdl2.SDL_Color):
            self.free()
            text_surface = sdl2.sdlttf.TTF_RenderText_Solid(g_font, texture_text.encode(), color)
            if not text_surface:
                print(f'Unable to render text surface! SDL_ttf Error: {sdl2.sdlttf.TTF_GetError().decode()}')
            else:
                self._m_texture = sdl2.SDL_CreateTextureFromSurface(g_renderer, text_surface)
                if not self._m_texture:
                    print(f'Unable to create texture from rendered text! SDL Error: {sdl2.SDL_GetError().decode()}')
                else:
                    self._m_width = text_surface.contents.w
                    self._m_height = text_surface.contents.h
                sdl2.SDL_FreeSurface(text_surface)
            return self._m_texture is not None

    def render(self,
            x: int, y: int,
            clip: sdl2.SDL_Rect = None,
            angle: float = 0,
            center: sdl2.SDL_Point = None,
            flip: sdl2.SDL_RendererFlip = sdl2.SDL_FLIP_NONE
    ):
        render_quad = sdl2.SDL_Rect(x=x,y=y,w=self._m_width, h=self._m_height)
        if clip:
            render_quad.w = clip.w
            render_quad.h = clip.h
        sdl2.SDL_RenderCopyEx(g_renderer, self._m_texture,
            clip,
            render_quad,
            angle, center,
            flip,
        )
    
    def set_color(self, red: int, green: int, blue: int):
        sdl2.SDL_SetTextureColorMod(self._m_texture, red, green, blue)

    def set_blend_mode(self, mode: sdl2.SDL_BlendMode):
        sdl2.SDL_SetTextureBlendMode(self._m_texture, mode)
    
    def set_alpha(self, alpha: int):
        sdl2.SDL_SetTextureAlphaMod(self._m_texture, alpha)
    
    def free(self):
        if not self._destroyed and self._m_texture:
            sdl2.SDL_DestroyTexture(self._m_texture)
            self._m_width = 0
            self._m_height = 0

g_window = None
g_renderer = None
g_font = None
g_texture_list = [LTexture() for _ in range(LSpriteClipType.TOTAL)]

def init():
    global g_window, g_screen_surface, g_renderer

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
    global g_texture_list

    if not g_texture_list[0].load_from_file('image.png'):
        print(f'Failed to load default texture!')
        return False
        
    if not g_texture_list[1].load_from_file('image_up.png'):
        print(f'Failed to load up texture!')
        return False
        
    if not g_texture_list[2].load_from_file('image_down.png'):
        print(f'Failed to load down sprite!')
        return False
        
    if not g_texture_list[3].load_from_file('image_left.png'):
        print(f'Failed to load left sprite!')
        return False

    if not g_texture_list[4].load_from_file('image_right.png'):
        print(f'Failed to load right sprite!')
        return False

    return True

def close():
    global g_window, g_renderer, g_sprite

    g_sprite.free()
    g_sprite = None

    sdl2.SDL_DestroyRenderer(g_renderer)
    g_renderer = None
    sdl2.SDL_DestroyWindow(g_window)
    g_window = None
    if SDL2_SDLTTF_AVAILABLE:
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
            current_texture = g_texture_list[0]
            e = sdl2.SDL_Event()

            while not quit:
                while sdl2.SDL_PollEvent(ctypes.byref(e)) != 0:
                    if e.type == sdl2.SDL_QUIT:
                        quit = True

                    states = sdl2.SDL_GetKeyboardState(None)
                    print('Current pressed-down arrow key number:', sum(states[i] for i in [
                        sdl2.SDL_SCANCODE_UP,
                        sdl2.SDL_SCANCODE_DOWN,
                        sdl2.SDL_SCANCODE_LEFT,
                        sdl2.SDL_SCANCODE_RIGHT,
                    ]))

                    current_texture = (
                        g_texture_list[1] if states[sdl2.SDL_SCANCODE_UP]
                        else g_texture_list[2] if states[sdl2.SDL_SCANCODE_DOWN]
                        else g_texture_list[3] if states[sdl2.SDL_SCANCODE_LEFT]
                        else g_texture_list[4] if states[sdl2.SDL_SCANCODE_RIGHT]
                        else g_texture_list[0]
                    )

                sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
                sdl2.SDL_RenderClear(g_renderer)
                current_texture.render(0, 0)
                sdl2.SDL_RenderPresent(g_renderer)

    
    close()
    return 0

if __name__ == '__main__':
    sys.exit(main())

