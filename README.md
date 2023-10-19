# PDForm

This is a wrapper around the [pdfrw](https://github.com/pmaupin/pdfrw) library with two primary design goals:

1. Expose the structure of the PDF using logically-named properties, classes, and methods; instead of requiring you to read the PDF spec to learn the "raw" PDF structure with all its cryptic abbreviations
2. Primarily focus on making minor changes to existing PDFs (Filling in form data, stamping an image on the page, etc...) where something like reportlab is overkill and/or poorly suited

Current capabilities:
* Populate form data (including working with checkboxes and radio buttons, and setting appearance streams without relying on the reader)
* The ability to stamp images on a page (useful for non-cryptographic signatures)
* Basic low-level interface for building content streams (which could be used to build higher-level interfaces)
* And, of course, anything you could already do with pdfrw

All references to the PDF specs within docblocks and comments are based on this version of the spec: <https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf>