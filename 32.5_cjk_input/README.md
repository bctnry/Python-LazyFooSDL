# README for 32.5 CJK Input

The original turtorial does not mention handling CJK (or any kind of text outside the range of ISO 8859 characters), but depending on what your goal is, this can be an issue. This turtorial is intended as a complement for that.

The font used here is called "Cubic 11", which can be found here:

https://github.com/ACh-K/Cubic-11

You can replace it with other fonts that support CJK (e.g. GNU Unifont).

NOTE THAT the code here will be mostly (if not all) in Python. Different from C/C++, Python differentiates strings (simply called "string"s in Python) and byte sequences (called "bytestring"s in Python), so you have to consider that as well if you're doing this in those languages.

## Rendering Unicode text

The original code of `LTexture::loadFromRenderedText` uses `TTF_RenderText_Solid`. Replace it with `TTF_RenderUTF8_Solid`. There are also `TTF_RenderUNICODE_*` functions, but it's UCS-2 (which means more hassle to use).

## Caret for text input

Let's extend the original turtorial code for text input a little further by adding a caret. You have to use a better data structure like gap buffer or piece table if you want to write a full-fledged text input component, but for this example we'll go with the simplest way.

``` python
# ...
g_window = None
g_renderer = None
g_font = None
g_prompt = LTexture()
g_text_piece1 = LTexture()
g_text_piece2 = LTexture()
# ...

    # ...
    text = ''
    text_caret = 0
    # ...
    while sdl2.SDL_PollEvent(ctypes.byref(e)) != 0:
        #...
        elif e.type == sdl2.SDL_TEXTINPUT:
            if not ((sdl2.SDL_GetModState()&sdl2.KMOD_CTRL)
                        and (e.text.text[0] in [ord('c'), ord('C'), ord('v'), ord('V')])):
                old_piece1 = text[:text_caret]; old_piece2 = text[text_caret:]
                text = old_piece1+e.text.text.decode()+old_piece2
                text_caret = len(old_piece1) + len(e.text.text.decode())
                should_render_text = True
        elif e.type == sdl2.SDL_KEYDOWN:
            # NOTE: because we render the text in two different pieces
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
            # ...
    # ...
    if should_render_text:
        piece1 = text[:text_caret]; piece2 = text[text_caret:]
        g_text_piece1.load_from_rendered_text(piece1 or ' ', color)
        g_text_piece2.load_from_rendered_text(piece2 or ' ', color)
        
    g_prompt.render(
        (SCREEN_WIDTH - g_prompt.get_width())//2,
        0,
    )
    total_width = g_text_piece1.get_width() + g_text_piece2.get_width()

    # render g_text_piece1
    g_text_piece1.render(
        (SCREEN_WIDTH - total_width)//2,
        (SCREEN_HEIGHT - g_text_piece1.get_height())//2,
    )

    # render text caret by putting it at the end of g_text_piece1.
    sdl2.SDL_SetRenderDrawColor(g_renderer, 0, 0, 0, 0xff)
    sdl2.SDL_RenderDrawLine(
        g_renderer,
        (SCREEN_WIDTH - total_width)//2+g_text_piece1.get_width(),
        (SCREEN_HEIGHT - g_text_piece1.get_height())//2,
        (SCREEN_WIDTH - total_width)//2+g_text_piece1.get_width(),
        (SCREEN_HEIGHT - g_text_piece1.get_height())//2+g_text_piece1.get_height(),
    )

    # render g_text_piece2
    g_text_piece2.render(
        (SCREEN_WIDTH - total_width)//2+g_text_piece1.get_width(),
        (SCREEN_HEIGHT - g_text_piece1.get_height())//2,
    )
    # ...
```

The full code could be found at `main_text_caret_only.py`. We could add more features like Shift-select and mouse events and all that stuff, but for the \*actual\* use case we're having this is good enough.

## Handling CJK input

### Setting hints

You need to set `SDL_HINT_IME_SHOW_UI` to 1 so that the candidate list of the IME will show up. In Python with pysdl2 it's done like this:

``` python
    # ...
    if not sdl2.SDL_SetHint(sdl2.SDL_HINT_IME_SHOW_UI, b'1'):
        print(f'Failed to set hint SDL_HINT_IME_SHOW_UI')
    # ...
```

### The overall workflow

From the SDL wiki <https://wiki.libsdl.org/Tutorials-TextInput#workflow>:

> 1.  The user activates an input method (IME). This is typically done via a hotkey or by selecting an input method in a GUI.
> 2.  The user begins to type in their selected language, starting a Composition.
> 3.  The user continues typing until the composition is satisfactory.
> 4.  Alternatively, the user may choose to open the Candidate List and select a Candidate. The IME can also force the Candidate List to open.
> 5.  The user commits the Composition, terminating it. The IME passes the text onto the application.

What actually happens in the process goes as follows:

1.  (Step 1) User activates IME. Nothing happened yet, no input, no candidate list.
2.  (Step 2~3) User types on the keyboard. **This gives the `SDL_TextEditingEvent`**. The program is responsible to (1) manage the Composition and (2) render the composition as the user is typing.
3.  (Step 4~5) User selects a candidate or simply commits the typed text. **This gives the `SDL_TextInputEvent`**.

So we can have the actual workflow:

1.  User may or may not input texts before activating the IME. 
2.  User activates the IME. We need to put the IME candidate list at the position of the caret.
3.  User starts a composition, which produces `SDL_TextEditingEvent`. This works like a new text input field and needs an additional caret.
4.  User complete the composition, which produces `SDL_TextInputEvent`.

``` python
    quit = False
    e = sdl2.SDL_Event()
    color = sdl2.SDL_Color(r=0,g=0,b=0,a=0xff)
    
    text = ''
    text_caret = 0
    composition = ''         # NEW
    composition_caret = 0    # NEW
    while not quit:
        should_render_text = False
        should_render_composition = False    # NEW
        while sdl2.SDL_PollEvent(ctypes.byref(e)) != 0:
            composition_mode = len(composition) > 0    # NEW
```

### Rendering the whole sequence

We divide the text with the text caret into `L_TEXT` and `R_TEXT` and the composition with the composition caret into `L_COMP` and `R_COMP`; then the display order is: `L_TEXT`, `L_COMP`, caret, `R_COMP`, `R_TEXT`. `L_COMP` and `R_COMP` are often rendered with an underline.

``` python
# ...
    # ...
    sdl2.SDL_SetRenderDrawColor(g_renderer, 0xff, 0xff, 0xff, 0xff)
    sdl2.SDL_RenderClear(g_renderer)

    if should_render_text:
        text_piece1 = text[:text_caret]
        text_piece2 = text[text_caret:]
        g_text_piece1.load_from_rendered_text(text_piece1 or ' ', color)
        g_text_piece2.load_from_rendered_text(text_piece2 or ' ', color)

    # NOTE: we force the size of the texture for composition text to 0 or else the space
    # around the caret would be too big. in a language like C you'll probably want to do
    # this very differently.
    if should_render_composition:
        composition_piece1 = composition[:composition_caret]
        composition_piece2 = composition[composition_caret:]
        g_composition_piece1.load_from_rendered_text(composition_piece1 or ' ', color)
        g_composition_piece2.load_from_rendered_text(composition_piece2 or ' ', color)
        if not composition_piece1: g_composition_piece1.force_size(0, 0)
        if not composition_piece2: g_composition_piece2.force_size(0, 0)
        
    g_prompt.render(
        (SCREEN_WIDTH - g_prompt.get_width())//2,
        0,
    )
    total_width = (
        g_text_piece1.get_width()
        + g_composition_piece1.get_width()
        + g_composition_piece2.get_width()
        + g_text_piece2.get_width()
    )
    starting_x = (SCREEN_WIDTH - total_width)//2
    starting_y = (SCREEN_HEIGHT - g_text_piece1.get_height())//2
    underline_y = max(
        starting_y + g_text_piece1.get_height(),
        starting_y + g_composition_piece1.get_height()
    )

    # rendering L_TEXT
    g_text_piece1.render(starting_x, starting_y)

    # rendering L_COMP
    g_composition_piece1.render(
        starting_x+g_text_piece1.get_width(),
        starting_y
    )

    # rendering caret
    sdl2.SDL_SetRenderDrawColor(g_renderer, 0, 0, 0, 0xff)
    sdl2.SDL_RenderDrawLine(
        g_renderer,
        starting_x + g_text_piece1.get_width() + g_composition_piece1.get_width(),
        starting_y,
        starting_x + g_text_piece1.get_width() + g_composition_piece1.get_width(),
        underline_y,
    )

    # rendering the underline, if any is needed
    if composition_mode:
        sdl2.SDL_RenderDrawLine(
            g_renderer,
            starting_x + g_text_piece1.get_width(),
            underline_y,
            starting_x + g_text_piece1.get_width() + g_composition_piece1.get_width() + g_composition_piece2.get_width(),
            underline_y,
        )

    # rendering R_COMP
    g_composition_piece2.render(
        starting_x+g_text_piece1.get_width()+g_composition_piece1.get_width(),
        starting_y
    )

    # rendering R_TEXT
    g_text_piece2.render(
        starting_x+g_text_piece1.get_width()+g_composition_piece1.get_width()+g_composition_piece2.get_width(),
        starting_y
    )
```

The `force_size` method call is added to the class `LTexture` as follows:

``` python
    def force_size(self, new_width=None, new_height=None):
        if new_width is not None: self._width = new_width
        if new_height is not None: self._height = new_height
```

### Setting position for candidate list

Without anything else, setting `SDL_HINT_IME_SHOW_UI` will only shows the candidate list at some "default" location (on my Windows 10 laptop it's the bottom right corner).

``` python
    # ...
    if composition:
        candidate_list_ui_location.x = (SCREEN_WIDTH - total_width)//2+g_text_piece1.get_width()
        candidate_list_ui_location.y = starting_x + g_text_piece1.get_width()
        sdl2.SDL_SetTextInputRect(candidate_list_ui_location)
```

### Handling `SDL_TextEditingEvent`

Taking Microsoft Pinyin as an example. Assume we now want to input "你好世界" ("Hello world in Chinese"), the pinyin (without tone markers) for this is "nihaoshijie", and Microsoft Pinyin will divide this string into "ni", "hao", "shi" and "jie" separated with `'`. This is reflected in the event data. If we have code like this:

``` python
    # ...
    elif e.type == sdl2.SDL_TEXTEDITING:
        print('editing', e.edit.text, e.edit.start, e.edit.length)
    # ...
```

We'll have console output like this:

```
editing b'' 0 0
editing b'n' 1 0
editing b'ni' 2 0
editing b"ni'h" 4 0    # NOTE THAT `e.edit.start` went from 2 to 4
editing b"ni'ha" 5 0
editing b"ni'hao" 6 0
editing b"ni'hao's" 8 0
editing b"ni'hao'sh" 9 0
editing b"ni'hao'shi" 10 0
editing b"ni'hao'shi'j" 12 0
editing b"ni'hao'shi'ji" 13 0
editing b"ni'hao'shi'jie" 14 0
```

From this we conclude `e.edit.start` is where we should render the caret. So we have:

``` python
    # ...
    elif e.type == sdl2.SDL_TEXT_EDITING:
        composition = e.edit.text.decode()
        composition_caret = e.edit.start
        should_render_composition = True
    # ...
```

Sometimes the composition the IME allowed will be longer than the data the event contains. In this case you basically can't do anything about this from your perspective.

### Handling `SDL_TextInputEvent`

We should clear composition here no matter what, because when this event is polled it means the composition is done or stopped prematurely.

``` python
    # ...
    elif e.type == sdl2.SDL_TEXTINPUT:
        # ...
            should_render_text = True

            composition = ''    # NEW
            composition_caret = 0    # NEW
            should_render_composition = True    # NEW
```

We should also do the same when CTRL+v is handled:

``` python
    # ...
    elif e.key.keysym.sym == sdl2.SDLK_v and (sdl2.SDL_GetModState()&sdl2.KMOD_CTRL):
        text = sdl2.SDL_GetClipboardText().decode()
        text_caret = len(text)
        should_render_text = True
        composition = ''
        composition_caret = 0
        should_render_composition = True
```

### Handling arrow keys and backspaces

Arrow key presses and backspaces are actually handled by the IME as well, we only need to re-render the composition text - the actual caret moving will be reflected back to the SDL application in the form of `SDL_TextEditingEvent`, where it'll handle with the usual procedure.

``` python
    # ...
    elif e.type == sdl2.SDL_KEYDOWN:
        # NOTE: IME sometimes don't interpret SDLK_UP and SDLK_DOWN as Home and End
        # so we don't assume anything here.
        if e.key.keysym.sym == sdl2.SDLK_UP:
            if not composition_mode:
                text_caret = 0
                should_render_text = True
        elif e.key.keysym.sym == sdl2.SDLK_DOWN:
            if not composition_mode:
                text_caret = len(text)
                should_render_text = True
        elif e.key.keysym.sym == sdl2.SDLK_LEFT:
            if composition_mode:
                should_render_composition = True
            elif text_caret > 0:
                text_caret -= 1
                should_render_text = True
        elif e.key.keysym.sym == sdl2.SDLK_RIGHT:
            if composition_mode:
                should_render_composition = True
            elif text_caret < len(text):
                text_caret += 1
                should_render_text = True
        elif e.key.keysym.sym == sdl2.SDLK_BACKSPACE and len(text) > 0:
            if composition_mode:
                should_render_composition = True
            else:
                if text_caret > 0:
                    text = text[:text_caret-1]+text[text_caret:]
                    text_caret -= 1
                    should_render_text = True
```



