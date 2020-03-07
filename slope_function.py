import math

import marble_path

def get_drop(arclengths, min_angle, max_angle, start_time_step, end_time_step):
    """
    Given a set of arclengths, the start & end times, and the angles
    to gradually transition between, return the total drop for that span.

    TODO: refactor with the code that assigns the actual angles in update_slopes?
    """
    total_drop = 0.0
    delta_time_step = end_time_step - start_time_step
    for time_step in range(delta_time_step):
        if time_step < delta_time_step * 0.2:
            slope = min_angle + (max_angle - min_angle) * time_step / (delta_time_step * 0.2)
        elif time_step > delta_time_step * 0.8:
            slope = min_angle + (max_angle - min_angle) * (delta_time_step - time_step) / (delta_time_step * 0.2)
        else:
            slope = max_angle
        total_drop = total_drop + (arclengths[time_step + start_time_step + 1] - arclengths[time_step + start_time_step]) * math.tan(slope * math.pi / 180)
    #print("Total drop for angle", max_angle, "is", total_drop)
    return total_drop

def get_drop_angle(arclengths, slope_angle, start_time_step, end_time_step, needed_dz):
    """
    Get the drop angle needed to gradually achieve the desired dz in the given time span

    Works by using binary search between the base slope_angle and 45 degrees down
    """
    total_drop = get_drop(arclengths, slope_angle, slope_angle, start_time_step, end_time_step)
    if total_drop > needed_dz:
        return

    total_drop = get_drop(arclengths, slope_angle, 45, start_time_step, end_time_step)
    if total_drop < needed_dz:
        raise ValueError("Even an angle of 45 is not sufficient to achieve this drop")

    min_angle = slope_angle
    max_angle = 45
    while max_angle - min_angle > 0.01:
        test_angle = (max_angle + min_angle) / 2
        total_drop = get_drop(arclengths, slope_angle, test_angle, start_time_step, end_time_step)
        if total_drop < needed_dz:
            min_angle = test_angle
        else:
            max_angle = test_angle
    return (max_angle + min_angle) / 2.0    

def get_time_step(times, t):
    """
    Given a list mapping time step to actual t, return the time step closest to the desired t
    """
    # TODO: implement binary search?
    if times[0] > t:
        return 0
    if times[-1] < t:
        return len(times) - 1
    for i in range(len(times)):
        if times[i] <= t and times[i+1] > t:
            return i
    raise AssertionError("Oops")

def update_slopes(slopes, arclengths, times, slope_angle, start_t, end_t, needed_dz):
    """
    Update a list of slopes, changing the slopes in a way such that
    between start_t and end_t, the path goes down by needed_dz
    """
    start_time_step = get_time_step(times, start_t)
    end_time_step = get_time_step(times, end_t)
    if end_time_step < start_time_step:
        end_time_step, start_time_step = start_time_step, end_time_step

    best_angle = get_drop_angle(arclengths, slope_angle, start_time_step, end_time_step, needed_dz)
    if best_angle is None:
        print("Nothing to do for the overlap at interval %.4f, %.4f" % (start_t, end_t))
        return

    delta_time_step = end_time_step - start_time_step
    for time_step in range(delta_time_step+1):
        if time_step < delta_time_step * 0.2:
            new_slope = slope_angle + (best_angle - slope_angle) * time_step / (delta_time_step * 0.2)
        elif time_step > delta_time_step * 0.8:
            new_slope = slope_angle + (best_angle - slope_angle) * (delta_time_step - time_step) / (delta_time_step * 0.2)
        else:
            new_slope = best_angle
        slopes[time_step+start_time_step] = max(new_slope, slopes[time_step+start_time_step])


def slope_function(x_t, y_t, time_t, slope_angle, num_time_steps, overlaps, overlap_separation):
    arclengths = marble_path.calculate_arclengths(x_t, y_t, num_time_steps)
    times = [time_t(t) for t in range(num_time_steps+1)]
    slopes = [slope_angle for t in range(num_time_steps+1)]
    if overlaps:
        for start_t, end_t in overlaps:
            # for the basic 2 loop cycloid, want +/- .16675, 1.40405
            update_slopes(slopes, arclengths, times, slope_angle, start_t, end_t, overlap_separation)

    slope_angle_t = lambda time_step_t: slopes[time_step_t]
    return slope_angle_t

