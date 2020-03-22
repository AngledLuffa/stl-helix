import contextlib
import filecmp
import io
import os
import tempfile
import unittest

import generate_cycloid
import generate_hypotrochoid
import generate_limacon

class TestGenerations(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(suffix=".stl", delete=False)
        self.test_file.close()

    def tearDown(self):
        os.unlink(self.test_file.name)

    def test_basic_limacon(self):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            generate_limacon.main(sys_args=['--output_name', self.test_file.name,
                                            '--time_steps', '50',
                                            '--tube_sides', '32'])
        self.assertTrue(filecmp.cmp(self.test_file.name, 'test_files/limacon_basic.stl'))

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
        
if __name__ == '__main__':
    unittest.main()

