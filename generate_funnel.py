import argparse
import math

import marble_path

"""
roughly speaking, want it to go from 2.7cm to 11.7cm over the course of 3cm

for example, a graph of

(4.5 / (1 + e^(-3x-17))) + 1.35

the inner wall should actually be 23mm at the point where the marble
drops down, then expanding back out to 27mm.  this guarantees that the
marbles can drop down without hitting the top of the piece below.

(4.7 / (1 + e^(-3x-17))) + 1.15

Expectation: will go from y=0mm to y=80mm

so t will go from 0 to 8


the outer wall should be 2mm away from this.  can do that via normals
the dumbest possible way would simply be to move it 2mm down and out,
but that may be good enough

(4.7 / (1 + e^(-3x-16.4))) + 1.35

slightly less may also be fine

(4.7 / (1 + e^(-3x-16.55))) + 1.35

"""

def inner_function_x(t):
    """
    Tries to blend 27mm at the connection with a logistic function to represent the funnel
    """    
    if t < 2:
        return 13.55
    if t < 3:
        offset = t - 2
        offset = offset ** 3
        return 13.55 * (1 - offset) + offset * (11.5 + 47 / (1 + math.exp(-3 * t + 17)))
    return 11.5 + 47 / (1 + math.exp(-3 * t + 17))

def inner_function_z(t):
    return t * 10

def outer_function_x(t):
    """
    the inner x, moved slightly away to hopefully make the walls 2mm thick

    14.5+\frac{47}{\left(1+e^{-3x+16.55}\right)}
    """
    return 14.75 + 46.75 / (1 + math.exp(-3 * t + 16.55))

def outer_function_z(t):
    return t * 10
    

def build_f_t_u(num_t_steps, num_u_steps):
    """
    over the course of num_t_steps, go from t=0 to t=7.5 in the above functions
    over the course of num_u_steps, go from 0 to 360 degrees
    """
    def f_xyz(time_t, time_u, outer):
        t = time_t / num_t_steps * 7.5
        time_u = time_u % num_u_steps
        u = time_u * math.pi * 2 / num_u_steps

        if outer:
            x = outer_function_x(t)
            z = outer_function_z(t)
        else:
            x = inner_function_x(t)
            z = inner_function_z(t)

        y = x * math.sin(u)
        x = x * math.cos(u)

        return x, y, z

    return f_xyz

def generate_funnel():
    num_t_steps = 75
    num_u_steps = 120
    f_xyz = build_f_t_u(num_t_steps, num_u_steps)

    for t in range(num_t_steps):
        for u in range(num_u_steps):
            BL = f_xyz(  t,   u, True)
            BR = f_xyz(  t, u+1, True)
            TL = f_xyz(t+1,   u, True)
            TR = f_xyz(t+1, u+1, True)

            yield (BL, BR, TR)
            yield (TR, TL, BL)

    for t in range(num_t_steps):
        for u in range(num_u_steps):
            BL = f_xyz(  t,   u, False)
            BR = f_xyz(  t, u+1, False)
            TL = f_xyz(t+1,   u, False)
            TR = f_xyz(t+1, u+1, False)

            yield (BR, BL, TR)
            yield (TL, TR, BL)

    for u in range(num_u_steps):
        IL = f_xyz(0,   u, False)
        IR = f_xyz(0, u+1, False)
        OL = f_xyz(0,   u, True)
        OR = f_xyz(0, u+1, True)

        yield (IL, IR, OR)
        yield (OR, OL, IL)

    for u in range(num_u_steps):
        IL = f_xyz(num_t_steps,   u, False)
        IR = f_xyz(num_t_steps, u+1, False)
        OL = f_xyz(num_t_steps,   u, True)
        OR = f_xyz(num_t_steps, u+1, True)

        yield (IR, IL, OL)
        yield (OL, OR, IR)

marble_path.write_stl(generate_funnel(), "funnel.stl")
