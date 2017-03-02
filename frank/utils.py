"""Random utilities"""


import datetime


def date_parses(date_str, date_format):
    """\
    Returns True or False depending on whether the string matches the format.
    """
    try:
        datetime.datetime.strptime(date_str, date_format)
    except ValueError:
        return False
    else:
        return True
