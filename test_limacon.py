import filecmp
import os
import tempfile
import unittest

import generate_limacon

class TestLimacon(unittest.TestCase):
    def test_basic_limacon(self):
        test_file = tempfile.NamedTemporaryFile(suffix=".stl", delete=False)
        test_file.close()
        try:
            generate_limacon.main(sys_args=['--output_name', test_file.name,
                                            '--time_steps', '50',
                                            '--tube_sides', '32'])
            self.assertTrue(filecmp.cmp(test_file.name, 'test_files/expected_basic_limacon.stl'))
        finally:
            os.unlink(test_file.name)

    def test_stretched_limacon(self):
        test_file = tempfile.NamedTemporaryFile(suffix=".stl", delete=False)
        test_file.close()
        try:
            generate_limacon.main(sys_args=['--output_name', test_file.name,
                                            '--time_steps', '50',
                                            '--tube_sides', '32',
                                            '--length', '200',
                                            '--cosine_factor', '2.5',
                                            '--constant_factor', '1.5'])
            self.assertTrue(filecmp.cmp(test_file.name, 'test_files/expected_stretched_limacon.stl'))
        finally:
            os.unlink(test_file.name)

if __name__ == '__main__':
    unittest.main()

