from ..model.rect import Rect
from ..model.font import Font
from ..model.content_stream import ContentStream
from pdfrw import PdfString

def layout_text_line(pdf, text, rect:Rect, font:Font, font_scale=1, include_set_font=True, include_set_spacing=True, include_clip_rect=True, padding=0, char_spacing=0, word_spacing=0):
    """
    Emit a ContentStream containing the relevant commands to render the provided string. This is 
    for single-line text only, see also `layout_text_multiline`.

    See:
    * 9.2.2: Basics of Showing Text
    * 9.2.4: Glyph Positioning and Metrics

    :param text: The text to render
    :param rect: The area in which to render the text
    :param font: The font in which the text will be rendered
    :param include_clip_rect: If True, a `clip` operation will be included in the output stream, 
        clipping to the bounds of `rect`
    :param include_set_font: If True, a `set_font` operation will be included in the output stream
    :param include_set_spacing: If True, a `set_word_spacing` operation and `set_character_spacing` 
        will be included in the output stream, if the corresponding parameters are not 0.
    :param padding:
    :param char_spacing: The width, in scaled font units, between each glyph. (See 9.3.2: Character
        Spacing)
    :param word_spacing: The width, in scale font units, between each word. This will be additional
        spacing between words, in addition to the width of the ' ' (ASCII space) character. (See 
        9.3.3: Word Spacing)
    """
    if isinstance(padding, tuple) and len(padding) == 2:
        pad_x, pad_y = padding
    else:
        pad_x = pad_y = padding
    stream = ContentStream()
    if include_clip_rect:
        stream.append_rectangle(rect.left, rect.bottom, rect.width, rect.height)
        stream.clip()
    if include_set_font:
        stream.set_font(font.name, font_scale)
    if include_set_spacing:
        if word_spacing != 0:
            stream.set_word_spacing(word_spacing)
        if char_spacing != 0:
            stream.set_character_spacing(char_spacing)
    # Position the cursor for the first line
    stream.move_text(rect.left + pad_x, rect.top - pad_y - font_scale)
    stream.paint_text(PdfString.from_unicode(text))
    return stream


def layout_text_multiline(pdf, text, rect:Rect, font:Font, font_scale=1, include_set_font=True, include_set_spacing=True, include_clip_rect=True, padding=0, char_spacing=0, word_spacing=0, leading=None, paragraph_spacing=1):
    """
    Emit a ContentStream containing the relevant commands to render the provided string. This is 
    for multi-line text, see also `layout_text_line`.

    See:
    * 9.2.2: Basics of Showing Text
    * 9.2.4: Glyph Positioning and Metrics

    :param text: The text to render
    :param rect: The area in which to render the text
    :param font: The font in which the text will be rendered
    :param include_clip_rect: If True, a `clip` operation will be included in the output stream, 
        clipping to the bounds of `rect`
    :param include_set_font: If True, a `set_font` operation will be included in the output stream
    :param include_set_spacing: If True, a `set_word_spacing` operation and `set_character_spacing` 
        will be included in the output stream, if the corresponding parameters are not 0.
    :param padding:
    :param char_spacing: The width, in scaled font units, between each glyph. (See 9.3.2: Character
        Spacing)
    :param word_spacing: The width, in scale font units, between each word. This will be additional
        spacing between words, in addition to the width of the ' ' (ASCII space) character. (See 
        9.3.3: Word Spacing)
    :param leading: The space between lines. The default value from the font will be used if 
        nothing is provided. (See 9.3.5: Leading)
    :param paragraph_spacing: The space to insert between paragraphs, measured in lines. May be a
        fractional value, e.g. 1.5 lines
    """
    if isinstance(padding, tuple) and len(padding) == 2:
        pad_x, pad_y = padding
    else:
        pad_x = pad_y = padding
    if leading is None:
        leading = font.leading
    paragraphs = font.word_wrap(text, rect.width - pad_x * 2, font_scale, char_spacing=char_spacing, word_spacing=word_spacing)
    stream = ContentStream()
    if include_clip_rect:
        stream.append_rectangle(rect.left, rect.bottom, rect.width, rect.height)
        stream.clip()
    if include_set_font:
        stream.set_font(font.name, font_scale)
    if include_set_spacing:
        if word_spacing != 0:
            stream.set_word_spacing(word_spacing)
        if char_spacing != 0:
            stream.set_character_spacing(char_spacing)
    # Position the cursor for the first line
    stream.move_text(rect.left + pad_x, rect.top - pad_y - font_scale)
    for paragraph in paragraphs:
        for line in paragraph:
            stream.paint_text(PdfString.from_unicode(line))
            # Position the cursor at the start of the next line (offset from previous line)
            # (I think we could use move_text_new_line or paint_text_line to simplify)
            stream.move_text(0, -leading - font_scale)
        # Replace line space with paragraph space
        stream.undo()
        stream.move_text(0, (-leading - font_scale) * paragraph_spacing) 
    # Remove unnecessary final paragraph space
    stream.undo()
    return stream