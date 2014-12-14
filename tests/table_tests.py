import sqlite3
import unittest

from PDSQL.PDTable import PDTable
from PDSQL.PDColumn import PDColumn


class TestTableComposition(unittest.TestCase):

    def setUp(self):
        self.t1 = PDTable('t1')
        self.t2 = PDTable('t2')
        self.t3 = PDTable('t3')
        self.t4 = PDTable('t4')
        self.c1 = PDColumn('C1')
        self.c2 = PDColumn('C2')
        self.c3 = PDColumn('C3')
        self.c4 = PDColumn('C4')

    def test_repr(self):
        print repr(
            self.t1.select(self.c3)
                .where(self.c1)
                .join(self.t2.group(self.c2).join(self.t3))
                .join(self.t4.where(self.c4)))
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

    def test_limiting(self):
        query = self.t1.select(self.t1.c).order(self.t1.c)
        self.assertEqual(
            query[0].compile(),
            'SELECT t1.c FROM t1 ORDER BY t1.c ASC LIMIT 1;')
        self.assertEqual(
            query[-1].compile(),
            'SELECT t1.c FROM t1 ORDER BY t1.c DESC LIMIT 1;')
        self.assertEqual(
            query[:5].compile(),
            'SELECT t1.c FROM t1 ORDER BY t1.c ASC LIMIT 5;')
        self.assertEqual(
            query[-5:].compile(),
            'SELECT t1.c FROM t1 ORDER BY t1.c DESC LIMIT 5;')

    def test_reverse(self):
        query = self.t1.select(self.t1.c).order(self.t1.c)
        self.assertEqual(
            query.compile(),
            'SELECT t1.c FROM t1 ORDER BY t1.c ASC;')
        query = reversed(query)
        self.assertEqual(
            query.compile(),
            'SELECT t1.c FROM t1 ORDER BY t1.c DESC;')
        query = reversed(query)
        self.assertEqual(
            query.compile(),
            'SELECT t1.c FROM t1 ORDER BY t1.c ASC;')

    def test_select(self):
        t1 = self.t1
        self.assertEqual(
            t1.select().compile(),
            'SELECT * FROM t1;')
        self.assertEqual(
            t1.select(t1.c1).compile(),
            'SELECT t1.c1 FROM t1;')
        self.assertEqual(
            t1.select(('c1', t1.c1)).compile(),
            'SELECT t1.c1 AS "c1" FROM t1;')
        self.assertEqual(
            t1.select(t1.c1, t1.c2).compile(),
            'SELECT t1.c1 , t1.c2 FROM t1;')
        self.assertEqual(
            t1.select(t1.c1, ('c2', t1.c2)).compile(),
            'SELECT t1.c1 , t1.c2 AS "c2" FROM t1;')
        self.assertEqual(
            t1.select(('c1', t1.c1), ('c2', t1.c2)).compile(),
            'SELECT t1.c1 AS "c1" , t1.c2 AS "c2" FROM t1;')

    def test_distinct(self):
        self.assertEqual(
            self.t1.select(self.t1.col).distinct().compile(),
            'SELECT DISTINCT t1.col FROM t1;')

    def test_is_null(self):
        t1 = self.t1
        self.assertEqual(
            t1.where(t1.col.is_null()).compile(),
            'SELECT * FROM t1 WHERE ( t1.col IS NULL );')
        self.assertEqual(
            t1.where(t1.col.not_null()).compile(),
            'SELECT * FROM t1 WHERE ( t1.col IS NOT NULL );')
        self.assertRaises(
            Exception,
            t1.col.not_null().is_null)

    def test_group(self):
        t1 = self.t1
        self.assertRaises(
            Exception,
            t1.having(t1.col == 1).compile)
        t1.group(t1.col).having(t1.col == 1).compile()

    def test_aggregation(self):
        t1 = self.t1
        t1.select(t1.col.sum())
        t1.group(t1.col).having(t1.col.sum())
        self.assertRaises(
            Exception,
            t1.where, t1.col.sum)
        self.assertRaises(
            Exception,
            t1.group, t1.col.sum)
        self.assertRaises(
            Exception,
            t1.order, t1.col.sum)


class TestDatabaseQuery(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect('tests/db.sqlite3')
        self.cursor = self.connection.cursor()
        self.states = PDTable('states', cursor=self.cursor)

    def test_queries(self):
        st = self.states
        query = st.select(st.name).where(st.statecode == 'CA')
        self.assertEqual(query.run().fetchall(), [('California',)])
        query = st.select(st.population_2010) \
            .where((st.statecode == 'CA') | (st.statecode == 'NV')) \
            .order(st.landarea)
        self.assertEqual(query.run().fetchall(), [(2700551,), (37253956,)])

    def tearDown(self):
        self.connection.close()


if __name__ == '__main__':
    unittest.main()
