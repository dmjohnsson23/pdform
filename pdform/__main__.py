#!/usr/bin/python3
"""
Tools for dealing with PDFs, specially focused on filling out PDF forms.
"""
import os, sys
# allow importing self (why is this necessary?)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pdform.main import main

if __name__ == '__main__':
    main()