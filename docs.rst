####################
PDForm Documentation
####################

======================
Command-Line Interface
======================

In addition to the Python API, this library may be invoked directly as a command-line utility.

-----------------------
Inspecting the AcroForm
-----------------------

Before you can fill the form, you will likely need to know what fields are available. The folowing command will output a JSON-formatted string which can be used to understand the internal structure of the form:

.. code-block:: shell

    python3 -m pdform inspect-form path/to/form.pdf

It will return a value similar to this:

.. code-block:: json

    [
        {
            "qualified_name": "VA9[0].#subform[0].TextField1[0]",
            "label": "IMPORTANT:  Read the attached instructions before you fill out this form.  V A also encourages you to get assistance from your representative in filling out this form.  \r\r1. NAME OF VETERAN (Last Name, First Name, Middle Initial)",
            "input_type": "text",
            "required": false,
            "read_only": false,
            "options": null
        },
        {
            "qualified_name": "VA9[0].#subform[0].TextField1[1]",
            "label": "2. CLAIM FILE NO. (Include prefix)",
            "input_type": "text",
            "required": false,
            "read_only": false,
            "options": null
        },
        {
            "qualified_name": "VA9[0].#subform[0].TextField1[2]",
            "label": "3. INSURANCE FILE NO., OR LOAN NO.",
            "input_type": "text",
            "required": false,
            "read_only": false,
            "options": null
        },
        ...
    ]

This provides the following information:

* ``qalified_name`` is the real name of the input in the form. You will use this as the key when filling the form.
* ``label`` is the human-readble lable assigned to the input. This should help you match the input to what you see visually in the form.
* ``input_type`` tells you what kind of input this is. The following are the possible values:
  
  * ``"text"``: A single-line text field
  * ``"textarea"``: A multi-line text field
  * ``"password"``
  * ``"select"``
  * ``"combo"``
  * ``"checkbox"``: A single checkbox
  * ``"radio"``: A group of radio buttons
  * ``"button"``
  * ``"signature"``: A digital signature field

* ``required`` indicates if the field is required.
* ``read_only`` indicates if the field is read-only.
* ``options`` is, if provided, a list of available options for this field. (Used by radio buttons, for example)

This information should help you build the JSON which can be provided to the ``fill-form`` command.

--------------
Filling a Form
--------------

To fill the form, use the following command: 

.. code-block:: shell

    python3 -m pdform fill-form path/to/form.pdf '{json data}' path/to/output.pdf


.. note::

    The output path can be omitted to output directly to stout. However, the template PDF must be a real file.

The command expects JSON data similar to the following:

.. code-block:: json

    {
        "VA9[0].#subform[0].TextField1[0]": "Bob Smith",
        "VA9[0].#subform[0].JF01[0]": True,
        "VA9[0].#subform[0].RadioButtonList[0]": "/3",
        "F[0].#subform[13].Digital_Signature[1]": "/path/to/signature.png"
    }

The keys for this JSON are the qualified names of the field. The allowed values will depend on the input type.

* ``"text"``: Accepts strings. The string should not contain newlines.
* ``"textarea"``: Accepts strings. The string will be wrapped automatically, but you may also include manual newlines if you wish.
* ``"password"``
* ``"select"``
* ``"combo"``
* ``"checkbox"``: Accepts either a boolean, or any of the values in the ``options`` array.
* ``"radio"``: Accepts any value from the ``options`` array.
* ``"button"``
* ``"signature"``: Accepts a string, which whould be a path pointing to an image file.

.. note::

    Filling a form does not actually populate signature fields; it merely stamps an image on top. This library does not handle true signatures, which require cryptographic keys.

If your form contains space for a signature, but does not actually use a real signature field, you can still stamp the signature by adding a special ``".stamps"`` key to your JSON:

.. code-block:: json

    {
        ".stamps": [
            {
                "img": "/path/to/img.png",
                "page": 3,
                "rect": [303, 30, 504, 59]
            }
        ]
    }

The stamps array contains objects with the following properties:

* ``img``: The path to the image to stamp.
* ``page``: The page number the stamp should be applied to (pages start at 1).
* ``rect``: The on-screen rectangle coodinates where the image should be stamped, expressed as ``[left, bottom, right, top]``. 

.. tip::

    The units in PDF documents are :dfn:`points`, and are measured from the bottom and left sides of the page. A point is typically considered to be :math:`\frac{1}{72}` in, or about 0.35 mm. This comes out to 9 pt per :math:`\frac{1}{8}` in, or about 28 pt per cm. 
    
    One way to get a good measurement is to set your PDF viewer to "Actual Size" and measure on the screen with a ruler. Some fine-tuning may still be required afterward, as the typical units on a ruler are much coarser than points, but it should get you close.

