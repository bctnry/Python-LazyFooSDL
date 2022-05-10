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

import sdl2.sdlmixer

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

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

g_window = None
g_renderer = None
g_texture = LTexture()
g_music = None
g_note = []

def init():
    global g_window, g_screen_surface, g_renderer

    success = True
    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO|sdl2.SDL_INIT_AUDIO) < 0:
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
            return False
        
        g_renderer = sdl2.SDL_CreateRenderer(g_window, -1, sdl2.SDL_RENDERER_ACCELERATED|sdl2.SDL_RENDERER_PRESENTVSYNC)
        if not g_renderer:
            print(f'Renderer could not be created! SDL Error: {sdl2.SDL_GetError().decode()}')
            return False
        
        sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
        img_flags = sdl2.sdlimage.IMG_INIT_PNG
        if not (sdl2.sdlimage.IMG_Init(img_flags) & img_flags):
            print(f'SDL_image could not initialize! SDL_image Error: {sdl2.sdlimage.IMG_GetError().decode()}')
            success = False
        
        # NOTE: yes, now it's Mix (instead of MIX) because it's not an abbreviation.
        if sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 8, 2048) < 0:
            print(f'SDL_mixer could not initialize. SDL_mixer Error: {sdl2.sdlmixer.Mix_GetError().decode()}')    

    return success


def load_media():
    global g_music

    success = True

    g_music = sdl2.sdlmixer.Mix_LoadMUS('influencia-do-jazz.mid'.encode())
    if not g_music:
        print(f'Failed to load music.')
        success = False
    
    for i in range(1, 6):
        note = sdl2.sdlmixer.Mix_LoadWAV(f'note_{i:02}.wav'.encode())
        if not note:
            print(f'Failed to load note {i}')
            success = False
        g_note.append(note)

    if not g_texture.load_from_file('texture.png'):
        print(f'Failed to load texture.')
        success = False

    return success

def close():
    global g_window, g_renderer, g_music, g_texture, g_note

    g_texture.free()
    g_texture = None

    for note in g_note:
        if note: sdl2.sdlmixer.Mix_FreeChunk(note)
    g_note = None

    sdl2.sdlmixer.Mix_FreeMusic(g_music)
    g_music = None

    sdl2.SDL_DestroyRenderer(g_renderer)
    g_renderer = None
    sdl2.SDL_DestroyWindow(g_window)
    g_window = None

    sdl2.sdlmixer.Mix_Quit()
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

            keys = [
                sdl2.SDLK_a,
                sdl2.SDLK_s,
                sdl2.SDLK_d,
                sdl2.SDLK_f,
                sdl2.SDLK_g,
            ]
            while not quit:
                while sdl2.SDL_PollEvent(ctypes.byref(e)) != 0:
                    if e.type == sdl2.SDL_QUIT:
                        quit = True
                    elif e.type == sdl2.SDL_KEYDOWN:
                        if e.key.keysym.sym == sdl2.SDLK_q:
                            sdl2.sdlmixer.Mix_PlayMusic(g_music, -1)
                        elif e.key.keysym.sym == sdl2.SDLK_w:
                            if sdl2.sdlmixer.Mix_PausedMusic():
                                sdl2.sdlmixer.Mix_ResumeMusic()
                            else:
                                sdl2.sdlmixer.Mix_PauseMusic()
                        elif e.key.keysym.sym == sdl2.SDLK_e:
                            sdl2.sdlmixer.Mix_HaltMusic()
                        elif e.key.keysym.sym in keys:
                            ix = keys.index(e.key.keysym.sym)
                            sdl2.sdlmixer.Mix_PlayChannel(-1, g_note[ix], 0)
                    
                sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
                sdl2.SDL_RenderClear(g_renderer)
                g_texture.render(0, 0)
                sdl2.SDL_RenderPresent(g_renderer)

    close()
    return 0

if __name__ == '__main__':
    sys.exit(main())

