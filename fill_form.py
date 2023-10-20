#! /usr/bin/python3
"""
Tool to programmatically fill a PDF form.

(Requires Python 3.7+ and pdfrw: `pip3 install pdfrw`)

"But don't such tools already exist? Why roll your own?"

Well, you'd certainly *think* that would be the case, wouldn't you. PDFTK is the best I found,
but it doesn't support checkboxes, radio buttons, or signatures, which are all kind of a big
dealbreaker. Existing python libraries like PyPDF also have form-fill functions, but again, no
support for checkboxes (properly...), signatures, and such.

This tool supports all the above (though signatures are just image stamps, not *real* signatures).

Usage:

```shell
fill_form.py template.pdf '{"fieldname":"value","checkbox":true,"signature":"sig.png"}' outfile.pdf
```

Tip: You can use Firefox's build-in PDF view, together with inspect element, to get the field names
"""
# IMPORTANT: Many comments below reference the PDF spec:
# https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf
# Open a copy before reading this source code
from io import BytesIO
from warnings import warn
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfObject, PdfString, PdfName, PdfArray, PageMerge
from pdfrw.objects.pdfname import BasePdfName
from typing import Optional, Union
from enum import Enum, IntFlag
from PIL import Image, ImageOps
import sys
from json import loads
import re

def main(template_path, data, output_path='-'):
    pdf = PdfReader(template_path)
    if isinstance(data, str):
        data = loads(data)
    fill_form(pdf, data)
    if output_path == '-':
        output_path = sys.stdout.buffer
    PdfWriter().write(output_path, pdf)


class InputType(Enum):
    text = 'text'
    textarea = 'textarea'
    password = 'password'
    select = 'select'
    combo = 'combo'
    checkbox = 'checkbox'
    radio = 'radio'
    button = 'button'
    signature = 'signature'


class FieldFlags(IntFlag):
    # Note: spec numbers bits starting with 1, so indexes below are off-by-one
    # Table 221 – Field flags common to all field types
    ReadOnly = 1 << 0
    Required = 1 << 1
    NoExport = 1 << 2
    # Table 226 – Field flags specific to button fields
    NoToggleToOff = 1 << 14
    Radio = 1 << 15
    Pushbutton = 1 << 16
    RadiosInUnison = 1 << 25
    # Table 228 – Field flags specific to text fields
    Multiline = 1 << 12
    Password = 1 << 13
    FileSelect = 1 << 20
    MultiSelect = 1 << 21
    DoNotSpellCheck = 1 << 22
    DoNotScroll = 1 << 23
    Comb = 1 << 24
    RichText = 1 << 25
    # Table 230 – Field flags specific to choice fields
    Combo = 1 << 17
    Edit = 1 << 18
    Sort = 1 << 19
    CommitOnSelChange = 1 << 26


class Rect(PdfArray):
    # Note: The PDF standard defines the origin as the bottom-left corner of the page (See 8.3.2.3)
    # Points are defined as [lower_left_x, lower_left_y, upper_right_x, upper_right_y] (See 4.40)
    def __init__(self, source=[0.0, 0.0, 0.0, 0.0]):
        if len(source) != 4:
            raise ValueError('Rect arrays must have exactly four elements')
        source = [float(el) for el in source]
        super().__init__(source)
    
    @property
    def left(self)->float:
        return self[0]
    @left.setter
    def left(self, value: float):
        self[0] = float(value)

    @property
    def bottom(self)->float:
        return self[1]
    @bottom.setter
    def bottom(self, value: float):
        self[1] = float(value)

    @property
    def right(self)->float:
        return self[2]
    @right.setter
    def right(self, value: float):
        self[2] = float(value)

    @property
    def top(self)->float:
        return self[3]
    @top.setter
    def top(self, value: float):
        self[3] = float(value)

    @property
    def height(self)->float:
        return self.top - self.bottom
    @property
    def width(self)->float:
        return self.right - self.left
    
    def to_bbox(self):
        """
        Get a rect with the same width and height as this one, but located at (0, 0).

        Bounding boxes represent independent coordinate systems, such as for form XObjects.
        """
        return Rect([0, 0, self.width, self.height])


class Field(PdfDict):
    @property
    def qualified_name(self) -> Optional[str]:
        """
        The fully-qualified name of this field. This is the /T value of this and all ancestors,
        concatenated together with dots.
        """
        return self.get_qualified_field_name(self)

    @classmethod
    def get_qualified_field_name(cls, field: PdfDict) -> Optional[str]:
        """
        Helper function to calculate :py:attr:`qualified_name`.
        """
        # See 12.7.3.2
        if "/T" not in field and "/Parent" in field:
            return cls.get_qualified_field_name(field.Parent)
        elif "/T" not in field:
            return None
        elif "/Parent" in field:
            return f"{cls.get_qualified_field_name(field.Parent)}.{field.T.to_unicode()}"
        else:
            return field.T.to_unicode()
    
    @property
    def input_type(self) -> Optional[InputType]:
        """
        Get the type of input this field represents
        """
        flags = FieldFlags(int(self.inheritable.Ff or 0))
        field_type = self.inheritable.FT
        if field_type == '/Sig':
            return InputType.signature
        elif field_type == '/Btn':
            if FieldFlags.Radio in flags:
                return InputType.radio
            elif FieldFlags.Pushbutton in flags:
                return InputType.button
            else:
                return InputType.checkbox
        elif field_type == '/Ch':
            if FieldFlags.Combo in flags:
                return InputType.combo
            else:
                return InputType.select
        elif field_type == '/Tx':
            if FieldFlags.Pushbutton in flags:
                return InputType.password
            elif FieldFlags.Multiline in flags:
                return InputType.textarea
            else:
                return InputType.text
        
    def set_value(self, pdf, value): # TODO I'd like to get rid of the PDF parameter
        input_type = self.input_type
        if input_type is InputType.radio:
            self._set_value_radiogroup(value)
        elif input_type is InputType.checkbox:
            self._set_value_checkbox(value)
        elif input_type is InputType.signature:
            # TODO we may be able to use this: https://pyhanko.readthedocs.io/en/latest/index.html
            warn('Signature fields are not supported; skipping')
            return
        else:
            # Assume text field
            self._set_value_text(pdf, value)

    def _set_value_radiogroup(self, value):
        if not isinstance(value, BasePdfName):
            value = PdfName(str(value))
        group = self
        off = PdfName('Off')
        if self.Kids is None:
            group = Field(self.Parent)
            if group.input_type is not InputType.radio:
                raise RuntimeError(f'Field {self.qualified_name} is a radio button not part of any group, or is a radio group with no buttons')
        for kid in group.Kids:
            # Set appearance streams for children (individual radio buttons)
            states = set(kid['/AP']['/N'].keys())
            states.discard(off)
            if value in states:
                kid.update(PdfDict(AS=value))
            elif '/AS' in kid:
                kid.update(PdfDict(AS=off))
        # Set value for parent (radio group)
        group.update(PdfDict(V=value))

    def _set_value_checkbox(self, value):
        off = PdfName('Off')
        states = set(self['/AP']['/N'].keys())
        states.discard(off)
        on = states.pop()
        # Set/Delete both value and appearance stream
        if value:
            self.update(PdfDict(V=on, AS=on))
        else:
            self.update(PdfDict(V=off, AS=off))
    
    def _set_value_text(self, pdf, value):
        if isinstance(value, PdfString):
            self.update(PdfDict(V=value))
            value = value.to_unicode()
        else:
            value = str(value)
            self.update(PdfDict(V=PdfString.from_unicode(value)))
        # We also need to set the normal appearance stream ['/AP']['/N'] to match the text.
        # (In theory, we could just set the "NeedAppearances" flag on `pdf.Root.AcroForm` and 
        # let the reader figure this out for us, but in practice not all readers will...)
        #
        # First get the default appearance, either from the parent chain or the root AcroForm
        da = self.inheritable.DA
        if da is None:
            da = pdf.Root.AcroForm.get('/DA')
        # All spec-compliant PDFs should have DA in one of those two places, so fail if not
        if da is None:
            raise RuntimeError(f'Corrupted or Invalid PDF: Field {self.qualified_name} has no /DA')
        # Now build the appearance stream for the entered text
        rect = Rect(self.Rect)
        xobject = layout_form_text(pdf, value, da, rect)
        if '/AP' not in self:
            self.update(PdfDict(AP = PdfDict(N = xobject)))
        else:
            self.AP.update(PdfDict(N = xobject))


def iter_fields(annots):
    """
    Iterator over a set of fields. For radio buttons, yield the parent. For all others, yield the leaf node.

    :param annots: The annotations or fields to iterate over, can be:
        - `pdf.Root.Acroform.Fields`
        - `page.Annots`
        - `field.Kids`
    """
    radios = set()
    for annot in annots:
        if annot['/Subtype'] != '/Widget':
            # Not a widget. We'll still iterate Kids just in case any of them are.
            if '/Kids' in annot:
                yield from iter_fields(annot.Kids)
            continue
        field = Field(annot)
        input_type = field.input_type
        if input_type is InputType.radio:
            if '/Kids' in annot:
                # Radio group
                yield annot
            else:
                # Single radio button, only yield the parent
                if field.qualified_name in radios:
                    continue # We already did this one
                yield annot.Parent
                radios.add(field.qualified_name)
        elif '/Kids' in annot:
            # All other groups, yield the leaf nodes
            yield from iter_fields(annot.Kids)
        else:
            # Leaf node
            yield annot


def fill_form(pdf, data:dict):
    for page in pdf.pages:
        annotations = page['/Annots']
        if annotations is None:
            continue
        to_delete = []
        for index, annotation in enumerate(iter_fields(annotations)):
            field = Field(annotation)
            key = field.qualified_name
            if key and key in data and data[key] is not None:
                if annotation.inheritable.FT == '/Sig':
                    # Replace sig fields with stamps
                    stamp(data[key], page, Rect(annotation.Rect))
                    to_delete.append(index)
                else:
                    field.set_value(pdf, data[key])
                    annotation.update(field)
        for index in reversed(to_delete):
            page['/Annots'].pop(index)
    if '.stamps' in data:
        # Custom stamps not associated with fields
        for stamp_data in data['.stamps']:
            if not stamp_data['img']:
                continue
            stamp(stamp_data['img'], pdf.pages[stamp_data['page']-1], Rect(stamp_data['rect']))
    #pdf.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject('true')))


# class PdfContentStream:
#     # See 7.8
#     _operands = []
#     def operand(self, operand:str, *params:Union[PdfArray,PdfDict,PdfName,PdfString,int,float]):
#         # Table 51 lists possible operands
#         self._operands.append((operand, params))
#         return self
    
#     def extend(self, other:PdfContentStream):
#         self._operands.extend(other._operands)
#         return self
    
#     def render(self):
#         pass
#    # TODO PdfTokens could be used to split the string when parsing
#    # Basically the same concept of what I want: https://doc.courtbouillon.org/pydyf/stable/api_reference.html#pydyf.Stream 
#    # See also https://github.com/Kozea/WeasyPrint/blob/main/weasyprint/pdf/stream.py


# class TextObject(PdfContentStream):
#     # The basic structure of a text object is like this: (From 9.2.2, see 9.4)
#     # BT                     <= Begin text object
#     #     /F13 12 Tf         <= Define font (F13) and scale factor (12pt) with the Tf operator
#     #     288 720 Td         <= Specify the coordinates with the Td operator
#     #     ( ABC ) Tj         <= Render the actual text with the Tj operator
#     # ET                     <= End text object
#     pass

def layout_form_text(pdf, text:str, da:str, rect:Rect, padding=1, line_spacing=1):
    """
    Lay out the given text in the given bounding box, returning a form XObject

    :param pdf: The PDF that this field belongs to
    :param text: The text to layout in the field
    :param da: The /DA attribute of the field
    :param rect: The /Rect attribute of the field
    """
    if isinstance(padding, tuple) and len(padding) == 2:
        pad_x, pad_y = padding
    else:
        pad_x = pad_y = padding
    if isinstance(da, PdfString):
        da = da.to_unicode()
    # Extract font information from DA
    # The DA will be something like this, defining font and scale factor for the text object:
    # /CourierNewPSMT 10.00 Tf 0 g
    match = re.search('\/([!-~]+)\s+(\d+(?:\.\d+))\s*Tf', da)
    if not match:
        raise ValueError(f'Invalid or missing /DA (contains no valid Tf operator): {repr(da)}')
    font_family = PdfName(match[1])
    font_size = float(match[2])
    # Lookup the font info in the main font dict 
    # TODO technically this data could also be stored in field.inheritable.DR
    font_dict = pdf.Root.AcroForm.DR.Font
    if font_family not in font_dict:
        raise RuntimeError(f'Cannot find font information for {font_family} (Available fonts: {", ".join(font_dict.keys())})')
    font_data = font_dict[font_family]
    # See 12.5.5 and in 8.10
    # Form Dictionary (Described in table 95)
    bbox = rect.to_bbox()
    xobject = PdfDict(
        Type = 'XObject',
        Subtype = 'Form',
        FormType = 1,
        BBox = bbox,
        Resources = PdfDict(
            Font = PdfDict({
                PdfName(font_family): font_data
            })
        )
    )
    # Convert the DA to new text stream (see 12.7.3.3)
    stream = (
        "/Tx BMC " # Begin marked content, with Tx tag (I guess this makes text more extractable)
        "q " # Push graphics stack
        "BT " # Begin text object
        f"{da} " # Include the default appearance
    )
    for lineno, line in enumerate(text.splitlines()):
        # TODO this is very naive and could probably be significantly improved
        # Refer to the following similar implementations for ideas:
        # * https://github.com/py-pdf/pypdf/blob/5c3550f66c5da530eb8853da91afe0f942afcbef/pypdf/_writer.py#L857
        # * https://github.com/mozilla/pdf.js/blob/2c87c4854a486d5cd0731b947dd622f8abe5e1b5/src/core/annotation.js#L2138
        # * https://github.com/fwenzel/pdftk/blob/a3db40d1a43207eaad558aa9591ef81403b51616/java/pdftk/com/lowagie/text/pdf/AcroFields.java#L407
        if lineno == 0:
            # Position the cursor at the top of the first line
            stream += f"{pad_x} {bbox.top - pad_y - font_size} Td "
        else:
            # Position the cursor at the start of the next line (offset from previous line)
            stream += f"0 {-line_spacing * font_size} Td "
        # Print the actual text
        stream += f"{PdfString.from_unicode(line)} Tj "
    stream += (
        "ET " # End text object
        "Q " # Pop graphics stack
        "EMC" # End marked content
    )
    # Set the stream on the form XObject
    xobject.stream = stream
    print(xobject, stream)
    return xobject


def stamp(img, page, rect:Rect, transparent_background:Optional[bool]=None):
    """
    Stamp an image on the page, fitting it in the box of the given rect.

    :param img: The image to stamp. Can be a file path, open file object, or base64 data URL.
    :param page: The page to stamp the image on.
    :param rect: The box in which to place the image. The image will be scaled to fit.
    :param transparent_background: If True, all white pixels will be made transparent.
    """
    if isinstance(img, str) and img.startswith('data:'):
        # embedded base64
        from base64 import b64decode
        _, path = path.split(',', 2)
        path = BytesIO(b64decode(path))
    # Open image and convert to RGB (Greyscale images cause issues)
    img = Image.open(img).convert('RGB')
    # Scale the image and add margins to perfectly match the destination
    img_width, img_height = img.size
    image_ratio = img_height / img_width
    target_ratio = rect.height / rect.width
    scale_factor = 1
    margin_x = 0
    margin_y = 0
    if image_ratio > target_ratio: 
        # Taller ratio than target
        if img_height > rect.height:
            # Scale down, and center horizontally
            scale_factor = rect.height / img_height
            margin_x = (rect.width - (img_width * scale_factor)) / 2
        else:
            # Center without scaling
            margin_x = (rect.width - img_width) / 2
            margin_y = (rect.height - img_height) / 2
    elif image_ratio < target_ratio:
        # Wider ratio than target
        if img_width > rect.width:
            # Scale down, and center vertically 
            scale_factor = rect.width / img_width
            margin_y = (rect.height - (img_height * scale_factor)) / 2
        else:
            # Center without scaling
            margin_x = (rect.width - img_width) / 2
            margin_y = (rect.height - img_height) / 2
    else:
        # Same ratio as target
        if img_height > rect.height:
            # Scale down
            scale_factor = rect.height / img_height
        else:
            # Center without scaling
            margin_x = (rect.width - img_width) / 2
            margin_y = (rect.height - img_height) / 2
    # Remove a transparent background (as a solid color)
    if transparent_background:
        # FIXME
        mask = img.convert('L')
        img.putalpha(mask)
    # Convert the image to a PDF
    img_as_pdf = BytesIO()
    img.save(img_as_pdf, 'pdf')
    del img
    img_as_pdf.seek(0)
    # Overlay the PDF version of the image over the page
    stamp_pdf = PdfReader(img_as_pdf)
    merge = PageMerge(page).add(stamp_pdf.pages[0])
    if scale_factor != 1:
        merge[1].scale(scale_factor)
    merge[1].x = rect.left#+margin_x
    merge[1].y = rect.bottom+margin_y
    merge.render()


if __name__ == "__main__":
    main(*sys.argv[1:])
