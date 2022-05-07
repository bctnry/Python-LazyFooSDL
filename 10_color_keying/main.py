import sys
import ctypes
import sdl2
import sdl2.sdlimage

# NOTE: the texture I used here is the so-called "XOR texture", which is probably the most
# famous texture in "old-school" demoscene because the code to generate this is very small
# so it can easily fit in tight size restrictions.

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

class LTexture:
    def __init__(self):
        self._m_texture = None
        self._m_width = None
        self._m_height = None

        self._destroyed = True

    # NOTE: you can also use prop to make getters for width and height.
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
            # NOTE: i used the bright magenta color here. it works the same as the original (which uses cyan) though.
            sdl2.SDL_SetColorKey(surface, sdl2.SDL_TRUE, sdl2.SDL_MapRGB(surface.contents.format, 0xff, 0, 0xff))
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

    def render(self, x: int, y: int):
        render_quad = sdl2.SDL_Rect(x=x,y=y,w=self._m_width, h=self._m_height)
        sdl2.SDL_RenderCopy(g_renderer, self._m_texture, None, render_quad)
    
    def free(self):
        # NOTE: python objects are freed by the os.
        # calling this method does not make the actual LTexture
        # object to be freed, but the texture obj in SDL will.
        # this is not how I prefer to do things, but to avoid
        # further confusion...
        if not self._destroyed and self._m_texture:
            sdl2.SDL_DestroyTexture(self._m_texture)
            self._m_width = 0
            self._m_height = 0

g_window = None
g_renderer = None
g_bg_texture = LTexture()
g_fg_texture = LTexture()

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
    global g_fg_texture, g_bg_texture

    success = True
    if not g_fg_texture.load_from_file('fg.png'):
        print(f'Failed to load foreground texture!')
        success = False
    if not g_bg_texture.load_from_file('bg.png'):
        print(f'Failed to load background texture!')
        success = False

    return success

def close():
    global g_window, g_renderer

    g_fg_texture.free()
    g_bg_texture.free()

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

                # NOTE: when SDL_RenderClear, SDL will use the render draw color to
                # fill in as the default background color. we set it to white here.
                sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
                sdl2.SDL_RenderClear(g_renderer)

                g_bg_texture.render(0, 0)
                g_fg_texture.render(380, 145)

                sdl2.SDL_RenderPresent(g_renderer)
    
    close()
    return 0

if __name__ == '__main__':
    sys.exit(main())

