from warnings import warn
from pikepdf import Dictionary, String, Name, Array
from typing import Optional, Union
from enum import Enum, IntFlag
import re
from .base import Wrapper, WrappedProperty
from .rect import Rect
from .content_stream import ContentStream
from .xobject import FormXObject
from .font import Font
from ..utils.text import layout_text_line, layout_text_multiline
from ..utils.dictionaries import get_inheritable


class InputType(Enum):
    """
    This represents the field type as interpreted. These values are not found in the PDF spec; they 
    are merely used as a convenience to avoid having to always check both the field type and field 
    flags to determine the input type. See `Field.input_type`.
    """
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
    """
    Represents the field flags values, as explained in the PDF spec sections 12.7.3.1 and 12.7.4. 
    These flags help determine information about the nature of the field beyond those expressed by 
    the broader field type. For example, to distinguish between a checkbox, radio button, or push
    button.
    """
    @classmethod
    def lookup(cls, value):
        if value is None:
            value = 0
        elif isinstance(value, str) and value.isdigit():
            value = int(value)
        return cls(value)
    # Note: spec numbers bits starting with 1, so indexes below are off-by-one
    # Values that get reused (make them first so all the other uses are aliases)
    RadiosInUnison_or_RichText = 1 << 25
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


class Field(Wrapper):
    """
    This wraps a form-field annotation dictionary and provides methods and properties to aid in 
    interacting with that dictionary.
    """
    raw:Dictionary
    rect = WrappedProperty(Name.Rect, Rect)
    field_flags = WrappedProperty(Name.Ff, FieldFlags.lookup, FieldFlags(0), True)
    @property
    def qualified_name(self) -> Optional[str]:
        """
        The fully-qualified name of this field. This is the /T value of this and all ancestors,
        concatenated together with dots.
        """
        return self.get_qualified_field_name(self.raw)

    @classmethod
    def get_qualified_field_name(cls, field: Dictionary) -> Optional[str]:
        """
        Helper function to calculate :py:attr:`qualified_name`.
        """
        # See 12.7.3.2
        if "/T" not in field and "/Parent" in field:
            return cls.get_qualified_field_name(field.Parent)
        elif "/T" not in field:
            return None
        elif "/Parent" in field:
            return f"{cls.get_qualified_field_name(field.Parent)}.{field.T}"
        else:
            return str(field.T)
    
    @property
    def input_type(self) -> Optional[InputType]:
        """
        Get the type of input this field represents
        """
        flags = self.field_flags
        field_type = get_inheritable(self.raw, Name.FT)
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
    
    @property
    def read_only(self):
        return FieldFlags.ReadOnly in self.field_flags
    @read_only.setter
    def read_only(self, value):
        if value:
            self.field_flags |= FieldFlags.ReadOnly
        else:
            self.field_flags &= ~FieldFlags.ReadOnly

    @property
    def required(self):
        return FieldFlags.Required in self.field_flags
    @required.setter
    def required(self, value):
        if value:
            self.field_flags |= FieldFlags.Required
        else:
            self.field_flags &= ~FieldFlags.Required

    @property
    def no_export(self):
        return FieldFlags.NoExport in self.field_flags
    @no_export.setter
    def no_export(self, value):
        if value:
            self.field_flags |= FieldFlags.NoExport
        else:
            self.field_flags &= ~FieldFlags.NoExport
    

    @property
    def options(self)->list:
        """
        For radio buttons, checkboxes, or select fields, list all possible options.

        Radio button and checkboxes will both return a list of Name objects corresponding to the
        allowed states. Select fields will return a list that contains either String objects,
        representing the value, or a [export_value, display_value] pairs.
        """
        input_type = self.input_type
        if input_type is InputType.radio:
            group = self.raw
            states = set()
            if self.raw.Kids is None:
                group = Field(self.raw.Parent)
                if group.input_type is not InputType.radio:
                    raise RuntimeError(f'Field {self.qualified_name} is a radio button not part of any group, or is a radio group with no buttons')
            for kid in group.Kids:
                states.update(kid.AP.N.keys())
            return list(states)
        elif input_type is InputType.checkbox:
            return list(self.raw.AP.N.keys())
        elif input_type is InputType.select or input_type is InputType.combo:
            return list((str(opt[0]), str(opt[1])) if isinstance(opt, Array) else opt for opt in self.raw.Opt)

    @property
    def value(self):
        """
        The value of this field. When setting, appearance streams and other associated properties 
        will also be set.
        """
        return get_inheritable(self.raw, Name.V)
    @value.setter
    def value(self, value):
        # Useful link: https://westhealth.github.io/exploring-fillable-forms-with-pdfrw.html
        # Note: The above link incorrectly conflates listbox/combobox with uniselect/multiselect
        # Actually, listbox = dropdown select, combobox = text input with dropdown suggestions
        input_type = self.input_type
        if input_type is InputType.radio:
            self._set_value_radiogroup(value)
        elif input_type is InputType.checkbox:
            self._set_value_checkbox(value)
        elif input_type is InputType.signature:
            # TODO we may be able to use this: https://pyhanko.readthedocs.io/en/latest/index.html
            warn('Signature fields are not supported; skipping')
            return
        elif input_type is InputType.select or input_type is InputType.combo:
            self._set_value_choice(value)
        else:
            # Assume text field
            self._set_value_text(value)

    def _set_value_radiogroup(self, value):
        if not isinstance(value, Name):
            value = str(value)
            if value[0] != '/':
                value = f"/{value}"
            value = Name(value)
        group = self.raw
        off = Name.Off
        if self.raw.Kids is None:
            group = Field(self.raw.Parent)
            if group.input_type is not InputType.radio:
                raise RuntimeError(f'Field {self.qualified_name} is a radio button not part of any group, or is a radio group with no buttons')
        for kid in group.Kids:
            # Set appearance streams for children (individual radio buttons)
            states = set(kid.AP.N.keys())
            states.discard(off)
            if value in states:
                kid.AS=value
            elif '/AS' in kid:
                kid.AS=off
        # Set value for parent (radio group)
        group.V=value

    def _set_value_checkbox(self, value):
        off = Name.Off
        states = set(self.raw.AP.N.keys())
        if isinstance(value, (str,bytes,Name)) and value in states:
            if not isinstance(value, Name):
                value = Name(value)
            self.raw.V = value
            self.raw.AS = value
            return
        states.discard(off)
        on = Name(states.pop())
        # Set/Delete both value and appearance stream
        if value is True:
            self.raw.V=on
            self.raw.AS=on
        elif value is False or value is None:
            self.raw.V=off
            self.raw.AS=off
        else:
            raise ValueError(f'Invalid checkbox value: {repr(value)}')
    
    def _set_value_text(self, value):
        if isinstance(value, String):
            self.raw.V=value
            value = str(value)
        else:
            value = str(value)
            self.raw.V=String(value)
        # We also need to set the normal appearance stream ['/AP']['/N'] to match the text.
        # (In theory, we could just set the "NeedAppearances" flag on `pdf.Root.AcroForm` and 
        # let the reader figure this out for us, but in practice not all readers will...)
        #
        # First get the default appearance, either from the parent chain or the root AcroForm
        da = get_inheritable(self.raw, Name.DA)
        if da is None:
            da = self.pdf.Root.AcroForm.get('/DA')
        # All spec-compliant PDFs should have DA in one of those two places, so fail if not
        if da is None:
            raise RuntimeError(f'Corrupted or Invalid PDF: Field {self.qualified_name} has no /DA')
        # Now build the appearance stream for the entered text
        xobject = layout_form_text(self.pdf, value, da, self.rect, multiline=FieldFlags.Multiline in self.field_flags)
        if '/AP' not in self.raw:
            self.raw.AP = Dictionary(N = xobject.raw)
        else:
            self.raw.AP.N = xobject.raw
        # If it's a rich text field, also set the rich value, which uses an XHTML-like language for 
        # markup and are placed in /RV, see 12.7.3.4
        # (We don't actually support the input of rich text right now, just the output)
        # FIXME: This doesn't actually seem to make any visible difference whatsoever
        if FieldFlags.RichText in self.field_flags:
            ds = str(self.raw.DS).replace('"', '\\"')
            xfa_api = {
                '1.5': '2.0',
                '1.6': '2.2',
                '1.7': '2.4'
            }.get(self.pdf.pdf_version, '2.4')
            rich_value = (
                '<?xml version="1.0"?>'
                '<body xmlns="http://www.w3.org/1999/xhtml" '
                'xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/" '
                'xfa:APIVersion="pdform:0.1.0" ' # Adobe uses "Acroform:2.7.0.0"
                f'xfa:spec="{xfa_api}" '
                '>'
                f'<p style="{ds}">'+
                f'</p><p style="{ds}">'.join(value.splitlines())+
                '</p>'
                '</body>'
            )
            self.raw.RV = String(rich_value)
    

    def _set_value_choice(self, value):
        if FieldFlags.MultiSelect in self.field_flags:
            raise NotImplementedError('Multiselect not yet supported')
            # TODO we should just have to set V to an array, but I'm not sure what to do for appearance
        self.field_flags |= FieldFlags.Combo # Hacky workaround since we aren't validating options right now
        self._set_value_text(value)



def layout_form_text(pdf, text:str, da:Union[String,bytes], rect:Rect, padding=0, multiline=False, line_spacing=None):
    """
    Lay out the given text in the given bounding box, returning a form XObject

    :param pdf: The PDF that this field belongs to
    :param text: The text to layout in the field
    :param da: The /DA attribute of the field
    :param rect: The /Rect attribute of the field
    """
    if isinstance(da, String):
        da = bytes(da)
    # Extract font information from DA
    # The DA will be something like this, defining font and scale factor for the text object:
    # /CourierNewPSMT 10.00 Tf 0 g
    match = re.search(b'(\/[!-~]+)\s+(\d+(?:\.\d+))\s*Tf', da)
    if not match:
        raise ValueError(f'Invalid or missing /DA (contains no valid Tf operator): {repr(da)}')
    font_family = Name(match[1].decode())
    font_size = float(match[2])
    # Lookup the font info in the main font dict 
    # TODO technically this data could also be stored in field.inheritable.DR
    font_dict = pdf.Root.AcroForm.DR.Font
    if font_family not in font_dict:
        raise RuntimeError(f'Cannot find font information for {font_family} (Available fonts: {", ".join(font_dict.keys())})')
    font_data = font_dict[font_family]
    font = Font(pdf, font_data, font_family)
    # See 12.5.5 and in 8.10
    # Form Dictionary (Described in table 95)
    bbox = rect.to_bbox()
    fdict = Dictionary()
    fdict[font_family] = font_data
    resources = Dictionary(Font = fdict)
    # Convert the DA to new text stream (see 12.7.3.3)
    stream = (ContentStream()
        .begin_marked_content(Name.Tx) # (I guess this makes text more extractable)
        .push_stack()
        .begin_text()
        .append_raw(da) # Include the default appearance
        # TODO this is very naive and could probably be significantly improved
        # Refer to the following similar implementations for ideas:
        # * https://github.com/py-pdf/pypdf/blob/5c3550f66c5da530eb8853da91afe0f942afcbef/pypdf/_writer.py#L857
        # * https://github.com/mozilla/pdf.js/blob/2c87c4854a486d5cd0731b947dd622f8abe5e1b5/src/core/annotation.js#L2138
        # * https://github.com/fwenzel/pdftk/blob/a3db40d1a43207eaad558aa9591ef81403b51616/java/pdftk/com/lowagie/text/pdf/AcroFields.java#L407
        # * https://github.com/qpdf/qpdf/blob/81823f4032caefd1050bccb207d315839c1c48db/libqpdf/QPDFFormFieldObjectHelper.cc#L746
        # FIXME:
        # * Does not respect field-defined alignment and spacing
        # * Weird spacing issue in Firefox (need set_word_spacing? Adobe looks like it just uses separate Td and Tj operations for each word.)
        .extend(
            layout_text_multiline(
                pdf, text, bbox, font, font_size, 
                include_set_font=False, padding=padding, leading=line_spacing
            )
            if multiline else 
            layout_text_line(
                pdf, text, bbox, font, font_size, 
                include_set_font=False, padding=padding
            )
        )
        .end_text()
        .pop_stack()
        .end_marked_content()
    )
    # Set the stream on the form XObject
    return FormXObject.new(pdf, bbox, stream, resources)
