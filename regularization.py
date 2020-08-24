import math

from enum import Enum

class Regularization(Enum):
    # Inverse Quadratic is 1 / (reg * length + 1)
    INVERSE_QUADRATIC = 1
    # The curve this represents starts out as a line with slope 1,
    # transitions to a circle, then flattens out at the cap value
    # The second derivative might be a problem here, as the models
    # this produces have noticeable kinks.
    CAPPED_LINEAR = 2
    # The base function will be
    #   (0.5x - y)^2 - (0.5x)^2 = 1
    # This goes to 0 as you go to the left and has a slope of 1 as you
    #   go up and to the right
    # Rearranged:
    #   (0.5x - y)^2 = 1 + 0.25x^2
    #   0.5x - y = - sqrt(1 + 0.25x^2)     # note the branch chosen
    #   y = 0.5x + sqrt(1 + 0.25x^2)
    # This can be translated or stretched as needed.
    HYPERBOLIC = 3
    LOGISTIC = 4


def add_regularization_args(parser):
    parser.add_argument('--regularization_method', default=Regularization.INVERSE_QUADRATIC,
                        type=lambda x: Regularization[x.upper()],
                        help='How to regularize.  Options are {}'.format(i.name for i in Regularization))
    parser.add_argument('--regularization_linear_cap', default=10.0, type=float,
                        help='Limit for the capped linear regularization method')
    parser.add_argument('--regularization', default=0.0, type=float,
                        help='A lot of interesting shapes get long lobes.  This can help smooth them out')
    parser.add_argument('--y_regularization', default=0.0, type=float,
                        help='A lot of interesting shapes get long lobes.  This can help smooth them out - y direction only')
    parser.add_argument('--regularization_radius', default=1.0, type=float,
                        help='Minimum distance from the origin to start applying regularization')
    parser.add_argument('--regularization_x_trans', default=0.0, type=float,
                        help='Amount to translate the hyperbolic regularization on the x axis')
    parser.add_argument('--regularization_y_trans', default=0.0, type=float,
                        help='Amount to translate the hyperbolic regularization on the y axis')
    parser.add_argument('--regularization_x_scale', default=1.0, type=float,
                        help='Amount to scale the hyperbolic regularization on the x axis')
    parser.add_argument('--regularization_y_scale', default=1.0, type=float,
                        help='Amount to scale the hyperbolic regularization on the y axis')
    parser.add_argument('--regularization_slope', default=1.0, type=float,
                        help='Slope for the hyperbolic regularization')

def radial_reg_factor(regularization, regularization_radius):
    def factor(length):
        if length < regularization_radius:
            length = 0
        else:
            length = length - regularization_radius
        reg = 1 / (regularization * length + 1)
        return reg
    return factor

def capped_linear_factor(reg_args):
    cap = reg_args.regularization_linear_cap
    cap_begin = cap * math.sqrt(2)
    linear_end = cap_begin / 2
    def factor(length):
        if length >= cap_begin:
            return cap / length
        elif length <= linear_end:
            return 1.0
        else:
            remainder = cap_begin - length
            return math.sqrt(cap * cap - remainder * remainder) / length
    return factor

def hyperbolic_function_string(reg_args):
    x_trans = reg_args.regularization_x_trans
    y_trans = reg_args.regularization_y_trans
    slope = reg_args.regularization_slope
    inv_slope_sq = 1 / (slope * slope)

    # y = 0.5x + sqrt(1 + 0.25x^2)
    if x_trans == 0:
        x_trans_str = "x"
    elif x_trans > 0:
        x_trans_str = "(x - {})".format(x_trans)
    else:
        x_trans_str = "(x + {})".format(-x_trans)
    if y_trans == 0:
        y_trans_str = ""
    elif y_trans > 0:
        y_trans_str = " + {}".format(y_trans)
    else:
        y_trans_str = " - {}".format(-y_trans)
    if slope == 1:
        slope_str = ""
    else:
        slope_str = str(slope) + " "
        
    return ("Hyperbolic regularization: y = %s(0.5 %s + (%s + 0.25 %s^{2})^{0.5})%s" %
            (slope_str, x_trans_str, str(inv_slope_sq), x_trans_str, y_trans_str))
    

def hyperbolic_factor(reg_args):
    x_trans = reg_args.regularization_x_trans
    y_trans = reg_args.regularization_y_trans
    slope = reg_args.regularization_slope
    inv_slope_sq = 1 / (slope * slope)

    # note that this method will not handle things that go through the origin
    def factor(length):
        x = length - x_trans
        y = slope * (0.5 * x + math.sqrt(inv_slope_sq + 0.25 * x * x))
        y = y + y_trans
        return y / length

    return factor

def logistic_function_string(reg_args):
    x_trans = reg_args.regularization_x_trans
    y_trans = reg_args.regularization_y_trans
    x_scale = reg_args.regularization_x_scale
    y_scale = reg_args.regularization_y_scale

    if x_scale == 0:
        x_str = ""
    elif x_scale == 1:
        x_str = "-x"
    elif x_scale > 0:
        x_str = "-{}x".format(x_scale)
    elif x_scale == -1:
        x_str = "x"
    else:
        x_str = "{}x".format(-x_scale)

    if x_trans > 0:
        x_str = "{} + {}".format(x_str, x_trans)
    elif x_trans < 0:
        x_str = "{} - {}".format(x_str, -x_trans)

    if y_trans == 0:
        y_trans_str = ""
    elif y_trans > 0:
        y_trans_str = "+ {}".format(y_trans)
    else:
        y_trans_str = "- {}".format(-y_trans)

    if y_scale == 1:
        y_scale_str = ""
    else:
        y_scale_str = "{} ".format(y_scale)

    return ("Logistic regularization: y = %s(1 / (1 + e^{%s}))%s" %
            (y_scale_str, x_str, y_trans_str))

def logistic_factor(reg_args):
    x_trans = reg_args.regularization_x_trans
    y_trans = reg_args.regularization_y_trans
    x_scale = reg_args.regularization_x_scale
    y_scale = reg_args.regularization_y_scale

    def factor(length):
        x = x_scale * length - x_trans
        y = 1 / (1 + math.exp(-x))
        y = y_scale * y + y_trans
        return y / length

    return factor

def regularized_function(f1_t, f2_t, factor):
    def reg_f_t(time_step):
        x = f1_t(time_step)
        y = f2_t(time_step)
        length = math.sqrt(x * x + y * y)
        return x * factor(length)
    return reg_f_t

def regularize(x_t, y_t, reg_args):
    if reg_args.regularization_method is Regularization.INVERSE_QUADRATIC:
        regularization_radius = reg_args.regularization_radius
        regularization = reg_args.regularization
        reg_x_t = regularized_function(x_t, y_t, radial_reg_factor(regularization, regularization_radius))
        regularization = reg_args.regularization + reg_args.y_regularization
        reg_y_t = regularized_function(y_t, x_t, radial_reg_factor(regularization, regularization_radius))
    elif reg_args.regularization_method is Regularization.CAPPED_LINEAR:
        factor = capped_linear_factor(reg_args)
        reg_x_t = regularized_function(x_t, y_t, factor)
        reg_y_t = regularized_function(y_t, x_t, factor)
    elif reg_args.regularization_method is Regularization.HYPERBOLIC:
        print(hyperbolic_function_string(reg_args))
        factor = hyperbolic_factor(reg_args)
        reg_x_t = regularized_function(x_t, y_t, factor)
        reg_y_t = regularized_function(y_t, x_t, factor)
    elif reg_args.regularization_method is Regularization.LOGISTIC:
        print(logistic_function_string(reg_args))
        factor = logistic_factor(reg_args)
        reg_x_t = regularized_function(x_t, y_t, factor)
        reg_y_t = regularized_function(y_t, x_t, factor)
    else:
        raise ValueError("Regularization method {} not implemented".reg_args.regularization_method)

    return reg_x_t, reg_y_t
