#!/usr/bin/python3
"""
Tools for dealing with PDFs, specially focused on filling out PDF forms.
"""
import argparse
import os, sys
# allow importing self (why is this necessary?)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pdform.tools import *

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
    from pdfrw import PdfReader, PdfWriter
    from json import loads
    pdf = PdfReader(args.template)
    data = loads(args.data)
    fill_form(pdf, data)
    output_path = args.output
    if output_path == '-':
        output_path = sys.stdout.buffer
    PdfWriter().write(output_path, pdf)
argp_fill_form.set_defaults(func=cli_fill_form)



if __name__ == '__main__':
    args = argp.parse_args()
    args.func(args)