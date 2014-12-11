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
        t1 = PDTable('t1')
        c1 = (t1.col1 == 4)
        c2 = ~(t1.col2.in_(('a', 'b')))
        c1_2 = c1 | c2
        c3 = t1.col1.count()
        c4 = t1.col3.sum()
        q = t1.where(c1_2)
        print repr(q)
        q2 = q.select(c4, sum=c4)
        print repr(q2)

    def test_has_query(self):
        t = self.t1.select(self.c1.abs())
        self.assertTrue(t.has_query("_select"))
        ta2 = t.join(self.t2)
        self.assertTrue(ta2.has_query("_select"))
        self.assertTrue(ta2.has_query("_join"))
        self.assertFalse(t.has_query("_join"))
        self.assertFalse(self.t2.has_query("_join"))


if __name__ == '__main__':
    unittest.main()

