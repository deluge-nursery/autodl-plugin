# -*- coding: utf-8 -*-
import math


def string_compare(a, b):
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def convert_string_to_bool(s):
    s = s.lower()
    return not (s == 'false' or s == 'off' or s == 'no' or s == '0')


def convert_string_to_number(value_str, default_value, min_value=None, max_value=None):
    value = float(value_str)
    if math.isnan(value):
        value = default_value
    elif value is None:
        return value
    elif value < min_value:
        value = min_value
    elif value > max_value:
        value = max_value
    return value


def convert_string_to_integer(value_str, default_value, min_value=None, max_value=None):
    return math.floor(convert_string_to_number(value_str, default_value, min_value, max_value))
