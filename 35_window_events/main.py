import os
import sys
import ctypes
import sdl2
import sdl2.sdlimage
import sdl2.sdlttf

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

class LWindow:
    def __init__(self):
        self._window = None
        self._width = 0
        self._height = 0
        self._mouse_focus = False
        self._keyboard_focus = False
        self._full_screen = False
        self._minimized = False

    def has_mouse_focus(self): return self._mouse_focus
    def has_keyboard_focus(self): return self._keyboard_focus
    def is_minimized(self): return self._minimized
    def get_width(self): return self._width
    def get_height(self): return self._height

    def init(self):
        self._window = sdl2.SDL_CreateWindow(
            "SDL Turtorial".encode(),
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            sdl2.SDL_WINDOW_SHOWN|sdl2.SDL_WINDOW_RESIZABLE
        )
        if self._window:
            self._mouse_focus = True
            self._keyboard_focus = True
            self._width = SCREEN_WIDTH
            self._height = SCREEN_HEIGHT
        return bool(self._window)

    def create_renderer(self):
        return sdl2.SDL_CreateRenderer(
            self._window,
            -1,
            sdl2.SDL_RENDERER_ACCELERATED|sdl2.SDL_RENDERER_PRESENTVSYNC
        )

    def handle_event(self, e):
        if e.type == sdl2.SDL_WINDOWEVENT:
            update_caption = False
            if e.window.event == sdl2.SDL_WINDOWEVENT_SIZE_CHANGED:
                self._width = e.window.data1
                self._height = e.window.data2
                sdl2.SDL_RenderPresent(g_renderer)
            elif e.window.event == sdl2.SDL_WINDOWEVENT_EXPOSED:
                sdl2.SDL_RenderPresent(g_renderer)
            elif e.window.event == sdl2.SDL_WINDOWEVENT_ENTER:
                self._mouse_focus = True
                update_caption = True
            elif e.window.event == sdl2.SDL_WINDOWEVENT_LEAVE:
                self._mouse_focus = False
                update_caption = True
            elif e.window.event == sdl2.SDL_WINDOWEVENT_FOCUS_GAINED:
                self._keyboard_focus = True
                update_caption = True
            elif e.window.event == sdl2.SDL_WINDOWEVENT_FOCUS_LOST:
                self._keyboard_focus = False
                update_caption = True
            elif e.window.event == sdl2.SDL_WINDOWEVENT_MINIMIZED:
                self._minimized = True
            elif e.window.event == sdl2.SDL_WINDOWEVENT_MAXIMIZED:
                self._minimized = False
            elif e.window.event == sdl2.SDL_WINDOWEVENT_RESTORED:
                self._minimized = False

            if update_caption:
                sdl2.SDL_SetWindowTitle(self._window, f'SDL Turtorial - MouseFocus {"On" if self._mouse_focus else "Off"} KeyFocus {"On" if self._keyboard_focus else "Off"}'.encode())
        elif e.type == sdl2.SDL_KEYDOWN and e.key.keysym.sym == sdl2.SDLK_RETURN:
            if self._full_screen:
                sdl2.SDL_SetWindowFullscreen(self._window, sdl2.SDL_FALSE)
                self._full_screen = False
            else:
                sdl2.SDL_SetWindowFullscreen(self._window, sdl2.SDL_TRUE)
                self._full_screen = True
                self._minimized = False

    def free(self):
        sdl2.SDL_DestroyWindow(self._window)
        self._window = None

class LTexture:
    def __init__(self):
        self._texture = None
        self._width = 0
        self._height = 0

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

g_window = LWindow()
g_renderer = None
g_font = None
g_texture = LTexture()

def init():
    global g_window, g_renderer

    success = True
    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0:
        print(f'SDL could not initialize! SDL_Error: {sdl2.SDL_GetError()}')
        success = False
    else:
        if not g_window.init():
            print(f'Window could not be created! SDL_Error: {sdl2.SDL_GetError()}')
            success = False
        else:
            g_renderer = g_window.create_renderer()
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
    global g_texture, g_font

    success = True
    if not g_texture.load_from_file('bg.png'):
        print(f'Failed to render text texture!')
        success = False

    return success

def close():
    global g_window, g_renderer

    g_texture.free()

    sdl2.SDL_DestroyRenderer(g_renderer)
    g_renderer = None
    g_window.free()
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

            sdl2.SDL_StartTextInput()
            while not quit:
                while sdl2.SDL_PollEvent(ctypes.byref(e)) != 0:
                    if e.type == sdl2.SDL_QUIT:
                        quit = True
                    g_window.handle_event(e)

                if not g_window.is_minimized():
                    sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
                    sdl2.SDL_RenderClear(g_renderer)
    
                    g_texture.render(
                        (g_window.get_width() - g_texture.get_width())//2,
                        (g_window.get_height() - g_texture.get_height())//2,
                    )
                    
                    sdl2.SDL_RenderPresent(g_renderer)

            sdl2.SDL_StopTextInput()
    close()
    return 0

if __name__ == '__main__':
    sys.exit(main())

