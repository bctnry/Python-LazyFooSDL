import sys
import ctypes
import sdl2
import enum

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# NOTE: yes. this is how you do enum in python.
class KeyPressSurfaces(enum.Enum):
    # NOTE: normally `enum.auto` would be the exact one-to-one
    # correspondence "readability-wise", but for some reasons
    # enum.auto starts with 1, so be careful when using it.
    KEY_PRESS_SURFACE_DEFAULT = 0
    KEY_PRESS_SURFACE_UP = enum.auto()
    KEY_PRESS_SURFACE_DOWN = enum.auto()
    KEY_PRESS_SURFACE_LEFT = enum.auto()
    KEY_PRESS_SURFACE_RIGHT = enum.auto()
    KEY_PRESS_SURFACE_TOTAL = enum.auto()


g_window = None
g_screen_surface = None
g_key_surfaces = {}

def load_surface(p: str):
    surface = sdl2.SDL_LoadBMP(p.encode())
    if not surface:
        print(f'Unable to load iamge {p}! SDL Error: {sdl2.SDL_GetError().decode()}')
        return None
    return surface

def init():
    global g_window, g_screen_surface

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
            g_screen_surface = sdl2.SDL_GetWindowSurface(g_window)

    return success

def load_media():
    global g_key_surfaces

    success = True

    g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_DEFAULT] = load_surface('image.bmp')
    if not g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_DEFAULT]:
        print('Failed to load default image!')
        success = False

    g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_UP] = load_surface('image_up.bmp')
    if not g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_UP]:
        print('Failed to load up image!')
        success = False

    g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_DOWN] = load_surface('image_down.bmp')
    if not g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_DOWN]:
        print('Failed to load down image!')
        success = False

    g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_LEFT] = load_surface('image_left.bmp')
    if not g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_LEFT]:
        print('Failed to load left image!')
        success = False

    g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_RIGHT] = load_surface('image_right.bmp')
    if not g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_RIGHT]:
        print('Failed to load right image!')
        success = False

    return success

def close():
    global g_key_surfaces, g_window

    for k in g_key_surfaces:
        sdl2.SDL_FreeSurface(g_key_surfaces[k])
    sdl2.SDL_DestroyWindow(g_window)
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

            g_current_surface = g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_DEFAULT]

            while not quit:
                while sdl2.SDL_PollEvent(ctypes.byref(e)) != 0:
                    if e.type == sdl2.SDL_QUIT:
                        quit = True
                    elif e.type == sdl2.SDL_KEYDOWN:
                        # NOTE: we don't have switch in python even if it fits well
                        # with python syntax-wise. oh well.
                        if e.key.keysym.sym == sdl2.SDLK_UP: g_current_surface = g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_UP]
                        elif e.key.keysym.sym == sdl2.SDLK_DOWN: g_current_surface = g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_DOWN]
                        elif e.key.keysym.sym == sdl2.SDLK_LEFT: g_current_surface = g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_LEFT]
                        elif e.key.keysym.sym == sdl2.SDLK_RIGHT: g_current_surface = g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_RIGHT]
                        else:
                            g_current_surface = g_key_surfaces[KeyPressSurfaces.KEY_PRESS_SURFACE_DEFAULT]
                            print(e.key.keysym.sym)

                sdl2.SDL_BlitSurface(g_current_surface, None, g_screen_surface, None)
                sdl2.SDL_UpdateWindowSurface(g_window)
    
    close()
    return 0

if __name__ == '__main__':
    sys.exit(main())

