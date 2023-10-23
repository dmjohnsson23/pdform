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
* Populate form data (including working with checkboxes and radio buttons, and setting appearance streams without relying on the reader)
* The ability to stamp images on a page (useful for non-cryptographic signatures)
* Basic low-level interface for building content streams (which could be used to build higher-level interfaces)
* And, of course, anything you could already do with pdfrw

No stand-alone documentation exists right now, but ``pdform -h`` will get you command-line help, and most of the functions and classes have descriptive docblocks. All references to the PDF specs within docblocks and comments are based on this version of the spec: <https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf>