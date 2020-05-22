def add_regularization_args(parser):
    parser.add_argument('--regularization', default=0.0, type=float,
                        help='A lot of interesting shapes get long lobes.  This can help smooth them out')
    parser.add_argument('--y_regularization', default=0.0, type=float,
                        help='A lot of interesting shapes get long lobes.  This can help smooth them out - y direction only')
    parser.add_argument('--regularization_radius', default=1.0, type=float,
                        help='Minimum distance from the origin to start applying regularization')
    
def radial_reg_x_t(x_t, y_t, reg_args):
    regularization = reg_args.regularization
    regularization_radius = reg_args.regularization_radius
    def reg_x_t(time_step):
        x = x_t(time_step)
        y = y_t(time_step)

        length = (x ** 2 + y ** 2) ** 0.5
        if length < regularization_radius:
            length = 0
        else:
            length = length - regularization_radius
        reg = 1 / (regularization * length + 1)
        return x * reg
    return reg_x_t

def radial_reg_y_t(x_t, y_t, reg_args):
    regularization = reg_args.regularization + reg_args.y_regularization
    regularization_radius = reg_args.regularization_radius
    def reg_y_t(time_step):
        x = x_t(time_step)
        y = y_t(time_step)

        length = (x ** 2 + y ** 2) ** 0.5
        if length < regularization_radius:
            length = 0
        else:
            length = length - regularization_radius
        reg = 1 / (regularization * length + 1)
        return y * reg

    return reg_y_t
