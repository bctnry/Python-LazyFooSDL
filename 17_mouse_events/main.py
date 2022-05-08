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

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

BUTTON_WIDTH = 300
BUTTON_HEIGHT = 200
TOTAL_BUTTONS = 4

@enum.unique
class LButtonSprite(enum.IntEnum):
    BUTTON_SPRITE_MOUSE_OUT = 0
    BUTTON_SPRITE_MOUSE_OVER_MOTION = enum.auto()
    BUTTON_SPRITE_MOUSE_OVER_DOWN = enum.auto()
    BUTTON_SPRITE_MOUSE_OVER_UP = enum.auto()
    BUTTON_SPRITE_TOTAL = enum.auto()

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

class LButton:
    def __init__(self):
        self._m_position = sdl2.SDL_Point()
        self._m_current_sprite = LButtonSprite.BUTTON_SPRITE_MOUSE_OUT

    def set_position(self, x: int, y: int):
        self._m_position.x = x
        self._m_position.y = y

    def handle_event(self, e: sdl2.SDL_Event):
        if (e.type == sdl2.SDL_MOUSEMOTION
                or e.type == sdl2.SDL_MOUSEBUTTONDOWN
                or e.type == sdl2.SDL_MOUSEBUTTONUP):
            # NOTE: SDL_GetMouseState passes by ref, so we have to act accordingly.
            # the return value is actually the state of the mouse buttons.
            x = ctypes.c_int(); y = ctypes.c_int()
            sdl2.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
            outside = (
                x.value < self._m_position.x
                or x.value > (self._m_position.x + BUTTON_WIDTH)
                or y.value < self._m_position.y
                or y.value > (self._m_position.y + BUTTON_HEIGHT)
            )
            if outside:
                self._m_current_sprite = LButtonSprite.BUTTON_SPRITE_MOUSE_OUT
            else:
                self._m_current_sprite = (
                    LButtonSprite.BUTTON_SPRITE_MOUSE_OVER_MOTION if e.type == sdl2.SDL_MOUSEMOTION
                    else LButtonSprite.BUTTON_SPRITE_MOUSE_OVER_DOWN if e.type == sdl2.SDL_MOUSEBUTTONDOWN
                    else LButtonSprite.BUTTON_SPRITE_MOUSE_OVER_UP if e.type == sdl2.SDL_MOUSEBUTTONUP
                    else LButtonSprite.BUTTON_SPRITE_MOUSE_OUT # impossible
                )

    def render(self):
        g_sprite.render(
            self._m_position.x,
            self._m_position.y,
            g_sprite_clips[self._m_current_sprite]
        )

g_buttons = [LButton(), LButton(), LButton(), LButton()]
g_window = None
g_renderer = None
g_font = None
g_sprite_clips = []
g_sprite = LTexture()

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
    global g_sprite, g_sprite_clips

    if not g_sprite.load_from_file('sprite.png'):
        print(f'Failed to load sprite!')
        return False

    g_sprite_clips = [
        sdl2.SDL_Rect(x=0,y=0,w=BUTTON_WIDTH,h=BUTTON_HEIGHT),
        sdl2.SDL_Rect(x=0,y=BUTTON_HEIGHT,w=BUTTON_WIDTH,h=BUTTON_HEIGHT),
        sdl2.SDL_Rect(x=BUTTON_WIDTH,y=BUTTON_HEIGHT,w=BUTTON_WIDTH,h=BUTTON_HEIGHT),
        sdl2.SDL_Rect(x=BUTTON_WIDTH,y=0,w=BUTTON_WIDTH,h=BUTTON_HEIGHT),
    ]

    # NOTE: we initialize the buttons here as well.
    g_buttons[0].set_position(0, 0)
    g_buttons[1].set_position(BUTTON_WIDTH, 0)
    g_buttons[2].set_position(0, BUTTON_HEIGHT)
    g_buttons[3].set_position(BUTTON_WIDTH, BUTTON_HEIGHT)

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
            e = sdl2.SDL_Event()

            while not quit:
                while sdl2.SDL_PollEvent(ctypes.byref(e)) != 0:
                    if e.type == sdl2.SDL_QUIT:
                        quit = True

                    for btn in g_buttons:
                        btn.handle_event(e)

                sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
                sdl2.SDL_RenderClear(g_renderer)

                for btn in g_buttons:
                    btn.render()

                sdl2.SDL_RenderPresent(g_renderer)
    
    close()
    return 0

if __name__ == '__main__':
    sys.exit(main())

