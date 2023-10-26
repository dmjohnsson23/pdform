from ..model.rect import Rect
from typing import Optional
from io import BytesIO
from PIL import Image
from pikepdf import Pdf, Page


def stamp(img, page:Page, rect:Rect, transparent_background:Optional[bool]=None):
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
    stamp_pdf = Pdf.open(img_as_pdf)
    page.add_overlay(stamp_pdf.pages[0], rect.helper)
