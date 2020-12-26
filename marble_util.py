import ast

def parse_tuple_tuple(arg, name):
    overlap_tuple = ast.literal_eval(arg)
    if (isinstance(overlap_tuple, (tuple, list)) and len(overlap_tuple) == 2 and
        isinstance(overlap_tuple[0], (int, float)) and isinstance(overlap_tuple[1], (int, float))):
        overlap_tuple = (tuple(overlap_tuple),)
    for i in overlap_tuple:
        if (len(i) != 2 or
            not isinstance(i[0], (int, float)) or
            not isinstance(i[1], (int, float))):
            raise ValueError('Need a tuple of len 2 tuples for %s' % name)
    return overlap_tuple

def parse_float_or_tuple_tuple(arg, name):
    overlap_tuple = ast.literal_eval(arg)
    if isinstance(overlap_tuple, (float, int)):
        return overlap_tuple
    if (isinstance(overlap_tuple, (tuple, list)) and len(overlap_tuple) == 2 and
        isinstance(overlap_tuple[0], (int, float)) and isinstance(overlap_tuple[1], (int, float))):
        overlap_tuple = (tuple(overlap_tuple),)
    for i in overlap_tuple:
        if (len(i) != 2 or
            not isinstance(i[0], (int, float)) or
            not isinstance(i[1], (int, float))):
            raise ValueError('Need a float or a tuple of len 2 tuples for %s' % name)
    return overlap_tuple

def get_time_step(times, t):
    """
    Given a list mapping time step to actual t, return the time step closest to the desired t
    """
    # TODO: implement binary search?
    if times[0] > t:
        return 0
    if times[-1] < t:
        return len(times) - 1
    for i in range(len(times)):
        if times[i] <= t and times[i+1] > t:
            return i
    raise AssertionError("Oops")

def simplify_float_to_string(value, decimals=8):
    template = "%." + str(decimals) + "f"
    result = template % value
    result = result.rstrip("0").rstrip(".")
    return result

def simplify_integer_ratio(numerator, denominator):
    if denominator == numerator:
        return ""
    elif denominator == 1:
        return "%s" % numerator
    else:
        return "(%s/%s)" % (numerator, denominator)

