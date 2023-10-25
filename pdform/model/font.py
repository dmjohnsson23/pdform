from .base import Wrapper
from pdfrw import *
from enum import IntFlag, Enum
from pdfrw.objects.pdfname import BasePdfName
from typing import Union, List

class FontFlags(IntFlag):
    """
    See 9.8.2: Font Descriptor Flags
    """
    # Note: spec numbers bits starting with 1, so indexes below are off-by-one
    # Table 123 – Font Flags
    FixedPitch = 1 << 0
    Serif = 1 << 1
    Symbolic = 1 << 2
    Script = 1 << 3
    Nonsymbolic = 1 << 5
    Italic = 1 << 6
    AllCap = 1 << 16
    SmallCap = 1 << 17
    ForceBold = 1 << 18

class FontType(BasePdfName, Enum):
    Type0='Type0'
    Type1='Type1'
    MMType1='MMType1'
    Type3='Type3'
    TrueType='TrueType'
    CIDFontType0='CIDFontType0'
    CIDFontType2='CIDFontType2'

class Font(Wrapper):
    """
    * 9.6: Simple Fonts
    * 9.8: Font Descriptors
    """
    raw:PdfDict

    def __init__(self, pdf, raw, name) -> None:
        self.name = name
        super().__init__()

    @property
    def glyph_space_ratio(self):
        """
        The unit ratio when converting between text space coordinates and glyph space coordinates.

        See 9.2.4: Glyph Positioning and Metrics
        """
        if self.raw.Subtype == FontType.Type3:
            raise NotImplementedError('Type 3 fonts not yet supported') # TODO
        else:
            return 1000

    @property
    def leading(self)->Union[int,float]:
        return self.raw.FontDescriptor.Leading or 0
    @leading.setter
    def leading(self, value:Union[int,float]):
        self.raw.FontDescriptor.Leading = value

    def get_char_width(self, char:str, scale=None)->Union[float,int]:
        """
        Get the width of the character.

        :param char: The character to check
        :param scale: If `None` or `False`, return the width unscaled in the glyph's coordinate 
            system. If `True`, return the width as a ratio of `glyph_space_ratio`. If a number,
            this should be the target font size, and the width will be returned relative to this 
            size.
        """
        char_code = ord(char) - int(self.raw.FirstChar)
        if len(self.raw.Widths) > char_code:
            width = float(self.raw.Widths[char_code])
        elif PdfName('MissingWidth') in self.raw.FontDescriptor:
            width = float(self.raw.FontDescriptor.MissingWidth)
        # TODO These remaining fallback I'm not 100% sure are in the right order...or that they should be here at all. Could also use FontBBox
        elif PdfName('AvgWidth') in self.raw.FontDescriptor:
            width = float(self.raw.FontDescriptor.AvgWidth)
        elif PdfName('MaxWidth') in self.raw.FontDescriptor:
            width = float(self.raw.FontDescriptor.MaxWidth)
        else:
            width = 0
        if scale is None or scale is False:
            return width
        # Scale based one the nominal height (see 9.2.2)
        # "This standard is arranged so that the nominal height of tightly spaced lines of text is
        # 1 unit. In the default user coordinate system, this means the standard glyph size is 1 
        # unit in user space, or 1 ⁄ 72 inch."
        width = width / self.glyph_space_ratio
        if scale is True:
            return width
        return width * scale
    
    def get_string_width(self, string:str, scale=None, char_spacing=0, word_spacing=0)->Union[float,int]:
        """
        Get the width of the string.

        :param char: The string to check
        :param scale: If `None` or `False`, return the width unscaled in the glyph's coordinate 
            system. If `True`, return the width as a ratio of `glyph_space_ratio`. If a number,
            this should be the target font size, and the width will be returned relative to this 
            size.
        :param char_spacing: The optional spacing to add after each non-space character
        :param char_spacing: The optional spacing to add after a space ' ' character
        """
        width = 0
        for char in string:
            width += self.get_char_width(char, scale) + (word_spacing if char == ' ' else char_spacing)
        return width
    
    def word_wrap(self, string:str, width, scale=None, char_spacing=0, word_spacing=0)->List[List[str]]:
        """
        Split a string into paragraphs, and each paragraph into lines that will fit in the given 
        width.

        Will not break words; if a word is too long for the line, it will exist on a line by itself.

        :param string: The string to split
        :param width: The maximum allowed line length
        :param scale: The scale factor to apply when calculating the widths (This is the font size)
        :param char_spacing: The width, in scaled font units, between each glyph. (See 9.3.2: 
            Character Spacing)
        :param word_spacing: The width, in scale font units, between each word. This will be 
            additional spacing between words, in addition to the width of the ' ' (ASCII space) 
            character. (See 9.3.3: Word Spacing)
        """
        # We'll define word spacing more liberally here as the actual value to add for each space
        word_spacing += self.get_char_width(' ', scale)
        paragraphs = []
        for line in string.splitlines():
            lines = []
            current_width = 0
            current_line = []
            for word in line.split():
                # Don't pass word spacing to `get_string_width`; we've redefined what word spacing 
                # means above, and there are no spaces in the string anyway
                word_len = self.get_string_width(word, scale, char_spacing)
                # Wrap if too long
                if current_width + word_len > width:
                    lines.append(' '.join(current_line))
                    current_width = 0
                    current_line = []
                current_line.append(word)
                current_width += word_len + word_spacing
            # Append last line
            if current_line:
                lines.append(' '.join(current_line))
            paragraphs.append(lines)
        return paragraphs



