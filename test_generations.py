import contextlib
import filecmp
import io
import os
import tempfile
import unittest

from collections import namedtuple

import generate_cycloid
import generate_hypotrochoid
import generate_limacon

Test = namedtuple('Test', ['module', 'args', 'gold_file'])

TESTS = [Test(module=generate_limacon,
              args="--time_steps 50 --tube_sides 32".split(),
              gold_file='test_files/limacon_basic.stl')]

class TestGenerations(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(suffix=".stl", delete=False)
        self.test_file.close()

    def tearDown(self):
        os.unlink(self.test_file.name)

    def test_generations(self):
        for test in TESTS:
            with self.subTest(gold_file=test.gold_file):
                with contextlib.redirect_stdout(io.StringIO()) as stdout:
                    args = ['--output_name', self.test_file.name] + test.args
                    test.module.main(sys_args=args)
                self.assertTrue(filecmp.cmp(self.test_file.name, test.gold_file))

    def test_stretched_limacon(self):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            generate_limacon.main(sys_args=['--output_name', self.test_file.name,
                                            '--time_steps', '50',
                                            '--tube_sides', '32',
                                            '--length', '200',
                                            '--cosine_factor', '2.5',
                                            '--constant_factor', '1.5'])
        self.assertTrue(filecmp.cmp(self.test_file.name, 'test_files/limacon_stretched.stl'))

    def test_two_loop_cycloid(self):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            generate_cycloid.main(sys_args=['--output_name', self.test_file.name,
                                            "--extra_t", "0.5",
                                            "--slope_angle", "3.0",
                                            "--tube_method", "oval",
                                            "--tube_wall_height", "6",
                                            "--overlaps", "((.16675,1.40405),(-.16675,-1.40405))",
                                            "--overlap_separation", "25",
                                            "--tube_sides", "16",
                                            "--num_time_steps", "50"])
        self.assertTrue(filecmp.cmp(self.test_file.name, 'test_files/cycloid_two_loops.stl'))

    def test_hypo_three_leaves_tube(self):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            generate_hypotrochoid.main(sys_args=['--output_name', self.test_file.name,
                                                 '--hypoA', '9',
                                                 '--hypoB', '3',
                                                 '--hypoC', '6',
                                                 '--start_t', '1.0472',
                                                 '--scale', '10',
                                                 '--tube_end_angle', '240',
                                                 '--slope_angle', '12',
                                                 '--regularization', '0.07',
                                                 '--tube_sides', '16',
                                                 '--num_time_steps', '80'])
        self.assertTrue(filecmp.cmp(self.test_file.name, 'test_files/hypo_three_leaf_flower_tube.stl'))

    def test_hypo_three_leaves_tunnel(self):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            generate_hypotrochoid.main(sys_args=['--output_name', self.test_file.name,
                                                 '--hypoA', '9',
                                                 '--hypoB', '3',
                                                 '--hypoC', '6',
                                                 '--start_t', '1.0472',
                                                 '--scale', '10',
                                                 '--tube_end_angle', '360',
                                                 '--slope_angle', '12',
                                                 '--regularization', '0.07',
                                                 '--tube_sides', '12',
                                                 '--num_time_steps', '60'])
        self.assertTrue(filecmp.cmp(self.test_file.name, 'test_files/hypo_three_leaf_flower_tunnel.stl'))
        
    def test_hypo_three_leaves_holes(self):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            generate_hypotrochoid.main(sys_args=['--output_name', self.test_file.name,
                                                 '--hypoA', '9',
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
                                                 '--num_time_steps', '60'])
        self.assertTrue(filecmp.cmp(self.test_file.name, 'test_files/hypo_three_leaf_flower_holes.stl'))

    def test_hypo_single_overlap(self):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            generate_hypotrochoid.main(sys_args=['--output_name', self.test_file.name,
                                                 "--hypoA", "12",
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
                                                 "--num_time_steps", "40"])
        self.assertTrue(filecmp.cmp(self.test_file.name, 'test_files/hypo_single_overlap.stl'))

if __name__ == '__main__':
    unittest.main()

