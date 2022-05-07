import sys
import ctypes
import sdl2

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

g_window = None
g_screen_surface = None
g_hello_world = None

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
    global g_hello_world

    success = True
    # NOTE: relative path is based on the current working directory instead of where
    # the python program is.
    image_path = 'image.bmp'
    g_hello_world = sdl2.SDL_LoadBMP(image_path.encode('utf-8'))
    if not g_hello_world:
        print(f'Unable to load iamge {image_path}! SDL Error: {sdl2.SDL_GetError()}')
        success = False
    return success

def close():
    global g_hello_world, g_window

    sdl2.SDL_FreeSurface(g_hello_world)
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

            while not quit:
                while sdl2.SDL_PollEvent(ctypes.byref(e)) != 0:
                    if e.type == sdl2.SDL_QUIT:
                        quit = True

                sdl2.SDL_BlitSurface(g_hello_world, None, g_screen_surface, None)
                sdl2.SDL_UpdateWindowSurface(g_window)
    
    close()
    return 0

if __name__ == '__main__':
    sys.exit(main())

