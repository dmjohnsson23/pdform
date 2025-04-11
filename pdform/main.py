#!/usr/bin/python3
"""
Tools for dealing with PDFs, specially focused on filling out PDF forms.
"""
import argparse
import sys
from .model import *
from .tools import *

argp = argparse.ArgumentParser(
    prog='pdform', 
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter
)

argp.set_defaults(func=lambda _: argp.print_help())
argp_sub = argp.add_subparsers()

# pdform fill-form
argp_fill_form = argp_sub.add_parser('fill-form', help='Fill a PDF with data')
argp_fill_form.add_argument('template', help="Path to the PDF you'd like to fill")
argp_fill_form.add_argument('data', help='The data to fill the form, as a JSON object mapping field qualified names to values')
argp_fill_form.add_argument('output', help="Path to output PDF, or '-' to use stdout", default='-', nargs='?')
def cli_fill_form(args):
    from pikepdf import Pdf
    from json import loads
    pdf = Pdf.open(args.template)
    data = loads(args.data)
    fill_form(pdf, data)
    output_path = args.output
    if output_path == '-':
        output_path = sys.stdout.buffer
    pdf.save(output_path)
argp_fill_form.set_defaults(func=cli_fill_form)

# pdform inspect-form
argp_inspect_form = argp_sub.add_parser('inspect-form', help='Get a description of the fields in the given form')
argp_inspect_form.add_argument('pdf', help="Path to the PDF you'd like to inspect for form fields")
def cli_inspect_form(args):
    from pikepdf import Pdf
    from json import dumps
    pdf = Pdf.open(args.pdf)
    info = []
    for field in iter_fields(pdf, pdf.Root.AcroForm.Fields):
        field = Field(pdf, field)
        info.append({
            'qualified_name':field.qualified_name,
            'label': str(field.raw.TU),
            'input_type': field.input_type.value,
            'required': field.required,
            'read_only': field.read_only,
            'options': field.options,
            'rect': [float(coord) for coord in field.rect.raw] if field.rect is not None else None,
        })
    print(dumps(info, indent=4))
argp_inspect_form.set_defaults(func=cli_inspect_form)



def main():
    args = argp.parse_args()
    args.func(args)