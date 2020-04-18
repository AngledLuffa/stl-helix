"""
Has a method to extend a function in the direction of the derivative at the endpoints given.
"""

def build_extension(base_f_t, t0):
    epsilon = 0.001
    f0 = base_f_t(t0)
    derivative = (base_f_t(t0 + epsilon) - base_f_t(t0 - epsilon)) / (epsilon * 2)
    print("Extenstion at %.4f.  Derivative %.4f f0 %.4f" % (t0, derivative, f0))
    def extension_t(t):
        return f0 + derivative * (t - t0)
    return extension_t

def extend_f_t(time_t, base_f_t, start_t, end_t, extra_start_t, extra_end_t):
    begin_f_t = build_extension(base_f_t, start_t)
    end_f_t = build_extension(base_f_t, end_t)
    
    def x_t(time_step):
        t = time_t(time_step)
        if extra_start_t and t < start_t:
            return begin_f_t(t)
        elif extra_end_t and t > end_t:
            return end_f_t(t)
        else:
            return base_f_t(t)

    return x_t

