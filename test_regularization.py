import logging
import math
import unittest

from argparse import Namespace

import regularization

log = logging.getLogger("unittest")

class TestRegularization(unittest.TestCase):
    def test_hyperbolic_factor(self):
        reg_args = Namespace(regularization_x_trans=1.0,
                             regularization_y_trans=2.0,
                             regularization_slope=0.5)
        self.assertEqual("Hyperbolic regularization: y = 0.5 (0.5 (x - 1.0) + (4.0 + 0.25 (x - 1.0)^{2})^{0.5}) + 2.0",
                          regularization.hyperbolic_function_string(reg_args))
        factor = regularization.hyperbolic_factor(reg_args)
        self.assertAlmostEqual(3.0, factor(1.0))
        self.assertAlmostEqual(1.6403882, factor(2.0))
        self.assertAlmostEqual(0.88284271, factor(5.0))
        self.assertAlmostEqual(0, factor(-1000000000))
        self.assertAlmostEqual(0.5, factor(1000000000))
        

    def test_capped_linear_factor(self):
        factor = regularization.capped_linear_factor(10.0)

        # on the linear part
        self.assertAlmostEqual(factor(1), 1.0)
        # at the intersection
        self.assertAlmostEqual(factor(10 / math.sqrt(2)), 1.0)
        # on the curve
        # take a couple different paths to calculate each one
        self.assertAlmostEqual(100, (9 * factor(9)) ** 2 + (2 ** 0.5 * 10 - 9) ** 2)
        self.assertAlmostEqual(9 * factor(9), 10 * math.cos(math.asin(2 ** 0.5 - .9)))
        self.assertAlmostEqual(100, (10 * factor(10)) ** 2 + (2 ** 0.5 * 10 - 10) ** 2)
        self.assertAlmostEqual(10 * factor(10), 10 * math.cos(math.asin(2 ** 0.5 - 1)))
        # at the next intersection
        self.assertAlmostEqual(factor(10 * math.sqrt(2)), math.sqrt(0.5))
        # on the flat part
        self.assertAlmostEqual(factor(15), 2 / 3)
        self.assertAlmostEqual(factor(20), 0.5)

if __name__ == '__main__':
    unittest.main()
