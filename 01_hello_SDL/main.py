import sys
import sdl2

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

def main():
    window = None
    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0:
        print(f'SDL could not initialize! SDL_Error: {sdl2.SDL_GetError()}')
    else:
        window = sdl2.SDL_CreateWindow(
            # NOTE: this arg in python only accept bytes so we `.encode`.
            "SDL Turtorial".encode('utf-8'),
            sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            sdl2.SDL_WINDOW_SHOWN,
        )
        if not window:
            print(f'Window could not be created! SDL_Error: {sdl2.SDL_GetError()}')
        else:
            # NOTE: probably due to how ctypes works in python you need `.contents` here.
            screen_surface = sdl2.SDL_GetWindowSurface(window)
            sdl2.SDL_FillRect(screen_surface,
                None,
                sdl2.SDL_MapRGB(screen_surface.contents.format, 0x00, 0xff, 0xff),
            )
            sdl2.SDL_UpdateWindowSurface(window)
            sdl2.SDL_Delay(2000)
    
    if window:
        sdl2.SDL_DestroyWindow(window)
        sdl2.SDL_Quit()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

