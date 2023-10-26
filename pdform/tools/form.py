from pikepdf import Dictionary, Name
from typing import Sequence
from ..model.form_field import Field, InputType
from ..model.rect import Rect
from .stamp import stamp
from ..utils.dictionaries import get_inheritable

def iter_fields(pdf, annots:Sequence[Dictionary]):
    """
    Iterator over a set of fields. For radio buttons, yield the parent. For all others, yield the leaf node.

    :param annots: The annotations or fields to iterate over, can be:

        * ``pdf.Root.Acroform.Fields``
        * ``page.Annots``
        * ``field.Kids``
    """
    radios = set()
    for annot in annots:
        if Name.Subtype not in annot or annot.Subtype != Name.Widget:
            # Not a widget. We'll still iterate Kids just in case any of them are.
            if Name.Kids in annot:
                yield from iter_fields(pdf, annot.Kids)
            continue
        field = Field(pdf, annot)
        input_type = field.input_type
        if input_type is InputType.radio:
            if Name.Kids in annot:
                # Radio group
                yield annot
            else:
                # Single radio button, only yield the parent
                if field.qualified_name in radios:
                    continue # We already did this one
                yield annot.Parent
                radios.add(field.qualified_name)
        elif Name.Kids in annot:
            # All other groups, yield the leaf nodes
            yield from iter_fields(pdf, annot.Kids)
        else:
            # Leaf node
            yield annot


def fill_form(pdf, data:dict):
    """
    Fill the form fields of the given PDF with the data provided.

    :param pdf: The PDF to populate with data
    :param data: The data to populate the form with. The keys of this dictionary should match
        ``field.qualified_name``. The values should be as follows:

        * For text fields, provide the value to set
        * For checkboxes, provide a boolean
        * For radio buttons, provide the value in the button's AP.N dictionary
        * For signature fields, provide the path to an image which will be stamped in its place (real
          cryptographic signatures are not supported)
    """
    for page in pdf.pages:
        if Name.Annots not in page:
            continue
        annotations = page[Name.Annots]
        to_delete = []
        for index, annotation in enumerate(iter_fields(pdf, annotations)):
            field = Field(pdf, annotation)
            key = field.qualified_name
            if key and key in data and data[key] is not None:
                if get_inheritable(annotation, Name.FT) == Name.Sig:
                    # Replace sig fields with stamps
                    stamp(data[key], page, Rect(pdf, annotation.Rect))
                    to_delete.append(index)
                else:
                    field.value = data[key]
        for index in reversed(to_delete):
            del page.Annots[index]
    if '.stamps' in data:
        # Custom stamps not associated with fields
        for stamp_data in data['.stamps']:
            if not stamp_data['img']:
                continue
            stamp(stamp_data['img'], pdf.pages[stamp_data['page']-1], Rect.new(pdf, *stamp_data['rect']))
