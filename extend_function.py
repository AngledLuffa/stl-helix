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

def extend_f_t(time_t, base_f_t, start_t, end_t, extension_args):
    begin_f_t = build_extension(base_f_t, start_t)
    end_f_t = build_extension(base_f_t, end_t)

    extra_t = extension_args.extra_t
    if extra_t is None:
        extra_start_t = extension_args.extra_start_t
        extra_end_t = extension_args.extra_end_t
    else:
        if (extension_args.extra_start_t is not None and
            extension_args.extra_t != extension_args.extra_start_t):
            raise ValueError("extra_start_t and extra_t both set, but do not agree")
        if (extension_args.extra_end_t is not None and
            extension_args.extra_t != extension_args.extra_end_t):
            raise ValueError("extra_end_t and extra_t both set, but do not agree")
        extra_start_t = extra_t
        extra_end_t = extra_t

    def f_t(time_step):
        t = time_t(time_step)
        if extra_start_t and t < start_t:
            return begin_f_t(t)
        elif extra_end_t and t > end_t:
            return end_f_t(t)
        else:
            return base_f_t(t)

    return f_t

def add_extend_args(parser, default_extra_t=None):
    parser.add_argument('--extra_t', default=default_extra_t, type=float,
                        help='Extra time to build the model as a straight line before & after the domain')
    parser.add_argument('--extra_start_t', default=None, type=float,
                        help='Extra time to build the model as a straight line before the domain')
    parser.add_argument('--extra_end_t', default=None, type=float,
                        help='Extra time to build the model as a straight line after the domain')

