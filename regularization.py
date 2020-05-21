def radial_reg_x_t(x_t, y_t, regularization):
    def reg_x_t(time_step):
        x = x_t(time_step)
        y = y_t(time_step)

        length = (x ** 2 + y ** 2) ** 0.5
        if length < 1:
            length = 0
        else:
            length = length - 1
        reg = 1 / (regularization * length + 1)
        return x * reg
    return reg_x_t

def radial_reg_y_t(x_t, y_t, regularization):
    def reg_y_t(time_step):
        x = x_t(time_step)
        y = y_t(time_step)

        length = (x ** 2 + y ** 2) ** 0.5
        if length < 1:
            length = 0
        else:
            length = length - 1
        reg = 1 / (regularization * length + 1)
        return y * reg

    return reg_y_t
