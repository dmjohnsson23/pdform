import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pdfrw import PdfReader, PdfWriter
from pdform import fill_form

pdf = PdfReader(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pdfs', 'VA9.pdf'))
fill_form(pdf, {
    # ===== Page 1 ===== #
    # 1. NAME OF VETERAN (Last Name, First Name, Middle Initial)re you fill out this form.  V A also encourages you to get assistance from your representative in filling out this form.
    "VA9[0].#subform[0].TextField1[0]": "Smith, John J",
    # 2. CLAIM FILE NO. (Include prefix)
    "VA9[0].#subform[0].TextField1[1]": "12345679",
    # 3. INSURANCE FILE NO., OR LOAN NO.
    "VA9[0].#subform[0].TextField1[2]": "123456789",
    # 4. I AM THE: "VETERAN" check box
    "VA9[0].#subform[0].JF01[0]": False,
    # VETERAN'S WIDOW/ER check box
    "VA9[0].#subform[0].JF02[0]": True,
    # VETERAN'S CHILD check box
    "VA9[0].#subform[0].JF03[0]": False,
    # VETERAN'S PARENT check box
    "VA9[0].#subform[0].JF04[0]": False,
    # OTHER (Specify) check box
    "VA9[0].#subform[0].JF06[0]": False,
    # Specify other
    "VA9[0].#subform[0].TextField1[3]": None,
    # 5. TELEPHONE NUMBERS.  A. HOME Telephone number (Include Area Code).
    "VA9[0].#subform[0].Field22[0]": "(321)456-7890",
    # B. WORK telephone number (Include Area Code).
    "VA9[0].#subform[0].Field22[1]": "(321)987-6543",
    # 6. MY ADDRESS IS: (Number & Street or Post Office Box, City, State & ZIP Code)
    "VA9[0].#subform[0].TextField1[4]": "123 Example St.\nApartment 404\nAnytown, FL 12345-6789",
    # 7. IF I AM NOT THE VETERAN, MY NAME IS: (Last Name, First Name, Middle Initial)
    "VA9[0].#subform[0].TextField1[5]": "Smith, Jane B",
    # A. I HAVE READ THE STATEMENT OF THE CASE AND ANY SUPPLEMENTAL STATEMENT OF THE CASE I RECEIVED.  I AM ONLY APPEALING THESE ISSUES (List below) check boxructions.)
    "VA9[0].#subform[0].JF10[0]": True,
    # List below
    "VA9[0].#subform[0].TextField1[6]": "Thing1\nThing2",
    # B.  I WANT TO APPEAL ALL OF THE ISSUES LISTED ON THE STATEMENT OF THE CASE AND ANY SUPPLEMENTAL STATEMENT OF THE CASE THAT MY LOCAL V A OFFICE SENT TO ME check box
    "VA9[0].#subform[0].JF11[0]": False,
    # (Continue on the back, or attach sheets of paper, if you need more space.)(Be sure to read the information about this block in paragraph 6 of the attached instructions.)
    "VA9[0].#subform[0].TextField1[7]": "This is the reason:\nThis is the song that never ends, it just goes on and on my friends. Some people started singing it not knowing what it was, and now they will be singing it forever just because this is the song that never ends. It just goes on and on, my friends. Some people started singing it not knowing what it was, and now they will be singing it forever just because. This is the song that never ends. It just goes on and on my friends; some people started singing it not knowing what it was, and now they will be singing it forever just because this is the song that never ends.",
    # RadioButtonList
    "VA9[0].#subform[0].RadioButtonList[0]": "1",
    # 12.  DATE SIGNED. Enter 2-digit month, 2-digit day and 4-digit year.
    "VA9[0].#subform[0].Field2[0]": "10/23/2023",
    # 14.  DATE SIGNED. Enter 2-digit month, 2-digit day and 4-digit year.
    "VA9[0].#subform[0].Field2[1]": "10/23/2023",

    ".stamps": [
        {
            'img': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'duck.jpg'),
            'page': 1,
            'rect': [36, 30, 234, 59],
        },
        {
            'img': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'sigtest.jpg'),
            'page': 1,
            'rect': [303, 30, 504, 59],
        }
    ]
})
PdfWriter().write(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', 'fill_form_VA9.pdf'), pdf)