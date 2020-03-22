import filecmp
import os
import tempfile
import unittest

import generate_limacon

class TestLimacon(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(suffix=".stl", delete=False)
        self.test_file.close()

    def tearDown(self):
        os.unlink(self.test_file.name)

    def test_basic_limacon(self):
        generate_limacon.main(sys_args=['--output_name', self.test_file.name,
                                        '--time_steps', '50',
                                        '--tube_sides', '32'])
        self.assertTrue(filecmp.cmp(self.test_file.name, 'test_files/expected_basic_limacon.stl'))

    def test_stretched_limacon(self):
        generate_limacon.main(sys_args=['--output_name', self.test_file.name,
                                        '--time_steps', '50',
                                        '--tube_sides', '32',
                                        '--length', '200',
                                        '--cosine_factor', '2.5',
                                        '--constant_factor', '1.5'])
        self.assertTrue(filecmp.cmp(self.test_file.name, 'test_files/expected_stretched_limacon.stl'))

if __name__ == '__main__':
    unittest.main()

