import unittest
from PDSQL.PDColumn import PDColumn


class TestUnaryOps(unittest.TestCase):

    def setUp(self):
        self.c1 = PDColumn('C1')
        self.c2 = PDColumn('C2')
        self.c3 = PDColumn('C3')

    def test_unary(self):
        c = self.c1.abs()
        self.assertTrue(c.has_unary())
        c = abs(self.c1)
        self.assertTrue(c.has_unary())
        self.assertFalse(self.c1.has_unary())
        c = self.c1.abs()
        self.assertRaises(Exception, c.__abs__)

    def test_repr(self):
        print repr(self.c1+(self.c2-self.c2.sum()))

if __name__ == '__main__':
    unittest.main()
