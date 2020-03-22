import contextlib
import filecmp
import io
import os
import tempfile
import unittest

import generate_cycloid
import generate_limacon

class TestLimacon(unittest.TestCase):
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
        self.assertTrue(filecmp.cmp(self.test_file.name, 'test_files/expected_basic_limacon.stl'))

    def test_stretched_limacon(self):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            generate_limacon.main(sys_args=['--output_name', self.test_file.name,
                                            '--time_steps', '50',
                                            '--tube_sides', '32',
                                            '--length', '200',
                                            '--cosine_factor', '2.5',
                                            '--constant_factor', '1.5'])
        self.assertTrue(filecmp.cmp(self.test_file.name, 'test_files/expected_stretched_limacon.stl'))

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
        
if __name__ == '__main__':
    unittest.main()

