import argparse
import math

from enum import Enum

import build_shape
import combine_functions
import generate_helix
import marble_path
import regularization
import slope_function

"""
Generates a hypotrochoid, a curve on a circle defined by 3 parameters.

x(t) = ((A - B) * math.cos(t) + C * math.cos((A - B) * t / B))
y(t) = ((A - B) * math.sin(t) - C * math.sin((A - B) * t / B))

Also has an option for generating an epitrochoid instead.

x(t) = ((A - B) * math.cos(t) + C * math.cos((A - B) * t / B))
y(t) = ((A - B) * math.sin(t) - C * math.sin((A - B) * t / B))


to make a 3 lobed flower:
------------------------
this is the ramp
python generate_hypotrochoid.py --hypoA 9 --hypoB 3 --hypoC 6 --start_t 1.0472 --scale 6  --tube_end_angle 240 --slope_angle 12

problem: the ramp has some obvious kinks in the corners
so we can add some regularization
python generate_hypotrochoid.py --hypoA 9 --hypoB 3 --hypoC 6 --start_t 1.0472 --scale 10  --tube_end_angle 240 --slope_angle 12 --regularization 0.07

complete circle tube.  chop everything except the middle.  this produces the tunnels through the post
python generate_hypotrochoid.py --hypoA 9 --hypoB 3 --hypoC 6 --start_t 1.0472 --scale 10  --tube_end_angle 360 --slope_angle 12 --regularization 0.07

make this a hole, use it for the negative space in the post
python generate_hypotrochoid.py --hypoA 9 --hypoB 3 --hypoC 6 --start_t 1.0472 --scale 10  --tube_end_angle 360 --slope_angle 12 --regularization 0.07  --tube_radius 10.5 --wall_thickness 11


angle is, not surprisingly, about 60 on the upper connection



Inside out flower, two leaves:
-----------------------------

Tube
python generate_hypotrochoid.py --hypoA 4 --hypoB 6 --hypoC 2 --slope_angle 4 --scale 14 --start_t  0 --tube_method ELLIPSE --tube_start_angle -60 --overlaps "(7.0686, 11.7810)" --overlap_separation 25

Put this at 0, 0, 18
Angle is 56

Tunnels
If you put the tunnel from start_t 0 end_t 18.8496 you get top & bottom tunnels you don't want.
Start from start_t=2, piece is 77.17 tall.  
Go from start_t=2 end_t 16, piece is 72.41 tall.
Difference: 4.76
python generate_hypotrochoid.py --hypoA 4 --hypoB 6 --hypoC 2 --slope_angle 4 --scale 14 --start_t  6 --end_t 12 --tube_method ELLIPSE --tube_end_angle 360 --overlaps "(7.0686, 11.7810)" --overlap_separation 25

Put this 0, 0, 22.76

Holes
python generate_hypotrochoid.py --hypoA 4 --hypoB 6 --hypoC 2 --slope_angle 4 --scale 14 --start_t  0 --tube_method ELLIPSE --tube_end_angle 360 --tube_radius 10.5 --wall_thickness 11  --overlaps "(7.0686, 11.7810)" --overlap_separation 25

ramp out: 12 tilt, 63 rotate

Four lobed outside flower
-----

python generate_hypotrochoid.py --hypoA 12 --hypoB 3 --hypoC 6 --slope_angle 3 --tube_method OVAL --tube_wall_height 7 --closest_approach 26 --regularization 0.05 --overlap_separation 23 --overlaps "((0.9117, 2.2299),(2.4825, 3.8007),(4.0533, 5.3715),(5.6241, 6.9423))" --zero_circle --start_t 0.8854 --end_t 6.9886

put this at 0,0,18
post goes at 81.15,81.15,0
rotate post 55 degrees

python generate_hypotrochoid.py --hypoA 12 --hypoB 3 --hypoC 6 --slope_angle 3 --tube_method ELLIPSE --tube_radius 10.5 --wall_thickness 11 --closest_approach 26 --regularization 0.05 --overlap_separation 23 --overlaps "((0.9117, 2.2299),(2.4825, 3.8007),(4.0533, 5.3715),(5.6241, 6.9423))" --zero_circle --start_t 0.8854 --end_t 6.9886 --tube_start_angle 0 --tube_end_angle 360

Five lobed outside flower
-------------------------

 the reg radius is needed to avoid a possible bend in the path
 This looks kind of stretched, but Logan likes it
python generate_hypotrochoid.py --hypoA 15 --hypoB 6 --hypoC 8.2 --tube_method oval --tube_wall_height 6 --slope_angle 3 --closest_approach 26 --regularization 0.27 --overlap_separation 25 --overlaps "((1.382,3.644),(3.895,6.157),(6.409,8.671),(8.922,11.184),(11.435,13.697))" --start_t 1.3066 --end_t 13.7730 --num_time_steps 400 --regularization_radius 0.3 --rebalance_time --zero_circle 

needs the 200 long post
91.813, 106.097

 hole for the on/off:
python generate_hypotrochoid.py --hypoA 15 --hypoB 6 --hypoC 8.2 --slope_angle 3 --closest_approach 26 --regularization 0.27 --overlap_separation 25 --overlaps "((1.382,3.644),(3.895,6.157),(6.409,8.671),(8.922,11.184),(11.435,13.697))" --start_t 1.3066 --end_t 13.7730 --num_time_steps 400 --regularization_radius 0.3 --rebalance_time --zero_circle  --tube_radius 10.5 --wall_thickness 11 --tube_end_angle 360

Five pointed star
-----------------

start time: 6 pi / 10, end time 6 pi / 10 + 6pi
but the both times are adjusted by .3 to leave room for the start/end circles

python generate_hypotrochoid.py --hypoA 5 --hypoB 3 --hypoC 5 --tube_method oval --tube_wall_height 6 --slope_angle 4.0 --closest_approach 26 --start_t 2.185 --end_t 20.4345 --num_time_steps 400 --rebalance_time --zero_circle --regularization_method LOGISTIC --regularization_x_trans 2.5 --regularization_y_trans -1.0 --regularization_x_scale 0.8 --regularization_y_scale 4.25 --zero_circle

hole for the on/off:
python generate_hypotrochoid.py --hypoA 5 --hypoB 3 --hypoC 5 --tube_method oval --tube_wall_height 6 --slope_angle 4.0 --closest_approach 26 --start_t 2.185 --end_t 20.4345 --num_time_steps 400 --rebalance_time --zero_circle --regularization_method LOGISTIC --regularization_x_trans 2.5 --regularization_y_trans -1.0 --regularization_x_scale 0.8 --regularization_y_scale 4.25 --zero_circle --tube_radius 10.5 --wall_thickness 11 --tube_end_angle 360

100mm post at 75.30, 72.08 with a rotation of 20 degrees

Three leaf inside out flower
----------------------------
This is the original version, but it has a very tight corner where it
is extremely difficult to remove the supports.

x,y,z: 0, 0, 17.04
python generate_hypotrochoid.py --hypoA 3 --hypoB 5 --hypoC 2 --slope_angle 4 --scale 15 --start_t  0 --tube_method ELLIPSE --tube_start_angle -60 --overlaps "((8.2279,12.7160),(18.6995,23.188))" --overlap_separation 26

tunnels through the pole:
x,y,z: 0, 0, 19.13
python generate_hypotrochoid.py --hypoA 3 --hypoB 5 --hypoC 2 --slope_angle 4 --scale 15 --start_t  1.5 --end_t 30 --tube_method ELLIPSE --tube_start_angle -180 --overlaps "((8.2279,12.7160),(18.6995,23.188))" --overlap_separation 26
then remove everything outside the pole

holes for the crossings, the on ramp, and the off ramp:
x,y,z: 2, 2, 19.04
python generate_hypotrochoid.py --hypoA 3 --hypoB 5 --hypoC 2 --slope_angle 4 --scale 15 --start_t  0 --tube_method ELLIPSE --tube_start_angle -180 --overlaps "((8.2279,12.7160),(18.6995,23.188))" --overlap_separation 26 --tube_radius 10.5 --wall_thickness 11

rotation on the out post: roughly 62 degrees

Here is a redo with a triangular roof in the center holes.  This hopefully means no supports are needed.

ramp:
x,y,z: 0, 0, 16
python generate_hypotrochoid.py --hypoA 3 --hypoB 5 --hypoC 2 --slope_angle 4 --scale 15 --start_t  0 --tube_method ELLIPSE --tube_start_angle -60 --overlaps "((8.2279,12.7160),(18.6995,23.188))" --overlap_separation 27

tunnels through the pole:
x,y,z: 0, 0, 18.827
python generate_hypotrochoid.py --hypoA 3 --hypoB 5 --hypoC 2 --slope_angle 4 --scale 15 --start_t  1.885 --end_t 29.531 --num_time_steps 220 --tube_method TRIANGLE_TOP --overlaps "((8.2279,12.7160),(18.6995,23.188))" --overlap_separation 27 --tube_roof_angle 30

holes for the crossings, etc:
x,y,z: 2, 2, 18
python generate_hypotrochoid.py --hypoA 3 --hypoB 5 --hypoC 2 --slope_angle 4 --scale 15 --start_t  0 --tube_method TRIANGLE_TOP --tube_radius 10.5 --wall_thickness 11 --overlaps "((8.2279,12.7160),(18.6995,23.188))" --overlap_separation 27 --tube_roof_angle 30


5 lobed flower:
--------------
this is a solid tube for the links
python generate_hypotrochoid.py --hypoA 5 --hypoB 1 --hypoC 4 --tube_end_angle 360 --slope_angle 7.71 --scale 8.5 --start_t 0.6283 --regularization 0.01

slight regularization is needed to fit in a Dremel 3d40
height is 136.51
put it at x=0,y=0,z=15
the hole in the middle will make it perfect for connecting to the
  previous piece at 150mm up and the next piece at 18mm

cut off the bottom of the tube
python generate_hypotrochoid.py --hypoA 5 --hypoB 1 --hypoC 4 --tube_end_angle 360 --slope_angle 7.71 --scale 8.5 --start_t 0.6283 --end_t 6.2 --regularization 0.01
new height: 123.34
so make z=15+136.51-123.34=28.17
z=28.17

cut off the top of the tube as well
python generate_hypotrochoid.py --hypoA 5 --hypoB 1 --hypoC 4 --tube_end_angle 360 --slope_angle 7.71 --scale 8.5 --start_t 1.2 --end_t 6.2 --regularization 0.01

connector tube will go at x=51.89,y=58.30

actual ramp:
python generate_hypotrochoid.py --hypoA 5 --hypoB 1 --hypoC 4 --tube_end_angle 240 --slope_angle 7.71 --scale 8.5 --start_t 0.6283 --regularization 0.01
this goes at 0,0,15

hole that goes down the middle:
python generate_hypotrochoid.py --hypoA 5 --hypoB 1 --hypoC 4 --tube_end_angle 360 --slope_angle 7.71 --scale 8.5 --start_t 0.6283  --regularization 0.01  --tube_radius 10.5 --wall_thickness 11
this goes at 2,2,17

rotation on post: 36 degrees


Updates for v2:

ramp, at 0,0,15:
python generate_hypotrochoid.py --hypoA 5 --hypoB 1 --hypoC 4 --tube_end_angle 220 --slope_angle 7.71 --scale 8.5 --start_t 0.6283 --regularization 0.01

hole that goes down the middle: 2, 2, 17
python generate_hypotrochoid.py --hypoA 5 --hypoB 1 --hypoC 4 --tube_end_angle 360 --slope_angle 7.71 --scale 8.5 --start_t 0.6283  --regularization 0.01  --tube_radius 10.5 --wall_thickness 11   --tube_method TRIANGLE_TOP --tube_roof_angle 30

tunnels in the middle:
0,0,15 -> 0,0.02,27.156
python generate_hypotrochoid.py --hypoA 5 --hypoB 1 --hypoC 4 --tube_end_angle 360 --slope_angle 7.71 --scale 8.5 --start_t 1.2  --end_t 6.2 --regularization 0.01   --tube_method TRIANGLE_TOP --tube_roof_angle 30
# the triangle tops overlap the bottoms of the tunnels.  this removes the bumps as a hole
python generate_hypotrochoid.py --hypoA 5 --hypoB 1 --hypoC 4 --tube_end_angle 180 --slope_angle 7.71 --scale 8.5 --start_t 0.58  --regularization 0.01  --tube_radius 10.5 --wall_thickness 11

Epitrochoid - Giant piece
-------------------------

# boring
python generate_hypotrochoid.py --hypoA 12 --hypoB 3 --hypoC 3 --slope_angle 3 --tube_method OVAL --tube_wall_height 7 --closest_approach 26 --overlap_separation 23 --start_t 0.0 --trochoid EPITROCHOID

# boring
python generate_hypotrochoid.py --hypoA 15 --hypoB 3 --hypoC 9 --slope_angle 3 --tube_method OVAL --tube_wall_height 7 --closest_approach 26 --overlap_separation 23 --start_t 0.0 --trochoid EPITROCHOID

# 8 loops, 3 times around... huge
python generate_hypotrochoid.py --hypoA 8 --hypoB 3 --hypoC 5 --slope_angle 3 --tube_wall_height 7 --closest_approach 26 --overlap_separation 23 --start_t 0.0 --trochoid EPITROCHOID --overlaps "((1.8912, 2.8212),(4.2474, 5.1774),(6.6036, 7.5336),(8.9598, 9.8898),(11.3160, 12.2460),(13.6722, 14.6022),(16.0284, 16.9584))"

# 7 loops, 3 times around... reasonably tall, but the corners don't work
python generate_hypotrochoid.py --hypoA 7 --hypoB 3 --hypoC 5 --slope_angle 3 --closest_approach 26 --overlap_separation 23 --start_t 0.0 --trochoid EPITROCHOID --overlaps "((2.0528, 3.3328),(4.7456, 6.0256),(7.4384, 8.7184),(10.1312, 11.4112),(12.8240, 14.1040),(15.5168, 16.7968))"

# 7 loops, 2 times around... works
python generate_hypotrochoid.py --hypoA 7 --hypoB 2 --hypoC 5 --slope_angle 3 --closest_approach 26 --overlap_separation 23 --start_t 0.0 --trochoid EPITROCHOID --overlaps "((1.2602, 2.3302),(3.0554, 4.1254),(4.8506, 5.9206),(6.6458, 7.7158),(8.4410, 9.5110),(10.2362, 11.3062))"

# wall
python generate_hypotrochoid.py --hypoA 7 --hypoB 2 --hypoC 5 --slope_angle 3.2 --closest_approach 26 --overlap_separation 23 --trochoid EPITROCHOID --overlaps "((1.2602, 2.3302),(3.0554, 4.1254),(4.8506, 5.9206),(6.6458, 7.7158),(8.4410, 9.5110),(10.2362, 11.3062))" --zero_circle --start_t 0.3 --end_t 12.266 --num_time_steps 800 --output_name epi.stl --tube_start_angle -60 --tube_sides 48

# hole
python generate_hypotrochoid.py --hypoA 7 --hypoB 2 --hypoC 5 --slope_angle 3.2 --closest_approach 26 --overlap_separation 23 --trochoid EPITROCHOID --overlaps "((1.2602, 2.3302),(3.0554, 4.1254),(4.8506, 5.9206),(6.6458, 7.7158),(8.4410, 9.5110),(10.2362, 11.3062))" --zero_circle --start_t 0.3 --end_t 12.266 --num_time_steps 800 --output_name epi_hole.stl --tube_radius 10.5 --wall_thickness 11 --tube_end_angle 360 --tube_sides 48

# tower in the middle goes at 84.74, 87.18.  rotate 36.5 degrees
"""

class Trochoid(Enum):
    HYPOTROCHOID = 1
    EPITROCHOID = 2

def build_time_t(args):
    """
    Return a function which converts discrete times 0..args.num_time_steps to the range
    args.start_t..args_end_t
    """
    def time_t(time_step):
        return args.start_t + time_step * (args.end_t - args.start_t) / args.num_time_steps
    return time_t

def build_reg_f_t(args):
    """
    Using the given args, builds a pair of functions for x & y

    x, y will take time steps and convert them to the correct span before calculating.

    The functions apply regularization to the x & y values.

    Not scaled yet, though.  This is refactored so that the method
    which calculates the scaling can do so
    """
    time_t = build_time_t(args)

    A = args.hypoA
    B = args.hypoB
    C = args.hypoC

    if args.trochoid == Trochoid.HYPOTROCHOID:
        def x_t(time_step):
            t = time_t(time_step)
            return ((A - B) * math.cos(t) + C * math.cos((A - B) * t / B))

        def y_t(time_step):
            t = time_t(time_step)
            return ((A - B) * math.sin(t) - C * math.sin((A - B) * t / B))
    elif args.trochoid == Trochoid.EPITROCHOID:
        def x_t(time_step):
            t = time_t(time_step)
            return ((A + B) * math.cos(t) - C * math.cos((A + B) * t / B))

        def y_t(time_step):
            t = time_t(time_step)
            return ((A + B) * math.sin(t) - C * math.sin((A + B) * t / B))
    else:
        raise ValueError("Unhandled trochoid type: " + args.trochoid)

    regularization.describe_regularization(args)
    reg_x_t, reg_y_t = regularization.regularize(x_t, y_t, args)

    return reg_x_t, reg_y_t

def build_f_t(args):
    reg_x_t, reg_y_t = build_reg_f_t(args)
    
    def scale_x_t(time_step):
        return reg_x_t(time_step) * args.x_scale
    
    def scale_y_t(time_step):
        return reg_y_t(time_step) * args.y_scale

    return scale_x_t, scale_y_t


def rebalance_time(time_t, x_t, y_t, num_time_steps):
    lengths = [((x_t(i) - x_t(i+1)) ** 2 +
                (y_t(i) - y_t(i+1)) ** 2) ** 0.5
               for i in range(num_time_steps)]
    total_length = sum(lengths)
    length_per_tick = total_length / num_time_steps

    tick_mapping = []
    
    current_segment = 0
    leftover_segment = 0.0
    for i in range(num_time_steps):
        tick_mapping.append(current_segment + leftover_segment)
        length_needed = length_per_tick
        if leftover_segment > 0.0:
            if lengths[current_segment] * (1.0 - leftover_segment) > length_per_tick:
                leftover_segment = leftover_segment + length_per_tick / lengths[current_segment]
                continue
            length_needed = length_needed - lengths[current_segment] * (1.0 - leftover_segment)
            current_segment = current_segment + 1
            leftover_segment = 0.0
        # try to avoid precision errors - this can go wrong when there is
        # 0.0001 length needed on the last segment, for example
        while current_segment < num_time_steps and length_needed > lengths[current_segment]:
            length_needed = length_needed - lengths[current_segment]
            current_segment = current_segment + 1
        if current_segment < num_time_steps and length_needed > 0.0:
            leftover_segment = length_needed / lengths[current_segment]
    tick_mapping.append(current_segment + leftover_segment)

    def remap_tick(t):
        if t < -1 or t > num_time_steps + 1:
            raise ValueError("Unable to estimate time {}".format(t))
        if t < 0:
            return (tick_mapping[1] - tick_mapping[0]) * t
        if t > num_time_steps:
            return tick_mapping[num_time_steps] + (tick_mapping[num_time_steps] - tick_mapping[num_time_steps - 1]) * (t - num_time_steps)
        segment = math.floor(t)
        remainder = t - segment
        if remainder == 0:
            return tick_mapping[segment]
        else:
            return tick_mapping[segment] + (tick_mapping[segment+1] - tick_mapping[segment]) * remainder

    def new_time_t(t):
        return time_t(remap_tick(t))
        
    def new_x_t(t):
        return x_t(remap_tick(t))

    def new_y_t(t):
        return y_t(remap_tick(t))

    #print("Time remapping")
    #for i in range(num_time_steps+1):
    #    print(i, tick_mapping[i], new_time_t(i))
    #print("Original functions")
    #for i in range(num_time_steps+1):
    #    print(time_t(i), x_t(i), y_t(i))
    #print("New functions")
    #for i in range(num_time_steps+1):
    #    print(new_time_t(i), new_x_t(i), new_y_t(i))

    return new_time_t, new_x_t, new_y_t

def describe_curve(args):
    A = args.hypoA
    B = args.hypoB
    C = args.hypoC

    if args.trochoid == Trochoid.HYPOTROCHOID:
        AmB = A - B
        print("Generating Hypotrochoid: x(t) = {} cos(t) + {} cos(({} / {}) t)".format(AmB, C, AmB, B))
        print("                         y(t) = {} sin(t) - {} sin(({} / {}) t)".format(AmB, C, AmB, B))
        print("  ({} cos(t) + {} cos(({} / {}) t), {} sin(t) - {} sin(({} / {}) t))".format(AmB, C, AmB, B, AmB, C, AmB, B))
    elif args.trochoid == Trochoid.EPITROCHOID:
        print("Generating Epitrochoid: x(t) = %d cos(t) - %.4f cos((%d / %d) t)" % (A + B, C, A+B, B))
        print("                        y(t) = %d sin(t) - %.4f sin((%d / %d) t)" % (A + B, C, A+B, B))
    else:
        raise ValueError("Unhandled trochoid type: " + args.trochoid)

def generate_hypotrochoid(args):
    describe_curve(args)
    x_t, y_t = build_f_t(args)

    num_time_steps = args.num_time_steps
    time_t = build_time_t(args)
    if args.rebalance_time:
        time_t, x_t, y_t = rebalance_time(time_t, x_t, y_t, num_time_steps)

    slope_angle_t = slope_function.slope_function(x_t=x_t,
                                                  y_t=y_t,
                                                  time_t=time_t,
                                                  slope_angle=args.slope_angle,
                                                  num_time_steps=num_time_steps,
                                                  overlap_args=args,
                                                  kink_args=None)

    r_t = marble_path.numerical_rotation_function(x_t, y_t)
    #for i in range(num_time_steps+1):
    #    print('i, x, y, r: %d %.4f %.4f %.4f' % (i, x_t(i), y_t(i), r_t(i)))

    if args.zero_circle:
        updated_functions = combine_functions.add_both_zero_circles(args=args,
                                                                    num_time_steps=num_time_steps,
                                                                    x_t=x_t,
                                                                    y_t=y_t,
                                                                    slope_angle_t=slope_angle_t,
                                                                    r_t=r_t)
        num_time_steps, x_t, y_t, slope_angle_t, r_t = updated_functions

    z_t = marble_path.arclength_height_function(x_t, y_t, num_time_steps,
                                                slope_angle_t=slope_angle_t)

    build_shape.print_stats(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t, num_time_steps=num_time_steps)

    print("Z goes from %.4f to %.4f" % (z_t(0), z_t(num_time_steps)))
    
    # can calculate dx & dy like this
    # but when adding regularization, that becomes hideous
    #t = time_t(time_step)
    #dx = -(A - B) * math.sin(t) - C * ((A - B) / B) * math.sin((A - B) * t / B)
    #dx = dx * args.x_scale
    #dy =  (A - B) * math.cos(t) - C * ((A - B) / B) * math.cos((A - B) * t / B)
    #dy = dy * args.y_scale

    for triangle in marble_path.generate_path(x_t=x_t, y_t=y_t, z_t=z_t, r_t=r_t,
                                              tube_args=args,
                                              num_time_steps=num_time_steps,
                                              slope_angle_t=slope_angle_t):
        yield triangle


def tune_closest_approach(args):
    """
    Calculate the closest approach to the center, then return a scale
    appropriate for making the marble path get exactly that close
    """
    reg_x, reg_y = build_reg_f_t(args)

    d_t = lambda t: (reg_x(t) ** 2 + reg_y(t) ** 2) ** 0.5

    ds = [d_t(t) for t in range(0, args.num_time_steps+1)]
    closest_approach = min(ds)
    closest_step = ds.index(closest_approach)
    print("Closest approach occurs at %d: %f away" % (closest_step, ds[closest_step]))
    if closest_approach <= 0.1:
        raise ValueError("The curve is going through (or very close to) the center, making it impossible to auto-scale")

    scale = args.closest_approach / closest_approach
    print("Calculated scale: %f" % scale)
    
    #for i, d in enumerate(ds):
    #    print(i, d)
    
    return scale
    
def parse_args(sys_args=None):
    parser = argparse.ArgumentParser(description='Arguments for an stl trochoid.')

    marble_path.add_tube_arguments(parser, default_slope_angle=12.0, default_output_name='hypo.stl')
    slope_function.add_overlap_args(parser)
    combine_functions.add_zero_circle_args(parser)
    regularization.add_regularization_args(parser)

    parser.add_argument('--hypoA', default=9, type=int,
                        help='value A in the hypo formula')
    parser.add_argument('--hypoB', default=3, type=int,
                        help='value B in the hypo formula')
    parser.add_argument('--hypoC', default=6, type=float,
                        help='value C in the hypo formula')

    parser.add_argument('--x_scale', default=6, type=float,
                        help='Scale the shape by this much in the x direction')
    parser.add_argument('--y_scale', default=6, type=float,
                        help='Scale the shape by this much in the y direction')
    parser.add_argument('--scale', default=None, type=float,
                        help='Scale both directions by this much')

    parser.add_argument('--start_t', default=math.pi / 3, type=float,
                        help='Time to start the equation')
    parser.add_argument('--end_t', default=None, type=float,
                        help='Time to end the equation.  If None, will be 2pi * b / gcd(a, b)')
    parser.add_argument('--num_time_steps', default=250, type=int,
                        help='Number of time steps in the whole curve')

    parser.add_argument('--closest_approach', default=None, type=float,
                        help='Measurement from 0,0 to the closest point of the tube center.  Will override scale.  26 for a 31mm connector connecting exactly to the tube')

    parser.add_argument('--rebalance_time', dest='rebalance_time',
                        default=False, action='store_true',
                        help='Rebalance time_t so that ticks have roughly the same arclength')
    parser.add_argument('--no_rebalance_time', dest='rebalance_time',
                        action='store_false',
                        help="Don't rebalance time_t so that ticks have roughly the same arclength")

    parser.add_argument('--trochoid', default=Trochoid.HYPOTROCHOID, type=lambda x: Trochoid[x.upper()],
                        help='What formula to use.  Options are hypotrochoid and epitrochoid.')
    # TODO: add a macro argument for a flower, an N pointed star, etc

    args = parser.parse_args(args=sys_args)

    if args.end_t is None:
        N = args.hypoB / math.gcd(args.hypoA, args.hypoB)
        print("Evaluation time: {}2pi".format("%d * " % N if N != 1 else ""))
        args.end_t = args.start_t + 2 * math.pi * N

    if args.closest_approach is not None:
        args.scale = tune_closest_approach(args)

    if args.scale is not None:
        args.x_scale = args.scale
        args.y_scale = args.scale

    return args

def main(sys_args=None):
    args = parse_args(sys_args)
    marble_path.print_args(args)    

    marble_path.write_stl(generate_hypotrochoid(args), args.output_name)

if __name__ == '__main__':
    main()

