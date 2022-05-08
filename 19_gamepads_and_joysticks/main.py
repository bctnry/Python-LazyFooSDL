import sys
import math
import ctypes
import sdl2
import sdl2.sdlimage

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
JOYSTICK_DEAD_ZONE = 8000

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
g_sprite = LTexture()
g_joystick = None

def init():
    global g_window, g_joystick, g_renderer

    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO|sdl2.SDL_INIT_JOYSTICK) < 0:
        print(f'SDL could not initialize! SDL_Error: {sdl2.SDL_GetError()}')
        return False

    # NOTE: if this is not present then when the sprite is rendered there'll be
    # a jagged edge, but when this is present the sprite will have a blurred edge.
    if not sdl2.SDL_SetHint(sdl2.SDL_HINT_RENDER_SCALE_QUALITY, "1".encode()):
        print('Warning: linear texture filtering not enabled.')

    if sdl2.SDL_NumJoysticks() < 1:
        print('Warning: no joysticks connected')
    else:
        g_joystick = sdl2.SDL_JoystickOpen(0)
        if not g_joystick:
            print(f'Warning: Unable to open game controller! SDL Error: {sdl2.SDL_GetError().decode()}')

    g_window = sdl2.SDL_CreateWindow(
        "SDL Turtorial".encode('utf-8'),
        sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED,
        SCREEN_WIDTH, SCREEN_HEIGHT,
        sdl2.SDL_WINDOW_SHOWN,
    )
    if not g_window:
        print(f'Window could not be created! SDL_Error: {sdl2.SDL_GetError()}')
        return False
    
    g_renderer = sdl2.SDL_CreateRenderer(g_window, -1, sdl2.SDL_RENDERER_ACCELERATED|sdl2.SDL_RENDERER_PRESENTVSYNC)
    if not g_renderer:
        print(f'Renderer could not be created! SDL Error: {sdl2.SDL_GetError().decode()}')
        return False
    
    sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
    img_flags = sdl2.sdlimage.IMG_INIT_PNG
    if not (sdl2.sdlimage.IMG_Init(img_flags) & img_flags):
        print(f'SDL_image could not initialize! SDL_image Error: {sdl2.sdlimage.IMG_GetError().decode()}')
        return False

    return True


def load_media():
    global g_sprite

    success = True
    if not g_sprite.load_from_file('sprite.png'):
        print(f'Failed to load foreground texture!')
        success = False

    return success

def close():
    global g_window, g_renderer, g_joystick

    g_sprite.free()

    sdl2.SDL_JoystickClose(g_joystick)
    g_joystick = None

    sdl2.SDL_DestroyRenderer(g_renderer)
    g_renderer = None
    sdl2.SDL_DestroyWindow(g_window)
    g_window = None
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

            x_dir = 0
            y_dir = 0

            while not quit:
                while sdl2.SDL_PollEvent(ctypes.byref(e)) != 0:
                    if e.type == sdl2.SDL_QUIT:
                        quit = True
                    elif e.type == sdl2.SDL_JOYAXISMOTION:
                        if e.jaxis.which == 0:
                            if e.jaxis.axis == 0:
                                if e.jaxis.value < -JOYSTICK_DEAD_ZONE:
                                    x_dir = -1
                                elif e.jaxis.value > JOYSTICK_DEAD_ZONE:
                                    x_dir = 1
                                else:
                                    x_dir = 0
                            elif e.jaxis.axis == 1:
                                if e.jaxis.value < -JOYSTICK_DEAD_ZONE:
                                    y_dir = -1
                                elif e.jaxis.value > JOYSTICK_DEAD_ZONE:
                                    y_dir = 1
                                else:
                                    y_dir = 0

                sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
                sdl2.SDL_RenderClear(g_renderer)
                joystick_angle = math.degrees(math.atan2(y_dir, x_dir))
                if x_dir == 0 and y_dir == 0: joystick_angle = 0

                g_sprite.render(
                    (SCREEN_WIDTH - g_sprite.get_width())//2,
                    (SCREEN_HEIGHT - g_sprite.get_height())//2,
                    None,
                    joystick_angle,
                )

                sdl2.SDL_RenderPresent(g_renderer)
    
    close()
    return 0

if __name__ == '__main__':
    sys.exit(main())

