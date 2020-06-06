import contextlib
import filecmp
import io
import os
import tempfile
import unittest

from collections import namedtuple

import generate_basic_ramp
import generate_cycloid
import generate_helix
import generate_hypotrochoid
import generate_limacon
import generate_lissajous
import generate_trig
import generate_tube
import generate_zigzag

Test = namedtuple('Test', ['name', 'model', 'args', 'gold_file'])

TESTS = [Test(name='Tube Basic',
              model=generate_tube,
              args=["--num_time_steps", "25",
                    "--tube_sides", "16",
                    "--slope_angle", "10"],
              gold_file='test_files/tube_basic.stl'),

         Test(name='Tube High Slope',
              model=generate_tube,
              args=["--num_time_steps", "25",
                    "--tube_sides", "16",
                    "--slope_angle", "45"],
              gold_file='test_files/tube_slope.stl'),

         Test(name='Tube Rotation',
              model=generate_tube,
              args=["--num_time_steps", "25",
                    "--tube_sides", "16",
                    "--slope_angle", "10",
                    "--rotation", "45"],
              gold_file='test_files/tube_rotation.stl'),

         Test(name='Helix Basic',
              model=generate_helix,
              args=["--slope_angle", "5",
                    "--helix_sides", "16",
                    "--tube_sides", "16"],
              gold_file='test_files/helix_basic.stl'),

         # test various alternate parameters for the helix
         Test(name='Helix Adjusted',
              model=generate_helix,
              args=["--slope_angle", "4.5",
                    "--helix_sides", "10",
                    "--helix_radius", "17",
                    "--tube_sides", "15",
                    "--rotations", ".7"],
              gold_file='test_files/helix_adjusted.stl'),

         # test rotating the helix.  also, test a helix with more than 1 rotation
         Test(name='Helix Rotated',
              model=generate_helix,
              args=["--vertical_displacement", '30',
                    "--initial_rotation", '36',
                    "--helix_sides", "10",
                    "--helix_radius", "17",
                    "--tube_sides", "15",
                    "--rotations", "1.5"],
              gold_file='test_files/helix_rotated.stl'),
         
         # clockwise test starting from 0 rotation.  
         Test(name='Helix Clockwise',
              model=generate_helix,
              args=["--vertical_displacement", '30',
                    "--clockwise",
                    "--initial_rotation", '0',
                    "--helix_sides", "10",
                    "--helix_radius", "17",
                    "--tube_sides", "15",
                    "--rotations", "0.3"],
              gold_file='test_files/helix_clockwise.stl'),
         
         # clockwise test starting from 72 rotation.
         Test(name='Helix Clockwise Rotated',
              model=generate_helix,
              args=["--vertical_displacement", '30',
                    "--clockwise",
                    "--initial_rotation", '72',
                    "--helix_sides", "10",
                    "--helix_radius", "17",
                    "--tube_sides", "15",
                    "--rotations", "1.5"],
              gold_file='test_files/helix_clockwise_rotated.stl'),
         
         Test(name='Basic Ramp',
              model=generate_basic_ramp,
              args=["--num_time_steps", "24",
                    "--tube_sides", "10",
                    "--slope_angle", "2.9"],
              gold_file='test_files/basic_ramp.stl'),

         Test(name='Basic Ramp Counterclockwise',
              model=generate_basic_ramp,
              args=["--num_time_steps", "24",
                    "--tube_sides", "10",
                    "--post_exit_counterclockwise",
                    "--slope_angle", "2.9"],
              gold_file='test_files/basic_ramp_ccw.stl'),

         Test(name='Basic Ramp Hole',
              model=generate_basic_ramp,
              args=["--num_time_steps", "24",
                    "--tube_sides", "10",
                    "--tube_radius", "10.5",
                    "--wall_thickness", "11",
                    "--post_effective_tube_radius", "12.5",
                    "--post_effective_wall_thickness", "2",
                    "--tube_start_angle", "0",
                    "--tube_end_angle", "360",
                    "--ramp_extension", "0.0",
                    "--slope_angle", "10"],
              gold_file='test_files/basic_ramp_hole.stl'),

         Test(name='Limacon Basic',
              model=generate_limacon,
              args=["--time_steps", "30",
                    "--tube_sides", "10"],
              gold_file='test_files/limacon_basic.stl'),

         Test(name='Limacon Stretched',
              model=generate_limacon,
              args=['--time_steps', '30',
                    '--tube_sides', '10',
                    '--length', '200',
                    '--cosine_factor', '2.5',
                    '--constant_factor', '1.5'],
              gold_file='test_files/limacon_stretched.stl'),

         Test(name='Cycloid with two loops',
              model=generate_cycloid,
              args=["--extra_t", "0.1",
                    "--scale", "32.3547",
                    "--slope_angle", "3.0",
                    "--tube_method", "oval",
                    "--tube_wall_height", "6",
                    "--overlaps", "((.16675,1.40405),(-.16675,-1.40405))",
                    "--overlap_separation", "25",
                    "--tube_sides", "10",
                    "--num_time_steps", "40"],
              gold_file='test_files/cycloid_two_loops.stl'),

         # Test that the extra_t production works at a different angle
         Test(name='Cycloid with two omegas',
              model=generate_cycloid,
              args=["--extra_t", "0.3",
                    "--slope_angle", "9.0",
                    "--tube_method", "ellipse",
                    "--scale", "40",
                    "--x_coeff", "-0.8",
                    "--x_t_coeff", "4",
                    "--y0", "0",
                    "--y_coeff", "1.5",
                    "--y_t_coeff", "2",
                    "--y_phase", "1.5708",
                    "--min_domain", "-1.5708",
                    "--max_domain", "1.5708",
                    "--no_use_sign",
                    "--tube_sides", "10",
                    "--num_time_steps", "40"],
              gold_file='test_files/cycloid_two_omegas.stl'),

         # Test overhangs on both start & end angle
         Test(name='Cycloid with two omegas and overhangs',
              model=generate_cycloid,
              args=["--extra_t", "0.0",
                    "--slope_angle", "9.0",
                    "--tube_method", "ellipse",
                    "--scale", "40",
                    "--x_coeff", "-0.8",
                    "--x_t_coeff", "4",
                    "--y0", "0",
                    "--y_coeff", "1.5",
                    "--y_t_coeff", "2",
                    "--y_phase", "1.5708",
                    "--min_domain", "-0.5",
                    "--max_domain", "0.5",
                    "--no_use_sign",
                    "--tube_sides", "8",
                    "--tube_end_angle", "((-0.2,240),(0.0,180))",
                    "--tube_start_angle", "((0.0,0),(0.2,-60))",
                    "--num_time_steps", "40"],
              gold_file='test_files/cycloid_two_omegas_overhangs.stl'),

         # This tests a variety of cycloid arguments and the old style
         # of smoothing kinks
         Test(name='Cycloid with crazy shape',
              model=generate_cycloid,
              args=["--extra_t", "0.0",
                    "--min_domain", "-2.3562",
                    "--max_domain", "2.3562",
                    "--x_coeff", "-1",
                    "--y0", "0.0",
                    "--y_coeff", "1.0",
                    "--y_t_coeff", "3",
                    "--scale", "46.3392",
                    "--no_use_sign",
                    "--y_scale", "1.2",
                    "--y_phase", "1.5708",
                    "--reg_x", "0.4",
                    "--overlaps", "((0.95215,2.18945),(-0.95215,-2.18945))",
                    "--overlap_separation", "23",
                    "--slope_angle", "2.19",
                    "--tube_method", "ellipse",
                    "--wall_thickness", "2.5",
                    "--kinks", "(-0.3927, 0.3927)",
                    "--kink_width", "0.15",
                    "--kink_slope", "0.5",
                    "--tube_sides", "8",
                    "--num_time_steps", "80"],
              gold_file='test_files/cycloid_crazy.stl'),
         
         Test(name='Hypo with 3 leaves tube',
              model=generate_hypotrochoid,
              args=['--hypoA', '9',
                    '--hypoB', '3',
                    '--hypoC', '6',
                    '--start_t', '1.0472',
                    '--scale', '10',
                    '--tube_end_angle', '240',
                    '--slope_angle', '12',
                    '--regularization', '0.07',
                    '--tube_sides', '16',
                    '--num_time_steps', '80'],
              gold_file='test_files/hypo_three_leaf_flower_tube.stl'),

         Test(name='Hypo with 3 leaves tunnel',
              model=generate_hypotrochoid,
              args=['--hypoA', '9',
                    '--hypoB', '3',
                    '--hypoC', '6',
                    '--start_t', '1.0472',
                    '--scale', '10',
                    '--tube_end_angle', '360',
                    '--slope_angle', '12',
                    '--regularization', '0.07',
                    '--tube_sides', '12',
                    '--num_time_steps', '60'],
              gold_file='test_files/hypo_three_leaf_flower_tunnel.stl'),

         Test(name='Hypo with 3 leaves holes',
              model=generate_hypotrochoid,
              args=['--hypoA', '9',
                    '--hypoB', '3',
                    '--hypoC', '6',
                    '--start_t', '1.0472',
                    '--scale', '10',
                    '--tube_end_angle', '360',
                    '--slope_angle', '12',
                    '--regularization', '0.07',
                    '--tube_radius', '10.5',
                    '--wall_thickness', '11',
                    '--tube_sides', '12',
                    '--num_time_steps', '60'],
              gold_file='test_files/hypo_three_leaf_flower_holes.stl'),

         Test(name='Hypo with four leaves and a zero circle',
              model=generate_hypotrochoid,
              args=['--hypoA', '12',
                    '--hypoB', '3',
                    '--hypoC', '6',
                    '--slope_angle', '3',
                    '--tube_method', 'OVAL',
                    '--tube_wall_height', '7',
                    '--closest_approach', '26',
                    '--regularization', '0.05',
                    '--overlap_separation', '23',
                    '--overlaps', "((0.9117, 2.2299),(2.4825, 3.8007))",
                    '--zero_circle',
                    '--start_t', '0.88',
                    '--end_t', '3.83',
                    '--num_time_steps', '30',
                    '--zero_circle_sides', '8',
                    '--tube_sides', '14'],
              gold_file='test_files/hypo_four_leaves_zero_circle.stl'),

         Test(name='Hypo with single overlap',
              model=generate_hypotrochoid,
              args=["--hypoA", "12",
                    "--hypoB", "3",
                    "--hypoC", "6",
                    "--start_t", "0.5",
                    "--end_t", "2.5",
                    "--slope_angle", "5",
                    "--tube_method", "OVAL",
                    "--tube_wall_height", "7",
                    "--closest_approach", "26",
                    "--regularization", "0.05",
                    "--overlap_separation", "23",
                    "--overlaps", "(0.9117, 2.2299)",
                    "--tube_sides", "16",
                    "--num_time_steps", "40"],
              gold_file='test_files/hypo_single_overlap.stl'),
              
         Test(name='Epitrochoid',
              model=generate_hypotrochoid,
              args=["--hypoA", "7",
                    "--hypoB", "2",
                    "--hypoC", "5",
                    "--slope_angle", "3.2",
                    "--closest_approach", "26",
                    "--trochoid", "EPITROCHOID",
                    "--overlaps", "(1.2602, 2.3302)",
                    "--zero_circle",
                    "--zero_circle_sides", "10",
                    "--start_t", "0.3",
                    "--end_t", "3.0",
                    "--tube_sides", "10",
                    "--num_time_steps", "30"],
              gold_file='test_files/epitrochoid.stl'),
              
                    
         Test(name='Trig - deep oval with kinks',
              model=generate_trig,
              args=["--y_coeff", "4.1",
                    "--power", "2",
                    "--slope_angle", "10.35",
                    "--tube_method", "deep_oval",
                    "--tube_wall_height", "3",
                    "--kink_replace_circle", "((1.0,2.0),(4.14,5.14))",
                    "--start_t", "0",
                    "--end_t", "5.8",
                    "--scale", "5.8572",
                    "--num_time_steps", "40",
                    "--tube_sides", "12"],
              gold_file='test_files/trig_deep_oval.stl'),
              
         Test(name='Trig - deep oval with curved overhang',
              model=generate_trig,
              args=["--y_coeff", "4.1",
                    "--power", "2",
                    "--slope_angle", "10.35",
                    "--tube_method", "deep_oval",
                    "--tube_wall_height", "3",
                    "--kink_replace_circle", "((1.0,2.0))",
                    "--start_t", "0",
                    "--end_t", "3",
                    "--scale", "5.8572",
                    "--num_time_steps", "25",
                    "--tube_start_angle", "0",
                    "--tube_end_angle", "225",
                    "--tube_sides", "12"],
              gold_file='test_files/trig_overhang.stl'),

         # Test that the overhang can be modified by specifying intervals on the tube_end_angle
         Test(name='Trig - deep oval with partial overhang',
              model=generate_trig,
              args=["--y_coeff", "4.1",
                    "--power", "2",
                    "--slope_angle", "10.35",
                    "--tube_method", "deep_oval",
                    "--tube_wall_height", "3",
                    "--kink_replace_circle", "((1.0,2.0))",
                    "--start_t", "0",
                    "--end_t", "3",
                    "--scale", "5.8572",
                    "--num_time_steps", "25",
                    "--tube_start_angle", "0",
                    "--tube_end_angle", "((1.0,225),(2.0,180))",
                    "--tube_sides", "12"],
              gold_file='test_files/trig_partial_overhang.stl'),
              
         Test(name='Trig - deep ellipse with kinks',
              model=generate_trig,
              args=["--y_coeff", "4.1",
                    "--power", "2",
                    "--slope_angle", "10.35",
                    "--tube_method", "deep_ellipse",
                    "--tube_start_angle", "0",
                    "--tube_end_angle", "360",
                    "--wall_thickness", "13",
                    "--kink_replace_circle", "((1.0,2.0),(4.14,5.14))",
                    "--start_t", "0",
                    "--end_t", "5.8",
                    "--scale", "5.8572",
                    "--num_time_steps", "40",
                    "--tube_sides", "8"],
              gold_file='test_files/trig_deep_ellipse.stl'),
              
         Test(name='Lissajous - basic, CCW kink',
              model=generate_lissajous,
              args=["--lissA", "5",
                    "--lissB", "0",
                    "--lissC", "3",
                    "--y_scale", "54",
                    "--x_scale", "40",
                    "--slope_angle", "4",
                    "--tube_sides", "10",
                    "--start_t", "0",
                    "--end_t", "0.4",
                    "--num_time_steps", "40",
                    "--kink_replace_circle", "(0.10,0.21)"],
              gold_file='test_files/lissajous_basic_ccw.stl'),
              
         Test(name='Lissajous - basic, CW kink',
              model=generate_lissajous,
              args=["--lissA", "5",
                    "--lissB", "0",
                    "--lissC", "3",
                    "--y_scale", "54",
                    "--x_scale", "40",
                    "--slope_angle", "4",
                    "--tube_sides", "10",
                    "--start_t", "-0.4",
                    "--end_t", "0",
                    "--num_time_steps", "40",
                    "--kink_replace_circle", "(-0.21,-0.10)"],
              gold_file='test_files/lissajous_basic_cw.stl'),

         Test(name='Lissajous - sum of harmonics',
              model=generate_lissajous,
              args=["--lissajous", "SUM_HARMONICS",
                    "--lissA", "1",
                    "--lissB", "0.5",
                    "--lissC", "1",
                    "--lissD", "0",
                    "--lissN", "3",
                    "--x_scale", "87",
                    "--y_scale", "88.5",
                    "--slope_angle", "2.9",
                    "--start_t", "0.11",
                    "--end_t", "0.39",
                    "--num_time_steps", "40",
                    "--tube_sides", "10"],
              gold_file='test_files/lissajous_sum_harmonics.stl'),

         Test(name='Lissajous - sum of harmonics, start_angle overhang',
              model=generate_lissajous,
              args=["--lissajous", "SUM_HARMONICS",
                    "--lissA", "2",
                    "--lissB", "0",
                    "--lissC", "1",
                    "--lissD", "-0.5",
                    "--lissN", "2.5",
                    "--x_scale", "55.416",
                    "--y_scale", "110.832",
                    "--slope_angle", "3.7",
                    "--start_t", "-0.036",
                    "--end_t", "0.07",
                    "--tube_radius", "12.5",
                    "--tube_method", "oval",
                    "--tube_start_angle", "((-0.02,-45),(0.04,0))",
                    "--tube_wall_height", "6",
                    "--num_time_steps", "30",
                    "--tube_sides", "16"],
              gold_file='test_files/lissajous_sum_start_overhang.stl'),
         
         Test(name='Lissajous - product of harmonics',
              model=generate_lissajous,
              args=["--lissajous", "PRODUCT_HARMONICS",
                    "--lissA", "2",
                    "--lissB", "0.0",
                    "--lissC", "1",
                    "--lissD", "0.5",
                    "--lissN", "7",
                    "--x_scale", "94.9873",
                    "--y_scale", "85.93",
                    "--slope_angle", "7.10198",
                    "--start_t", "-0.02",
                    "--end_t", "0.02",
                    "--tube_start_angle", "((-0.018,-60),(-0.005,-90),(0.005,-90),(0.018,-60))",
                    "--tube_end_angle", "((-0.018,240),(-0.005,270),(0.005,270),(0.018,240))",
                    "--num_time_steps", "40",
                    "--tube_sides", "10"],
              gold_file='test_files/lissajous_product.stl'),

         Test(name='Lissajous - compound harmonics splitter',
              model=generate_lissajous,
              args=["--lissajous", "COMPOUND_HARMONICS",
                    "--lissA", "2",
                    "--lissB", "0.25",
                    "--lissC", "1",
                    "--lissD", "0",
                    "--lissN", "1",
                    "--x_scale", "80",
                    "--y_scale", "80",
                    "--slope_angle", "9",
                    "--extra_start_t", "0.04",
                    "--start_t", "0.25",
                    "--end_t", "0.5625",
                    "--num_time_steps", "40",
                    "--tube_sides", "10"],
              gold_file='test_files/lissajous_compound_harmonics_splitter.stl'),

         Test(name='Zigzag',
              model=generate_zigzag,
              args=["--tube_sides", "10",
                    "--subdivisions_per_zigzag", "6"],
              gold_file='test_files/zigzag.stl'),]
              
class TestGenerations(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(suffix=".stl", delete=False)
        self.test_file.close()

    def tearDown(self):
        os.unlink(self.test_file.name)

    def test_generations(self):
        for test in TESTS:
            with self.subTest(name=test.name):
                print("Running %s" % test.name)
                with contextlib.redirect_stdout(io.StringIO()) as stdout:
                    args = ['--output_name', self.test_file.name] + test.args
                    test.model.main(sys_args=args)
                self.assertTrue(filecmp.cmp(self.test_file.name, test.gold_file))

if __name__ == '__main__':
    unittest.main()

