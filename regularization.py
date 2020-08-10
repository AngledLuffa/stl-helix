from enum import Enum

class Regularization(Enum):
    INVERSE_QUADRATIC = 1


def add_regularization_args(parser):
    parser.add_argument('--regularization_method', default=Regularization.INVERSE_QUADRATIC,
                        type=lambda x: Regularization[x.upper()],
                        help='How to regularize.  Options are {}'.format(i.name for i in Regularization))
    parser.add_argument('--regularization', default=0.0, type=float,
                        help='A lot of interesting shapes get long lobes.  This can help smooth them out')
    parser.add_argument('--y_regularization', default=0.0, type=float,
                        help='A lot of interesting shapes get long lobes.  This can help smooth them out - y direction only')
    parser.add_argument('--regularization_radius', default=1.0, type=float,
                        help='Minimum distance from the origin to start applying regularization')

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

def regularize(x_t, y_t, reg_args):
    if reg_args.regularization_method is Regularization.INVERSE_QUADRATIC:
        reg_x_t = radial_reg_x_t(x_t, y_t, reg_args)
        reg_y_t = radial_reg_y_t(x_t, y_t, reg_args)
        return reg_x_t, reg_y_t
    raise ValueError("Regularization method {} not implemented".reg_args.regularization_method)
