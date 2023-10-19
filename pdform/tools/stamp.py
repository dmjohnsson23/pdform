from ..model.rect import Rect
from typing import Optional
from io import BytesIO
from PIL import Image
from pdfrw import PdfReader, PageMerge


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
