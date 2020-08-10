import logging
import math
import unittest

import regularization
log = logging.getLogger("unittest")

class TestRegularization(unittest.TestCase):
    def test_generations(self):
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
