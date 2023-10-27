# PDForm

This is a wrapper around the [pikepdf](https://pypi.org/project/pikepdf/) library with two primary design goals:

1. Expose the structure of the PDF using logically-named properties, classes, and methods; instead of requiring you to read the PDF spec to learn the "raw" PDF structure with all its cryptic abbreviations
2. Primarily focus on making minor changes to existing PDFs (Filling in form data, stamping an image on the page, etc...) where something like reportlab is overkill and/or poorly suited

This was created primarily as a means of populating data into PDF forms, though hopefully it may also be useful for other purposes.

Current capabilities:
* Populate form data
    - Supports checkboxes, including those with "checked" values other than "/Yes"
    - Supports radio buttons
    - Supports text fields, including multi-line text fields
    - Generates appearance streams, without relying on the reader
* The ability to stamp images on a page (useful for non-cryptographic signatures: as in literally just slapping a PNG image of a signature on the page)
* Basic low-level interface for building content streams, which could be used to build higher-level interfaces (Currently used to generate appearance streams)
* And, of course, anything you could already do with pikepdf

No stand-alone documentation exists right now, but ``pdform -h`` will get you command-line help, and most of the functions and classes have descriptive docblocks. All references to the PDF specs within docblocks and comments are based on this version of the spec: <https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf>

## Example

CLI Usage
```shell
# Outputs a JSON-formatted string showing details about all form fields
python3 -m pdform inspect-form path/to/form.pdf

# Create a filled version of the form
python3 -m pdform fill-form path/to/form.pdf '{"field1":"value1","checkbox":True,"signature":"path/to/sig_img.png"}' path/to/output.pdf
```

See the examples folder for Python library usage.

## TODOs/Wishlist

* PikePDF already has a `Pdf.generate_appearance_streams()` method, which we could use in place of a lot of the work we are doing. However, this method has some issues that would need to be fixed before we could use it:
    - Does not properly support checkboxes, but I submitted an issue to fix: <https://github.com/qpdf/qpdf/issues/1056>.
    - Does not support multi-line text fields, newlines are ignored and nothing is wrapped. It is explicitly stated in the documentation that this is not supported.
* PikePdf already has classes for streams and stream operations that could replace ours, though they are slightly lower level than ours.
* PikePdf already has a Rectangle class that could replace our `Rect` class.
* The underlying library (QPDF) has `QPDFFormFieldObjectHelper` and `QPDFAcroFormDocumentHelper`, which if exposed could be of use to us for `Field`

## Other Options Explored

"But don't such tools already exist? Why roll your own?"

You'd think so, but I haven't found one.

I've chosen to use pikepdf because:
1. It both reads and writes PDFs. Other tools often only read (e.g. pdfminer) or only write (pydyf, reportlab).
2. It seem well-designed architecturally, and its interface is really easy to learn and use compared to others (I tried pypdf, but found it really frustrating to use, and disliked the weird barriers and API differences that existed between reading and writing).
3. It's very low-level, which means you have to read the PDF spec to figure out how to use it...but honestly that's a good thing when using it as the base of another project.
4. It's fairly feature-rich and handles compression better than pdfrw, which is what I was using previously

Some other tools I've looked at:
* [PdfTK](https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/)
    - Form filling must be done using FDF files, which are not really any easier to create than just modifying the PDF directly
* [MuTool Javascript API](https://mupdf.readthedocs.io/en/latest/mutool-run.html)
    - For whatever reason I just couldn't make it work correctly
* [PdfMiner](https://pypi.org/project/pdfminer/)
    - Not meant for making modifications
* [PyDyF](https://pypi.org/project/pydyf/)
    - Not meant for working with existing PDFs
* [Reportlab](https://www.reportlab.com/)
    - Overkill for the limited modifications we want to make
    - Doesn't support loading existing PDFs without a commercial license
    - Despite all that, no built-in support for forms anyway
* [PyPDF](https://pypi.org/project/pypdf/)
    - Weird incongruence between APIs for reading and writing
    - Not great documentation
    - Built-in form fill function doesn't support a lot of our use cases
* [pdfrw](https://pypi.org/project/pdfrw/)
    - Doesn't work well with compression
    - Not as feature-rich as pikepdf
* [PyPDFium2](https://pypdfium2.readthedocs.io/en/stable/index.html)
    - May look more into this in the future