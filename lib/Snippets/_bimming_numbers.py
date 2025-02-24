# -*- coding: utf-8 -*-

# Imports
#==================================================
from Autodesk.Revit.DB import *
import random
import math
from decimal import Decimal, getcontext, ROUND_HALF_UP
from Snippets._bimming_convert import *
from Autodesk.Revit.DB import *
from pyrevit import forms
from collections import defaultdict
# Variables
#==================================================
app   = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type:Document

# Functions
#==================================================

def count_decimals_string(string):
    """
    Counts the number of decimal places in a given numeric string.

    Args:
        string (str or float): A number represented as a string or float.

    Returns:
        int: The number of decimal places.
    """
    # Convert the float to a Decimal
    decimal_number = Decimal(str(string)).normalize()  # normalize() removes trailing zeros
    # This expression calculates the number of decimal places in a Decimal number.
    # - decimal_number.as_tuple().exponent: Retrieves the exponent of the Decimal number,
    #   which indicates the position of the decimal point relative to the integer part.
    # - The negative sign (-) reverses the exponent to give the count of decimal places.
    # - max(0, ...): Ensures that the result is non-negative, returning 0 if the number has no decimal part.
    number_of_decimals = max(0, -decimal_number.as_tuple().exponent)
    return number_of_decimals

def custom_round(value, precision='0.000000000005', rounding=ROUND_HALF_UP):
    """
    Rounds a given value to the nearest specified precision using Decimal.

    Args:
        value (float or str): The value to be rounded.
        precision (str, optional): The rounding step (default: 0.000000000005).
        rounding (ROUNDING, optional): Rounding mode (default: ROUND_HALF_UP).

    Returns:
        Decimal: The rounded value.
    """
    # Convert to Decimal for precision
    decimal_value = Decimal(value)

    # Define the quantization step (0.0001, to control 4th decimal place)
    step = Decimal(precision)

    # Quantize the value to the nearest 0.0005
    rounded_value = (decimal_value / step).quantize(Decimal('1'), rounding) * step
    return rounded_value


def scaled_decimal(value, n):
    """
    Converts an integer input into a decimal number following a specific pattern.

    The function returns `value / 10^n`, which results in:
    - `scaled_decimal(5, 2)` → `0.05`
    - `scaled_decimal(5, 4)` → `0.0005`
    - `scaled_decimal(10, 3)` → `0.01`

    Args:
        value (int or Decimal): The numerator of the fraction.
        n (int): The scaling factor for the decimal output.

    Returns:
        Decimal: The computed decimal value.
    """
    return Decimal(value) / (10 ** n)