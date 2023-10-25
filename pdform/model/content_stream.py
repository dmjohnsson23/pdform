from __future__ import annotations
from typing import Union,List
from pdfrw import PdfArray,PdfDict,PdfName,PdfString
from pdfrw.objects.pdfname import BasePdfName
from enum import Enum,IntEnum
from dataclasses import dataclass


class Operator(str, Enum): # We can just use StrEnum in Python 3.11
    """
    Enumeration of all possible graphics operations used in PDF content streams. See 8.2 and 9.4.

    Operators are callable, and doing so will return an operation. Thus, all the following are 
    equivalent::

        Operation(Operator.move, x, y)
        Operator.move(x, y)
        Operator('m')(x, y)
        Operation(Operator('m'), x, y)
    """
    # General graphics state (Table 57)
    set_line_width='w'
    set_line_cap='J'
    set_line_join='j'
    set_miter_limit='M'
    set_dash_pattern='d'
    set_intent='ri'
    set_flatness='i'
    use_dict_params='gs'
    # Special graphics state (Table 57)
    push_stack='q'
    pop_stack='Q'
    set_transform_matrix='cm',
    # Path construction (Table 59)
    move='m',
    append_line='l',
    append_cubic_bezier='c',
    append_cubic_bezier_initial='v',
    append_cubic_bezier_final='y',
    append_closing_line='h'
    append_rectangle='re',
    # Path painting (Table 60)
    stroke='S'
    close_and_stroke='s'
    fill='f'
    fill_compat='F' # Not actually used, legacy alias of ``fill``
    fill_even_odd='f*'
    fill_and_stroke='B'
    fill_and_stroke_even_odd='B*'
    close_fill_and_stroke='b'
    close_fill_and_stroke_even_odd='b*'
    end_path='n'
    # Clipping paths (Table 61)
    clip='W'
    clip_even_odd='W*'
    # Text objects (Table 107)
    begin_text='BT'
    end_text='ET' 
    # Text state (Table 105)
    set_character_spacing='Tc'
    set_word_spacing='Tw'
    set_text_scaling_h='Tz'
    set_text_leading='TL'
    set_font='Tf'
    set_text_render_mode='Tr'
    set_text_rise='Ts'
    # Text positioning (Table 108)
    move_text='Td'
    move_text_set_leading='TD'
    set_text_matrix='Tm'
    move_text_new_line='T*' 
    # Text showing (Table 109)
    paint_text='Tj'
    paint_text_line="'"
    paint_text_line_with_spacing='"'
    paint_text_per_glyph='TJ'
    # Type 3 fonts (Table 113)
    # TODO: d0, d1 
    # Color (Table 74)
    set_stroke_color_space='CS'
    set_nonstroke_color_space='cs'
    set_stroke_color='SC'
    set_stroke_color_name='SCN'
    set_nonstroke_color='sc'
    set_nonstroke_color_name='scn'
    set_stroke_color_gray='G'
    set_nonstroke_color_gray='g'
    set_stroke_color_rgb='RG',
    set_nonstroke_color_rgb='rg',
    set_stroke_color_cymk='K',
    set_nonstroke_color_cymk='k',
    # Shading patterns (Table 77)
    paint_shading='sh' 
    # Inline images (Table 92)
    begin_image='BI'
    image_data='ID'
    end_image='EI' 
    # XObjects (Table 87)
    paint_xobject='Do' 
    # Marked content (Table 320)
    mark_point='MP'
    mark_point_with_properties='DP'
    begin_marked_content='BMC'
    begin_marked_content_properties='BDC'
    end_marked_content='EMC'
    # Compatibility (Table 32)
    begin_compatibility='BX'
    end_compatibility='EX' 

    def __call__(self, *operands):
        return Operation(self, operands)
    
    def __str__(self):
        return self.value

class TextRenderMode(IntEnum):
    """
    See 9.3.6 "Text Rendering Mode"
    """
    fill=0
    stroke=1
    fill_and_stroke=2
    invisible=3
    fill_and_clip=4
    stroke_and_clip=5
    fill_stroke_and_clip=6
    clip=7


@dataclass
class Operation:
    """
    Represents a operation in a PDF content stream. See 8.2 and 9.4.
    """
    operator:Operator
    operands:List[Union[PdfArray,PdfDict,PdfName,PdfString,int,float]]

    def __str__(self):
        if not self.operands:
            return str(self.operator)
        else:
            # TODO properly convert PdfArray and PdfDict to string
            return f"{' '.join(map(str, self.operands))} {self.operator}"

class ContentStream:
    """
    Represents a PDF content stream, such as is used to render text or graphics.

    Currently, this is only intended for creating new content streams; no functionality exists to
    read or modify streams.

    Relevant spec sections:
    
    * 7.8: Content Streams and Resources
    * 8.2: Graphics Objects
    * 8.4: Graphics State
    * 8.5: Path Construction and Painting

    There are numerous shortcut methods for appending various operations to the stream. All the 
    following lines are equivalent::

        stream.operation(Operator.move, x, y)
        stream.operation(Operator('m'), x, y)
        stream.operation('m', x, y)
        stream.append(Operator.move(x, y))
        stream.append(Operator('m')(x, y))
        stream.append(Operation(Operator.move, x, y))
        stream.append(Operation(Operator('m'), x, y))
        stream.append_raw(f"{x} {y} m")
        stream.move(x, y)
    """
    # Basically the same concept: https://doc.courtbouillon.org/pydyf/stable/api_reference.html#pydyf.Stream 
    # See also: https://github.com/Kozea/WeasyPrint/blob/main/weasyprint/pdf/stream.py
    def __init__(self, operations:List[Operation]=None):
        self._operations = operations or []

    def operation(self, operator:Union[str,Operator], *operands:Union[PdfArray,PdfDict,PdfName,PdfString,int,float]):
        # Table 51 (under 8.2) lists possible operations
        self._operations.append(Operator(operator)(operands))
        return self
    
    def extend(self, other:ContentStream):
        self._operations.extend(other._operations)
        return self
    
    def append(self, operation:Operation):
        """
        Append an operation to the stream
        """
        self._operations.append(operation)
        return self
    
    def append_raw(self, code:str):
        """
        Append raw code to the stream
        """
        # TODO we should parse this instead of cheating and using a string...
        self._operations.append(code)
        return self

    def undo(self):
        """
        Remove the most recent operation from the stream
        """
        return self._operations.pop()
    
    def __str__(self):
        return ' '.join(map(str, self._operations))
    # TODO PdfTokens could be used to split the string when parsing

    def set_line_width(self, width):
        """
        Set the line width in the graphics state (see 8.4.3.2, "Line Width").
        """
        self._operations.append(Operator.set_line_width(width))
        return self
    
    def set_line_cap(self, cap):
        """
        Set the line cap style in the graphics state (see 8.4.3.3, "Line Cap Style").
        """
        self._operations.append(Operator.set_line_cap(cap))
        return self
    
    def set_line_join(self, join):
        """
        Set the line join style in the graphics state (see 8.4.3.4, "Line Join Style").
        """
        self._operations.append(Operator.set_line_join(join))
        return self
    
    def set_miter_limit(self, limit):
        """
        Set the miter limit in the graphics state (see 8.4.3.5, "Miter Limit").
        """
        self._operations.append(Operator.set_miter_limit(limit))
        return self
    
    def set_dash_pattern(self, array, phase):
        """
        Set the line dash pattern in the graphics state (see 8.4.3.6, "Line Dash Pattern").
        """
        self._operations.append(Operator.set_dash_pattern(array, phase))
        return self
    
    def set_intent(self, intent):
        """
        Set the color rendering intent in the graphics state (see 8.6.5.8, "Rendering Intents").
        """
        self._operations.append(Operator.set_intent(intent))
        return self
    
    def set_flatness(self, flatness):
        """
        Set the flatness tolerance in the graphics state (see 10.6.2, "Flatness Tolerance"). 
        
        :param flatness: A number in the range 0 to 100. A value of 0 shall specify the output 
        device's default flatness tolerance.
        """
        self._operations.append(Operator.set_flatness(flatness))
        return self
    
    def use_dict_params(self, dict_name):
        """
        Set the specified parameters in the graphics state from a subdictionary of the current 
        resource dictionary.

        :param dictName: The name of a graphics state parameter dictionary in the ExtGState
            (see 8.4.5, "Graphics State Parameter Dictionaries").
        """
        self._operations.append(Operator.use_dict_params(dict_name) )
        return self
    
    def push_stack(self):
        """
        Save the current graphics state on the graphics state stack (see 8.4.2, "Graphics State 
        Stack").
        """
        self._operations.append(Operator.push_stack())
        return self
    
    def pop_stack(self):
        """
        Restore the graphics state by removing the most recently saved state from the stack and 
        making it the current state (see 8.4.2, "Graphics State Stack").
        """
        self._operations.append(Operator.pop_stack())
        return self
    
    def set_transform_matrix(self, a, b, c, d, e, f):
        """
        Modify the current transformation matrix (CTM) by concatenating the specified matrix (see 
        8.3.2, "Coordinate Spaces").
        """
        self._operations.append(Operator.set_transform_matrix(a, b, c, d, e, f))
        return self
    
    def move(self, x, y):
        """
        Begin a new subpath by moving the current point to coordinates (x, y), omitting any 
        connecting line segment. If the previous path construction operator in the current path
        was also a move operation, the new move overrides it; no vestige of the previous move 
        operation remains in the path.
        """
        self._operations.append(Operator.move(x, y))
        return self
    
    def append_line(self, x, y):
        """
        Append a straight line segment from the current point to the point (x, y). The new current 
        point shall be (x, y).
        """
        self._operations.append(Operator.append_line(x, y))
        return self
    
    def append_cubic_bezier(self, x1, y1, x2, y2, x3, y3):
        """
        Append a cubic Bézier curve to the current path. The curve shall extend from the current 
        point to the point (x3, y3), using (x1, y1) and (x2, y2) as the Bézier control points (see 
        8.5.2.2, "Cubic Bézier Curves"). The new current point shall be (x3, y3).
        """
        self._operations.append(Operator.append_cubic_bezier(x1, y1, x2, y2, x3, y3))
        return self
    
    def append_cubic_bezier_initial(self, x2, y2, x3, y3):
        """
        Append a cubic Bézier curve to the current path. The curve shall extend from the current 
        point to the point (x3, y3), using the current point and (x2 , y2 ) as the Bézier control 
        points (see 8.5.2.2, "Cubic Bézier Curves"). The new current point shall be (x3, y3).
        """
        self._operations.append(Operator.append_cubic_bezier_initial(x2, y2, x3, y3))
        return self
    
    def append_cubic_bezier_final(self, x1, y1, x3, y3):
        """
        Append a cubic Bézier curve to the current path. The curve shall extend from the current 
        point to the point (x3, y3), using (x1 , y1 ) and (x3 , y3 ) as the Bézier control points 
        (see 8.5.2.2, "Cubic Bézier Curves"). The new current point shall be (x3, y3).
        """
        self._operations.append(Operator.append_cubic_bezier_final(x1, y1, x3, y3))
        return self
    
    def append_closing_line(self):
        """
        Close the current subpath by appending a straight line segment from the current point to 
        the starting point of the subpath. If the current subpath is already closed,  do
        nothing. 
        
        This operator terminates the current subpath. Appending another segment to the current path 
        shall begin a new subpath, even if the new segment begins at the endpoint reached by this 
        operation.
        """
        self._operations.append(Operator.append_closing_line())
        return self
    
    def append_rectangle(self, x, y, width, height):
        """
        Append a rectangle to the current path as a complete subpath, with lower-left corner (x, y)
        and dimensions width and height in user space. 

        Example::

            # This call...
            stream.append_rectangle(x, y, width, height)
            # ...is equivalent to this series of calls
            stream.move(x, y)
            stream.append_line(x + width, y)
            stream.append_line(x + width, y + height)
            stream.append_line(x, y + height)
            stream.append_closing_line()
        """
        self._operations.append(Operator.append_rectangle(x, y, width, height))
        return self
    
    def stroke(self):
        """
        Stroke the path.
        """
        self._operations.append(Operator.stroke())
        return self
    
    def close_and_stroke(self):
        """
        Close and stroke the path.

        Example::

            # This call...
            stream.close_and_stroke()
            # ...is equivalent to this series of calls
            stream.append_closing_line()
            stream.stroke()
        """
        self._operations.append(Operator.close_and_stroke())
        return self
    
    def fill(self):
        """
        Fill the path, using the nonzero winding number rule to determine the region to fill (see
        8.5.3.3.2, "Nonzero Winding Number Rule"). Any subpaths that are open shall be implicitly
        closed before being filled.
        """
        self._operations.append(Operator.fill())
        return self
    
    def fill_even_odd(self):
        """
        Fill the path, using the even-odd rule to determine the region to fill (see 8.5.3.3.3, 
        "Even-Odd Rule").
        """
        self._operations.append(Operator.fill_even_odd())
        return self
    
    def fill_and_stroke(self):
        """
        Fill and then stroke the path, using the nonzero winding number rule to determine the 
        region to fill. This operator shall produce the same result as constructing two identical 
        path objects, painting the first with ``stream.fill()`` and the second with 
        ``stream.stroke()``.
        """
        self._operations.append(Operator.fill_and_stroke())
        return self
    
    def fill_and_stroke_even_odd(self):
        """
        Fill and then stroke the path, using the even-odd rule to determine the region to fill. 
        This operator shall produce the same result as ``stream.fill_and_stroke``, except that the
        path is filled as if with ``stream.fill_even_odd()`` instead of ``stream.fill()``. See also
        11.7.4.4, "Special Path-Painting Considerations".
        """
        self._operations.append(Operator.fill_and_stroke_even_odd())
        return self
    
    def close_fill_and_stroke(self):
        """
        Close, fill, and then stroke the path, using the nonzero winding number rule to determine 
        the region to fill.

        Example::

            # This call...
            stream.close_fill_and_stroke()
            # ...is equivalent to this series of calls
            stream.append_closing_line()
            stream.fill_and_stroke()
        
        See also 11.7.4.4, "Special Path-Painting Considerations".
        """
        self._operations.append(Operator.close_fill_and_stroke())
        return self
    
    def close_fill_and_stroke_even_odd(self):
        """
        Close, fill, and then stroke the path, using the even-odd rule to determine the region to 
        fill.

        Example::

            # This call...
            stream.close_fill_and_stroke_even_odd()
            # ...is equivalent to this series of calls
            stream.append_closing_line()
            stream.fill_and_stroke_even_odd()
        
        See also 11.7.4.4, "Special Path-Painting Considerations".
        """
        self._operations.append(Operator.close_fill_and_stroke_even_odd())
        return self
    
    def end_path(self):
        """
        End the path object without filling or stroking it. This operator shall be a path-painting 
        no-op, used primarily for the side effect of changing the current clipping path (see 8.5.4,
        "Clipping Path Operators").
        """
        self._operations.append(Operator.end_path())
        return self

    def clip(self):
        """
        Modify the current clipping path by intersecting it with the current path, using the 
        nonzero winding number rule to determine which regions lie inside the clipping path.
        """
        self._operations.append(Operator.clip())
        return self
    
    def clip_even_odd(self):
        """
        Modify the current clipping path by intersecting it with the current path, using the 
        even-odd rule to determine which regions lie inside the clipping path.
        """
        self._operations.append(Operator.clip_even_odd())
        return self

    def begin_text(self):
        """
        Begin a text object, initializing the text matrix, ``Tm``, and the text line matrix, ``Tlm``,
        to the identity matrix. Text objects shall not be nested; a second ``begin_text()`` shall
        not appear before an ``end_text()``.
        """
        self._operations.append(Operator.begin_text())
        return self

    def end_text(self):
        """
        End a text object, discarding the text matrix.
        """
        self._operations.append(Operator.end_text())
        return self

    def set_character_spacing(self, char_space:Union[int,float]):
        """
        Set the character spacing. Character spacing shall be used by the ``paint_text``, 
        ``paint_text_line``, ``paint_text_per_glyph`` operators. Initial value: 0.
        
        :param char_space: A number expressed in unscaled text space units. 
        """
        self._operations.append(Operator.set_character_spacing(char_space))
        return self

    def set_word_spacing(self, word_space:Union[int,float]):
        """
        Set the word spacing. Word spacing shall be used by the ``paint_text``, ``paint_text_line``,
        ``paint_text_per_glyph`` operators. Initial value: 0.
        
        :param word_space: A number expressed in unscaled text space units. 
        """
        self._operations.append(Operator.set_word_spacing(word_space))
        return self

    def set_text_scaling_h(self, scale:Union[int,float]):
        """
        Set the horizontal scaling to :math:`scale / 100`. Initial value: 100 (normal width).
        
        :param scale: A number specifying the percentage of the normal width. 
        """
        self._operations.append(Operator.set_text_scaling_h(scale))
        return self

    def set_text_leading(self, leading:Union[int,float]):
        """
        Set the text leading value. Text leading shall be used only by the ``move_text_new_line``,
        ``paint_text_line``, and ``paint_text_line_with_spacing`` operators. Initial value: 0.
         
        :param leading: A number expressed in unscaled text space units. 
        """
        self._operations.append(Operator.set_text_leading(leading))
        return self

    def set_font(self, font:BasePdfName, size:Union[int,float]):
        """
        Set the text font and the text font size. There is no initial value for either font or size;
        they shall be specified explicitly before any text is shown.
         
        :param font: The name of a font resource in the Font subdictionary of the current resource 
            dictionary
        :param size: A number representing a scale factor.
        """
        self._operations.append(Operator.set_font(font, size))
        return self

    def set_text_render_mode(self, mode:Union[TextRenderMode,int]):
        """
        Set the text rendering mode. Initial value: ``TextRenderMode.fill`` (0).
        """
        self._operations.append(Operator.set_text_render_mode(mode))
        return self

    def set_text_rise(self, rise:Union[int,float]):
        """
        Set the text rise. Initial value: 0.
        
        :param rise: A number expressed in unscaled text space units.
        """
        self._operations.append(Operator.set_text_rise(rise))
        return self

    def move_text(self, tx:Union[int,float], ty:Union[int,float]):
        """
        Move to the start of the next line, offset from the start of the current line by (``tx``, 
        ``ty``). ``tx`` and ``ty`` shall denote numbers expressed in unscaled text space units.
        """
        self._operations.append(Operator.move_text(tx, ty))
        return self

    def move_text_set_leading(self, tx:Union[int,float], ty:Union[int,float]):
        """
        Move to the start of the next line, offset from the start of the current line by (``tx``, 
        ``ty``). As a side effect, this operator shall set the leading parameter in the text state.
        
        This operator shall have the same effect as this code::

            stream.set_text_leading(-ty)
            stream.move_text(tx, ty)
        """
        self._operations.append(Operator.move_text_set_leading(tx, ty))
        return self

    def set_text_matrix(self, a:Union[int,float], b:Union[int,float], c:Union[int,float], d:Union[int,float], e:Union[int,float], f:Union[int,float]):
        """
        Set the text matrix, ``Tm``, and the text line matrix, ``Tlm``:

        .. math::

            Tm = Tlm = \\begin{bmatrix}
            a b 0
            c d 0
            e f 1
            \\end{bmatrix}

        The operands shall all be numbers, and the initial value for ``Tm`` and ``Tlm`` shall be 
        the identity matrix, [ 1 0 0 1 0 0 ]. Although the operands specify a matrix, they shall be
        passed as six separate numbers, not as an array.
        
        The matrix specified by the operands shall not be concatenated onto the current text matrix, 
        but shall replace it.
        """
        self._operations.append(Operator.set_text_matrix(a, b, c, d, e, f))
        return self

    def move_text_new_line(self):
        """
        Move to the start of the next line. This operator has the same effect as the code::
            
            stream.move_text(0, -Tl)

        where ``Tl`` denotes the current leading parameter in the text state. The negative of ``Tl`` 
        is used here because Tl is the text leading expressed as a positive number. Going to the 
        next line entails decreasing the y coordinate.
        """
        self._operations.append(Operator.move_text_new_line())
        return self

    def paint_text(self, string:PdfString):
        """
        Show a text string.
        """
        self._operations.append(Operator.paint_text(string))
        return self

    def paint_text_line(self, string:PdfString):
        """
        Move to the next line and show a text string. This operator shall have the same effect as
        the code::

            stream.move_text_new_line()
            stream.pain_text(string)
        """
        self._operations.append(Operator.paint_text_line(string))
        return self

    def paint_text_line_with_spacing(self, word_space:Union[int,float], character_space:Union[int,float], string:PdfString):
        """
        Move to the next line and show a text string, using the given word spacing and character 
        spacing (setting the corresponding parameters in the text state). 
        
        :param word_space: A number expressed in unscaled text space units for the word spacing.
        :param character_space: A number expressed in unscaled text space units for the character 
            spacing.
         
        This operator shall have the same effect as this code::

            stream.set_word_spacing(word_space)
            stream.set_character_spacing(character_space)
            stream.paint_text_line(string)
        """
        self._operations.append(Operator.paint_text_line_with_spacing(word_space, character_space, string))
        return self

    def paint_text_per_glyph(self, array:PdfArray):
        """
        Show one or more text strings, allowing individual glyph positioning. Each element of array
        shall be either a string or a number. If the element is a string, this operator shall show 
        the string. If it is a number, the operator shall adjust the text position by that amount; 
        that is, it shall translate the text matrix. The number shall be expressed in thousandths 
        of a unit of text space (see 9.4.4, "Text Space Details"). This amount shall be subtracted 
        from the current horizontal or vertical coordinate, depending on the writing mode. In the 
        default coordinate system, a positive adjustment has the effect of moving the next glyph 
        painted either to the left or down by the given amount.
        """
        self._operations.append(Operator.paint_text_per_glyph(array))
        return self

    def set_stroke_color_space(self, name:BasePdfName):
        """
        Set the current color space to use for stroking operations. The operand name shall be a 
        name object. If the color space is one that can be specified by a name and no additional 
        parameters (DeviceGray, DeviceRGB, DeviceCMYK, and certain cases of Pattern), the name may
        be specified directly. Otherwise, it shall be a name defined in the ColorSpace 
        subdictionary of the current resource dictionary (see 7.8.3, "Resource Dictionaries"); the 
        associated value shall be an array describing the color space (see 8.6.3, "color Space 
        Families").

        The names DeviceGray, DeviceRGB, DeviceCMYK, and Pattern always identify the corresponding 
        color spaces directly; they never refer to resources in the ColorSpace subdictionary.

        This operator shall also set the current stroking color to its initial value, which depends
        on the color space:

        * In a DeviceGray, DeviceRGB, CalGray, or CalRGB color space, the initial color shall have 
          all components equal to 0.0.
        * In a DeviceCMYK color space, the initial color shall be [ 0.0 0.0 0.0 1.0 ].
        * In a Lab or ICCBased color space, the initial color shall have all components equal to 
          0.0 unless that falls outside the intervals specified by the space's Range entry, in 
          which case the nearest valid value shall be substituted.
        * In an Indexed color space, the initial color value shall be 0.
        * In a Separation or DeviceN color space, the initial tint value shall be 1.0 for all 
          colorants.
        * In a Pattern color space, the initial color shall be a pattern object that causes nothing
          to be painted
        """
        self._operations.append(Operator.set_stroke_color_space(name))
        return self

    def set_nonstroke_color_space(self, name:BasePdfName):
        """
        Set the current color space to use for non-stroking operations. The operand name shall be a 
        name object. If the color space is one that can be specified by a name and no additional 
        parameters (DeviceGray, DeviceRGB, DeviceCMYK, and certain cases of Pattern), the name may
        be specified directly. Otherwise, it shall be a name defined in the ColorSpace 
        subdictionary of the current resource dictionary (see 7.8.3, "Resource Dictionaries"); the 
        associated value shall be an array describing the color space (see 8.6.3, "color Space 
        Families").

        The names DeviceGray, DeviceRGB, DeviceCMYK, and Pattern always identify the corresponding 
        color spaces directly; they never refer to resources in the ColorSpace subdictionary.

        This operator shall also set the current non-stroking color to its initial value, which 
        depends on the color space:

        * In a DeviceGray, DeviceRGB, CalGray, or CalRGB color space, the initial color shall have 
          all components equal to 0.0.
        * In a DeviceCMYK color space, the initial color shall be [ 0.0 0.0 0.0 1.0 ].
        * In a Lab or ICCBased color space, the initial color shall have all components equal to 
          0.0 unless that falls outside the intervals specified by the space's Range entry, in 
          which case the nearest valid value shall be substituted.
        * In an Indexed color space, the initial color value shall be 0.
        * In a Separation or DeviceN color space, the initial tint value shall be 1.0 for all 
          colorants.
        * In a Pattern color space, the initial color shall be a pattern object that causes nothing
          to be painted
        """
        self._operations.append(Operator.set_nonstroke_color_space(name))
        return self

    def set_stroke_color(self, *operands):
        """
        Set the color to use for stroking operations in a device, CIE-based (other than ICCBased), 
        or Indexed color space. The number of operands required and their interpretation depends 
        on the current stroking color space:
        
        * For DeviceGray, CalGray, and Indexed color spaces, one operand shall be required (n = 1).
        * For DeviceRGB, CalRGB, and Lab color spaces, three operands shall be required (n = 3).
        * For DeviceCMYK, four operands shall be required (n = 4).
        """
        self._operations.append(Operator.set_stroke_color(*operands))
        return self

    def set_stroke_color_name(self, *operands):
        """
        Same as ``set_stroke_color`` but also supports Pattern, Separation, DeviceN and ICCBased 
        color spaces.

        * If the current stroking color space is a Separation, DeviceN, or ICCBased color space, 
          the operands ``c1``...``cn`` shall be numbers. The number of operands and their 
          interpretation depends on the color space.
        * If the current stroking color space is a Pattern color space, the final parameter, 
          ``name``, shall be the name of an entry in the Pattern subdictionary of the current 
          resource dictionary (see 7.8.3, "Resource Dictionaries"). For an uncolored tiling pattern 
          (PatternType = 1 and PaintType = 2), ``c1``..``cn`` shall be component values specifying
          a color in the pattern's underlying color space.
        * For other types of patterns, these operands shall not be
          specified.
        """
        self._operations.append(Operator.set_stroke_color_name(*operands))
        return self

    def set_nonstroke_color(self, *operands):
        """
        Set the color to use for non-stroking operations in a device, CIE-based (other than 
        ICCBased), or Indexed color space. The number of operands required and their interpretation 
        depends on the current stroking color space:
        
        * For DeviceGray, CalGray, and Indexed color spaces, one operand shall be required (n = 1).
        * For DeviceRGB, CalRGB, and Lab color spaces, three operands shall be required (n = 3).
        * For DeviceCMYK, four operands shall be required (n = 4).
        """
        self._operations.append(Operator.set_nonstroke_color(*operands))
        return self

    def set_nonstroke_color_name(self, *operands):
        """
        Same as ``set_nonstroke_color`` but also supports Pattern, Separation, DeviceN and ICCBased 
        color spaces.

        * If the current stroking color space is a Separation, DeviceN, or ICCBased color space, 
          the operands ``c1``...``cn`` shall be numbers. The number of operands and their 
          interpretation depends on the color space.
        * If the current stroking color space is a Pattern color space, the final parameter, 
          ``name``, shall be the name of an entry in the Pattern subdictionary of the current 
          resource dictionary (see 7.8.3, "Resource Dictionaries"). For an uncolored tiling pattern 
          (PatternType = 1 and PaintType = 2), ``c1``..``cn`` shall be component values specifying
          a color in the pattern's underlying color space.
        * For other types of patterns, these operands shall not be
          specified.
        """
        self._operations.append(Operator.set_nonstroke_color_name(*operands))
        return self

    def set_stroke_color_gray(self, gray:float):
        """
        Set the stroking color space to DeviceGray (or the DefaultGray color space; see 8.6.5.6,
        "Default color Spaces") and set the gray level to use for stroking operations. 
        
        :param gray: A number between 0.0 (black) and 1.0 (white).
        """
        self._operations.append(Operator.set_stroke_color_gray(gray))
        return self

    def set_nonstroke_color_gray(self, gray:float):
        """
        Set the non-stroking color space to DeviceGray (or the DefaultGray color space; see 8.6.5.6,
        "Default color Spaces") and set the gray level to use for non-stroking operations. 
        
        :param gray: A number between 0.0 (black) and 1.0 (white).
        """
        self._operations.append(Operator.set_nonstroke_color_gray(gray))
        return self

    def set_stroke_color_rgb(self, r:float, g:float, b:float):
        """
        Set the stroking color space to DeviceRGB (or the DefaultRGB color space; see 8.6.5.6, 
        "Default color Spaces") and set the color to use for stroking operations. Each operand 
        shall be a number between 0.0 (minimum intensity) and 1.0 (maximum intensity).
        """
        self._operations.append(Operator.set_stroke_color_rgb(r, g, b))
        return self

    def set_nonstroke_color_rgb(self, r:float, g:float, b:float):
        """
        Set the non-stroking color space to DeviceRGB (or the DefaultRGB color space; see 8.6.5.6, 
        "Default color Spaces") and set the color to use for non=stroking operations. Each operand 
        shall be a number between 0.0 (minimum intensity) and 1.0 (maximum intensity).
        """
        self._operations.append(Operator.set_nonstroke_color_rgb(r, g, b))
        return self

    def set_stroke_color_cymk(self, c:float, y:float, m:float, k:float):
        """
        Set the stroking color space to DeviceCMYK (or the DefaultCMYK color space; see 8.6.5.6, 
        "Default color Spaces") and set the color to use for stroking operations. 
        
        Each operand shall be a number between 0.0 (zero concentration) and 1.0 (maximum 
        concentration). The behavior of this operator is affected by the overprint mode (see 8.6.7, 
        "Overprint Control").
        """
        self._operations.append(Operator.set_stroke_color_cymk(c, y, m, k))
        return self

    def set_nonstroke_color_cymk(self, c:float, y:float, m:float, k:float):
        """
        Set the non-stroking color space to DeviceCMYK (or the DefaultCMYK color space; see 8.6.5.6,
         "Default color Spaces") and set the color to use for non-stroking operations. 
        
        Each operand shall be a number between 0.0 (zero concentration) and 1.0 (maximum 
        concentration). The behavior of this operator is affected by the overprint mode (see 8.6.7, 
        "Overprint Control").
        """
        self._operations.append(Operator.set_nonstroke_color_cymk(c, y, m, k))
        return self

    def paint_shading(self, name:BasePdfName):
        """
        Paint the shape and color shading described by a shading dictionary, subject to the current 
        clipping path. The current color in the graphics state is neither used nor altered. The 
        effect is different from that of painting a path using a shading pattern as the current 
        color.

        :param name: The name of a shading dictionary resource in the Shading subdictionary of the 
            current resource dictionary (see 7.8.3, "Resource Dictionaries"). All coordinates in 
            the shading dictionary are interpreted relative to the current user space. (By contrast, 
            when a shading dictionary is used in a type 2 pattern, the coordinates are expressed in 
            pattern space.) All colors are interpreted in the color space identified by the shading 
            dictionary's ColorSpace entry (see Table 78). The Background entry, if present, is 
            ignored.
            
        This operator should be applied only to bounded or geometrically defined shadings. If 
        applied to an unbounded shading, it paints the shading's gradient fill across the entire 
        clipping region, which may be time-consuming.

        """
        self._operations.append(Operator.paint_shading(name))
        return self

    def begin_image(self):
        """
        Begin an inline image object
        """
        self._operations.append(Operator.begin_image())
        return self

    def image_data(self): # TODO how does this work?
        """
        Begin the image data for an inline image object.
        """
        self._operations.append(Operator.image_data())
        return self

    def end_image(self):
        """
        End an inline image object.
        """
        self._operations.append(Operator.end_image())
        return self

    def paint_xobject(self, name:BasePdfName):
        """
        Paint the specified XObject. The operand name shall appear as a key in the XObject 
        subdictionary of the current resource dictionary (see 7.8.3, "Resource Dictionaries"). The
        associated value shall be a stream whose Type entry, if present, is XObject. The effect of
        this operation depends on the value of the XObject's Subtype entry, which may be Image (see 
        8.9.5, "Image Dictionaries"), Form (see 8.10, "Form XObjects"), or PS (see 8.8.2, 
        "PostScript XObjects").
        """
        self._operations.append(Operator.paint_xobject(name))
        return self

    def mark_point(self, tag:BasePdfName):
        """
        Designate a marked-content point. 
        
        :param tag: A name object indicating the role or significance of the point.
        """
        self._operations.append(Operator.mark_point(tag))
        return self

    def mark_point_with_properties(self, tag:BasePdfName, properties:Union[PdfDict,BasePdfName]):
        """
        Designate a marked-content point with an associated property list.
        
        :param tag: A name object indicating the role or significance of the point. 
        :param properties: Either an inline dictionary containing the property list or a name 
            object associated with it in the Properties subdictionary of the current resource 
            dictionary (see 14.6.2, “Property Lists”).
        """
        self._operations.append(Operator.mark_point_with_properties(tag, properties))
        return self

    def begin_marked_content(self, tag:BasePdfName):
        """
        Begin a marked-content sequence, which must be terminated by calling 
        ``stream.end_marked_content()``
        
        :param tag: A name object indicating the role or significance of the point. 
        """
        self._operations.append(Operator.begin_marked_content(tag))
        return self

    def begin_marked_content_properties(self, tag:BasePdfName, properties:Union[PdfDict,BasePdfName]):
        """
        Begin a marked-content sequence with an associated property list, which must be terminated 
        by calling ``stream.end_marked_content()``
        
        :param tag: A name object indicating the role or significance of the point. 
        :param properties: Either an inline dictionary containing the property list or a name 
            object associated with it in the Properties subdictionary of the current resource 
            dictionary (see 14.6.2, “Property Lists”).
        """
        self._operations.append(Operator.begin_marked_content_properties(tag, properties))
        return self

    def end_marked_content(self):
        """
        End a marked-content sequence begun by ``stream.begin_marked_content()`` or 
        ``stream.begin_marked_content_properties()``
        """
        self._operations.append(Operator.end_marked_content())
        return self

    def begin_compatibility(self):
        """
        Begin a compatibility section. Readers will ignore unrecognized operators (along with their
        operands) without error in this section.
        """
        self._operations.append(Operator.begin_compatibility())
        return self

    def end_compatibility(self):
        """
        End the section started with ``stream.begin_compatibility()``
        """
        self._operations.append(Operator.end_compatibility())
        return self
