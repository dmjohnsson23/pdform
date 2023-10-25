# PDForm

This is a wrapper around the [pdfrw](https://github.com/pmaupin/pdfrw) library with two primary design goals:

1. Expose the structure of the PDF using logically-named properties, classes, and methods; instead of requiring you to read the PDF spec to learn the "raw" PDF structure with all its cryptic abbreviations
2. Primarily focus on making minor changes to existing PDFs (Filling in form data, stamping an image on the page, etc...) where something like reportlab is overkill and/or poorly suited

This was created primarily as a means of populating data into PDF forms, though hopefully it may also be useful for other purposes.

"But don't such tools already exist? Why roll your own?"

Well, you'd certainly *think* that would be the case, wouldn't you. PDFTK is the best I found, but so far as I could tell it doesn't (easily anyway) support checkboxes, radio buttons, or signatures, which are all kind of a big dealbreaker. Existing python libraries like PyPDF also have form-fill functions, but again, no support for checkboxes (properly...), signatures, and such. MuTool also looked good, but I just couldn't get it working right for my use case.

I've chosen to use pdfrw because:
1. As the name implies, it both reads and writes PDFs. Other tools often only read (e.g. pdfminer) or only write (pydyf, reportlab).
2. It seem well-designed architecturally, and its interface is really easy to learn and use compared to others (I tried pypdf, but found it really frustrating to use, and disliked the weird barriers and API differences that existed between reading and writing).
3. It's very low-level, which means you have to read the PDF spec to figure out how to use it...but honestly that's a good thing when using it as the base of another project.

Current capabilities:
* Populate form data
    - Supports checkboxes, including those with "checked" values other than "/Yes"
    - Supports radio buttons
    - Supports text fields, including multi-line text fields
    - Generates appearance streams, without relying on the reader
* The ability to stamp images on a page (useful for non-cryptographic signatures: as in literally just slapping a PNG image of a signature on the page)
* Basic low-level interface for building content streams, which could be used to build higher-level interfaces (Currently used to generate appearance streams)
* And, of course, anything you could already do with pdfrw

No stand-alone documentation exists right now, but ``pdform -h`` will get you command-line help, and most of the functions and classes have descriptive docblocks. All references to the PDF specs within docblocks and comments are based on this version of the spec: <https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf>

## Other Options

I don't *want* to create a new tool. I would love an existing tool that works for my use case. Here is where I explore others:

* [PikePDF](https://pikepdf.readthedocs.io/en/latest/index.html): another low-level library like pdfrw, but with more features, and pretty good documentation.
    - The base library already has `Pdf.generate_appearance_streams()`, which will reduce a lot of what we've been doing ourselves for form filling (we'll still need to actually do the filling ourselves, but PikePDF should be able to handle all the appearance stuff). Though there is this: <https://github.com/pikepdf/pikepdf/issues/58>
    - The base library already implements content streams, though at a slightly lower level than we currently are.
    - The base library has its own Rectangle class well.
    - Overlay/underlay is naively supported, replacing our `stamp` function.
    - Does not properly support checkboxes, but I submitted an issue to fix: <https://github.com/qpdf/qpdf/issues/1056>.
    - Does not support multi-line text fields, newlines are ignored and nothing is wrapped. It is explicitly stated in the documentation that this is not supported.
    - The underlying library (QPDF) has `QPDFFormFieldObjectHelper` and `QPDFAcroFormDocumentHelper`, which if exposed could be of use to us
* [PyPDFium2](https://pypdfium2.readthedocs.io/en/stable/index.html)