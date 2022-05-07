import sys
import ctypes
import sdl2
import sdl2.sdlimage

# NOTE: the texture I used here is the so-called "XOR texture", which is probably the most
# famous texture in "old-school" demoscene because the code to generate this is very small
# so it can easily fit in tight size restrictions.

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

g_window = None
g_renderer = None
g_texture = None

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
            g_renderer = sdl2.SDL_CreateRenderer(g_window, -1, sdl2.SDL_RENDERER_ACCELERATED)
            if not g_renderer:
                print(f'Renderer could not be created! SDL Error: {sdl2.SDL_GetError().decode()}')
                success = False
            else:
                sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
                img_flags = sdl2.sdlimage.IMG_INIT_PNG
                if not (sdl2.sdlimage.IMG_Init(img_flags) & img_flags):
                    print(f'SDL_image could not initialize! SDL_image Error: {sdl2.sdlimage.IMG_GetError().decode()}')
                    success = False


    return success

def load_media():
    success = True
    return success

def close():
    global g_texture, g_window, g_renderer

    sdl2.SDL_DestroyTexture(g_texture)
    g_texture = None
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
                sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
                sdl2.SDL_RenderClear(g_renderer)
                
                fill_rect = sdl2.SDL_Rect(x=SCREEN_WIDTH//4,y=SCREEN_HEIGHT//4,w=SCREEN_WIDTH//2,h=SCREEN_HEIGHT//2)
                sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0, 0, 0xff)
                sdl2.SDL_RenderFillRect(g_renderer, fill_rect)

                outline_rect = sdl2.SDL_Rect(x=SCREEN_WIDTH//6,y=SCREEN_HEIGHT//6,w=SCREEN_WIDTH*2//3,h=SCREEN_HEIGHT*2//3)
                sdl2.SDL_SetRenderDrawColor(g_renderer, 0, 0xff, 0, 0xff)
                sdl2.SDL_RenderDrawRect(g_renderer, outline_rect)

                sdl2.SDL_SetRenderDrawColor(g_renderer, 0, 0, 0xff, 0xff)
                sdl2.SDL_RenderDrawLine(g_renderer, 0, SCREEN_HEIGHT//2, SCREEN_WIDTH, SCREEN_HEIGHT//2)

                sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0, 0xff)
                for i in range(0, SCREEN_HEIGHT, 4):
                    sdl2.SDL_RenderDrawPoint(g_renderer, SCREEN_WIDTH//2, i)
                    
                sdl2.SDL_RenderPresent(g_renderer)
    
    close()
    return 0

if __name__ == '__main__':
    sys.exit(main())

