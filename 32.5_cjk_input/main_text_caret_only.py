from ast import Lt
import sys
import ctypes
import sdl2
import sdl2.sdlimage
import sdl2.sdlttf

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

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

g_window = None
g_renderer = None
g_font = None
g_prompt = LTexture()
g_text_piece1 = LTexture()
g_text_piece2 = LTexture()

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
    global g_texture, g_font

    success = True
    g_font = sdl2.sdlttf.TTF_OpenFont('Cubic_11.ttf'.encode(), 11)
    if not g_font:
        print(f'Failed to load font! SDL_ttf Error: {sdl2.sdlttf.TTF_GetError().decode()}')
        success = False
    else:
        text_color = sdl2.SDL_Color(r=0, g=0, b=0, a=255)
        if not g_prompt.load_from_rendered_text('Enter text:', text_color):
            print(f'Failed to render text texture!')
            success = False

    return success

def close():
    global g_window, g_renderer, g_font

    g_text_piece1.free()
    g_text_piece2.free()

    sdl2.sdlttf.TTF_CloseFont(g_font)
    g_font = None
    sdl2.SDL_DestroyRenderer(g_renderer)
    g_renderer = None
    sdl2.SDL_DestroyWindow(g_window)
    g_window = None
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

            color = sdl2.SDL_Color(r=0,g=0,b=0,a=0xff)
            text = ''
            text_caret = 0
            sdl2.SDL_StartTextInput()
            while not quit:
                should_render_text = False
                while sdl2.SDL_PollEvent(ctypes.byref(e)) != 0:
                    if e.type == sdl2.SDL_QUIT:
                        quit = True
                    elif e.type == sdl2.SDL_TEXTINPUT:
                        if not ((sdl2.SDL_GetModState()&sdl2.KMOD_CTRL)
                                    and (e.text.text[0] in [ord('c'), ord('C'), ord('v'), ord('V')])):
                            old_piece1 = text[:text_caret]; old_piece2 = text[text_caret:]
                            text = old_piece1+e.text.text.decode()+old_piece2
                            text_caret = len(old_piece1) + len(e.text.text.decode())
                            should_render_text = True
                    elif e.type == sdl2.SDL_KEYDOWN:
                        if e.key.keysym.sym == sdl2.SDLK_UP:
                            text_caret = 0
                            should_render_text = True
                        elif e.key.keysym.sym == sdl2.SDLK_DOWN:
                            text_caret = len(text)
                            should_render_text = True
                        elif e.key.keysym.sym == sdl2.SDLK_LEFT:
                            if text_caret > 0:
                                text_caret -= 1
                                should_render_text = True
                        elif e.key.keysym.sym == sdl2.SDLK_RIGHT:
                            if text_caret < len(text):
                                text_caret += 1
                                should_render_text = True
                        elif e.key.keysym.sym == sdl2.SDLK_BACKSPACE and len(text) > 0:
                            if text_caret > 0:
                                text = text[:text_caret-1]+text[text_caret:]
                                text_caret -= 1
                                should_render_text = True
                        elif e.key.keysym.sym == sdl2.SDLK_c and (sdl2.SDL_GetModState()&sdl2.KMOD_CTRL):
                            sdl2.SDL_SetClipboardText(text.encode())
                        elif e.key.keysym.sym == sdl2.SDLK_v and (sdl2.SDL_GetModState()&sdl2.KMOD_CTRL):
                            text = sdl2.SDL_GetClipboardText().decode()
                            text_caret = len(text)
                            should_render_text = True
                                    
                sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
                sdl2.SDL_RenderClear(g_renderer)

                if should_render_text:
                    piece1 = text[:text_caret]; piece2 = text[text_caret:]
                    g_text_piece1.load_from_rendered_text(piece1 or ' ', color)
                    g_text_piece2.load_from_rendered_text(piece2 or ' ', color)
                    
                g_prompt.render(
                    (SCREEN_WIDTH - g_prompt.get_width())//2,
                    0,
                )
                total_width = g_text_piece1.get_width() + g_text_piece2.get_width()
                g_text_piece1.render(
                    (SCREEN_WIDTH - total_width)//2,
                    (SCREEN_HEIGHT - g_text_piece1.get_height())//2,
                )
                sdl2.SDL_SetRenderDrawColor(g_renderer, 0, 0, 0, 0xff)
                sdl2.SDL_RenderDrawLine(
                    g_renderer,
                    (SCREEN_WIDTH - total_width)//2+g_text_piece1.get_width(),
                    (SCREEN_HEIGHT - g_text_piece1.get_height())//2,
                    (SCREEN_WIDTH - total_width)//2+g_text_piece1.get_width(),
                    (SCREEN_HEIGHT - g_text_piece1.get_height())//2+g_text_piece1.get_height(),
                )
                g_text_piece2.render(
                    (SCREEN_WIDTH - total_width)//2+g_text_piece1.get_width(),
                    (SCREEN_HEIGHT - g_text_piece1.get_height())//2,
                )
                
                sdl2.SDL_RenderPresent(g_renderer)

            sdl2.SDL_StopTextInput()
    close()
    return 0

if __name__ == '__main__':
    sys.exit(main())

