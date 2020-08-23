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
    parser.add_argument('--regularization_slope', default=1.0, type=float,
                        help='Slope for the hyperbolic regularization')

def radial_reg(x, y, regularization, regularization_radius):
    length = (x ** 2 + y ** 2) ** 0.5
    if length < regularization_radius:
        length = 0
    else:
        length = length - regularization_radius
    reg = 1 / (regularization * length + 1)
    return reg
    
def radial_reg_x_t(x_t, y_t, reg_args):
    regularization = reg_args.regularization
    regularization_radius = reg_args.regularization_radius
    def reg_x_t(time_step):
        x = x_t(time_step)
        y = y_t(time_step)

        reg = radial_reg(x, y, regularization, regularization_radius)
        return x * reg
    return reg_x_t

def radial_reg_y_t(x_t, y_t, reg_args):
    regularization = reg_args.regularization + reg_args.y_regularization
    regularization_radius = reg_args.regularization_radius
    def reg_y_t(time_step):
        x = x_t(time_step)
        y = y_t(time_step)

        reg = radial_reg(x, y, regularization, regularization_radius)
        return y * reg

    return reg_y_t

def capped_linear_factor(cap):
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

def capped_linear_x_t(x_t, y_t, reg_args):
    factor = capped_linear_factor(reg_args.regularization_linear_cap)
    def reg_x_t(time_step):
        x = x_t(time_step)
        y = y_t(time_step)
        length = math.sqrt(x * x + y * y)
        return x * factor(length)
    return reg_x_t

def capped_linear_y_t(x_t, y_t, reg_args):
    factor = capped_linear_factor(reg_args.regularization_linear_cap)
    def reg_y_t(time_step):
        x = x_t(time_step)
        y = y_t(time_step)
        length = math.sqrt(x * x + y * y)
        return y * factor(length)
    return reg_y_t

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

# TODO: use a closure
def hyperbolic_x_t(x_t, y_t, reg_args):
    factor = hyperbolic_factor(reg_args)
    def reg_x_t(time_step):
        x = x_t(time_step)
        y = y_t(time_step)
        length = math.sqrt(x * x + y * y)
        return x * factor(length)
    return reg_x_t

def hyperbolic_y_t(x_t, y_t, reg_args):
    factor = hyperbolic_factor(reg_args)
    def reg_y_t(time_step):
        x = x_t(time_step)
        y = y_t(time_step)
        length = math.sqrt(x * x + y * y)
        return y * factor(length)
    return reg_y_t

def regularize(x_t, y_t, reg_args):
    if reg_args.regularization_method is Regularization.INVERSE_QUADRATIC:
        reg_x_t = radial_reg_x_t(x_t, y_t, reg_args)
        reg_y_t = radial_reg_y_t(x_t, y_t, reg_args)
    elif reg_args.regularization_method is Regularization.CAPPED_LINEAR:
        reg_x_t = capped_linear_x_t(x_t, y_t, reg_args)
        reg_y_t = capped_linear_y_t(x_t, y_t, reg_args)
    elif reg_args.regularization_method is Regularization.HYPERBOLIC:
        print(hyperbolic_function_string(reg_args))
        reg_x_t = hyperbolic_x_t(x_t, y_t, reg_args)
        reg_y_t = hyperbolic_y_t(x_t, y_t, reg_args)
    else:
        raise ValueError("Regularization method {} not implemented".reg_args.regularization_method)

    return reg_x_t, reg_y_t
