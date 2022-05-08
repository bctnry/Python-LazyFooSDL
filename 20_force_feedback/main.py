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
g_texture = LTexture()
# NOTE: the original code uses 3 different API to support older version of SDL.
# the newest one of them is SDL_GameController.
g_joystick = None
g_haptic = sdl2.SDL_Haptic()
g_game_controller = None

def init():
    global g_window, g_joystick, g_game_controller, g_haptic, g_renderer

    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO|sdl2.SDL_INIT_JOYSTICK|sdl2.SDL_INIT_HAPTIC|sdl2.SDL_INIT_GAMECONTROLLER) < 0:
        print(f'SDL could not initialize! SDL_Error: {sdl2.SDL_GetError()}')
        return False

    # NOTE: if this is not present then when the sprite is rendered there'll be
    # a jagged edge, but when this is present the sprite will have a blurred edge.
    if not sdl2.SDL_SetHint(sdl2.SDL_HINT_RENDER_SCALE_QUALITY, "1".encode()):
        print('Warning: linear texture filtering not enabled.')

    if sdl2.SDL_NumJoysticks() < 1:
        print('Warning: no joysticks connected')
    else:
        if not sdl2.SDL_IsGameController(0):
            print(f'Warning: Joystick is not compatible with SDL GameController interface. SDL Error: {sdl2.SDL_GetError().decode()}')
        else:
            g_game_controller = sdl2.SDL_GameControllerOpen(0)
            if not sdl2.SDL_GameControllerHasRumble(g_game_controller):
                print(f'Warning: Game controller does not have rumble. {sdl2.SDL_GetError().decode()}')
        if not g_game_controller:
            g_joystick = sdl2.SDL_JoystickOpen(0)
            if not g_joystick:
                print(f'Warning: Unable to open game controller! SDL Error: {sdl2.SDL_GetError().decode()}')
            else:
                if not sdl2.SDL_JoystickIsHaptic(g_joystick):
                    print(f'Warning: Controller does not support haptics. SDL Error: {sdl2.SDL_GetError().decode()}')
                else:
                    if not sdl2.SDL_HapticRumbleInit(ctypes.byref(g_haptic)):
                        print(f'Warning: Failed to initialize haptic rumble. SDL Error: {sdl2.SDL_GetError().decode()}')

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
    global g_texture

    success = True
    if not g_texture.load_from_file('texture.png'):
        print(f'Failed to load foreground texture!')
        success = False

    return success

def close():
    global g_window, g_renderer, g_joystick, g_haptic, g_game_controller

    g_texture.free()

    if g_game_controller: sdl2.SDL_GameControllerClose(g_game_controller)
    if g_haptic: sdl2.SDL_HapticClose(g_haptic)
    if g_joystick: sdl2.SDL_JoystickClose(g_joystick)
    
    g_game_controller = None
    g_haptic = None
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

            while not quit:
                while sdl2.SDL_PollEvent(ctypes.byref(e)) != 0:
                    if e.type == sdl2.SDL_QUIT:
                        quit = True
                    elif e.type == sdl2.SDL_JOYBUTTONDOWN:
                        if g_game_controller:
                            if sdl2.SDL_GameControllerRumble(g_game_controller, 0xffff * 3 // 4, 0xffff * 3 // 4, 500):
                                print(f'Warning: unable to play game controller rumble. SDL Error: {sdl2.SDL_GetError().decode()}')
                        elif g_haptic:
                            if sdl2.SDL_HapticRumblePlay(g_haptic, 0.75, 500):
                                print(f'Warning: unable to play haptic rumble. SDL Error: {sdl2.SDL_GetError().decode()}')

                sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
                sdl2.SDL_RenderClear(g_renderer)

                g_texture.render(
                    (SCREEN_WIDTH - g_texture.get_width())//2,
                    (SCREEN_HEIGHT - g_texture.get_height())//2,
                )

                sdl2.SDL_RenderPresent(g_renderer)
    
    close()
    return 0

if __name__ == '__main__':
    sys.exit(main())

