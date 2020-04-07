import contextlib
import filecmp
import io
import os
import tempfile
import unittest

from collections import namedtuple

import generate_cycloid
import generate_helix
import generate_hypotrochoid
import generate_limacon
import generate_lissajous
import generate_tube

Test = namedtuple('Test', ['name', 'model', 'args', 'gold_file'])

TESTS = [Test(name='Tube Basic',
              model=generate_tube,
              args=["--time_steps", "25",
                    "--tube_sides", "16",
                    "--slope_angle", "10"],
              gold_file='test_files/tube_basic.stl'),

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
         Test(name='Helix Clockwise',
              model=generate_helix,
              args=["--vertical_displacement", '30',
                    "--clockwise",
                    "--initial_rotation", '72',
                    "--helix_sides", "10",
                    "--helix_radius", "17",
                    "--tube_sides", "15",
                    "--rotations", "1.5"],
              gold_file='test_files/helix_clockwise_rotated.stl'),
         
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
              args=["--extra_t", "0.5",
                    "--slope_angle", "3.0",
                    "--tube_method", "oval",
                    "--tube_wall_height", "6",
                    "--overlaps", "((.16675,1.40405),(-.16675,-1.40405))",
                    "--overlap_separation", "25",
                    "--tube_sides", "10",
                    "--num_time_steps", "40"],
              gold_file='test_files/cycloid_two_loops.stl'),

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
              gold_file='test_files/lissajous_basic_cw.stl')]
              
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

