import ast

def parse_tuple_tuple(arg, name):
    overlap_tuple = ast.literal_eval(arg)
    if (isinstance(overlap_tuple, (tuple, list)) and len(overlap_tuple) == 2 and
        isinstance(overlap_tuple[0], float) and isinstance(overlap_tuple[1], float)):
        overlap_tuple = (tuple(overlap_tuple),)
    for i in overlap_tuple:
        if len(i) != 2:
            raise ValueError('Need a tuple of len 2 tuples for %s' % name)
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

