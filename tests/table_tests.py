import unittest
from PDSQL.PDTable import PDTable
from PDSQL.PDColumn import PDColumn

class TestTableComposition(unittest.TestCase):

    def setUp(self):
        self.t1 = PDTable('t1')
        self.t2 = PDTable('t2')
        self.t3 = PDTable('t3')
        self.t4 =PDTable('t4')
        self.c1 = PDColumn('C1')
        self.c2 = PDColumn('C2')
        self.c3 = PDColumn('C3')
        self.c4 = PDColumn('C4')

    def test_repr(self):
        print repr(self.t1.select(self.c3).where(self.c1).join(self.t2.group(self.c2).join(self.t3)).join(self.t4.where(self.c4)))

