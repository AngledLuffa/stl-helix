def append_functions(x1_t, y1_t, slope1_t, r1_t,
                     x2_t, y2_t, slope2_t, r2_t,
                     inflection_t):
    """
    Combine two x, y, slope, r functions into one function

    Second function will be offset in x&y so it matches the first function at inflection_t.

    Slope is assumed to not need that offset.

    r_t must be combined as the "arclength" manner of generating it
    will have a very noticeable discontinuity at inflection_t otherwise
    """
    x_off = x1_t(inflection_t) - x2_t(0)
    y_off = y1_t(inflection_t) - y2_t(0)
    def x_t(t):
        if t < inflection_t:
            return x1_t(t)
        else:
            return x2_t(t - inflection_t) + x_off

    def y_t(t):
        if t < inflection_t:
            return y1_t(t)
        else:
            return y2_t(t - inflection_t) + y_off

    def slope_t(t):
        if t < inflection_t:
            return slope1_t(t)
        else:
            return slope2_t(t - inflection_t)

    def r_t(t):
        if t < inflection_t:
            return r1_t(t)
        else:
            return r2_t(t - inflection_t)
        
    return x_t, y_t, slope_t, r_t

