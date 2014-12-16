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
        c4 = t1.col3.sum()
        q = t1.where(c1_2)
        print repr(q)
        q2 = q.select(c4, ('sum', c4))
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
        self.assertRaises(Exception, query.limit, 'test')
        self.assertRaises(Exception, query.limit(1).limit, 2)

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
        self.assertRaises(Exception, t1.col.not_null().is_null)

    def test_group(self):
        t1 = self.t1
        self.assertRaises(
            Exception,
            t1.having(t1.col == 1).compile)
        t1.group(t1.col).having(t1.col == 1).compile()

    def test_querying_restrictions(self):
        t1 = self.t1
        t1.select(t1.col.sum())
        t1.group(t1.col).having(t1.col.sum())
        self.assertRaises(Exception, t1.where, t1.col.sum())
        self.assertRaises(Exception, t1.group, t1.col.sum())
        self.assertRaises(Exception, t1.join, 'test')
        t1.join(self.t2)

    def test_join(self):
        t1 = self.t1
        t2 = self.t2
        t3 = self.t3
        self.assertEqual(
            t1.join(t2).compile(), 'SELECT * FROM ( t1 INNER JOIN t2 );')
        self.assertEqual(
            t1.join(t2.where(t2.col == 1)).compile(),
            'SELECT * FROM ( t1 INNER JOIN '
            '( SELECT * FROM t2 WHERE ( ( t2.col = 1 ) ) ) );')
        self.assertEqual(
            t1.join(t2.join(t3)).compile(),
            'SELECT * FROM ( t1 INNER JOIN ( SELECT * FROM '
            '( t2 INNER JOIN t3 ) ) );')

    def test_subqueries(self):
        t1 = self.t1
        self.assertEqual(
            t1.where(t1.col == t1.select(t1.col.max())).compile(),
            'SELECT * FROM t1 WHERE ( ( '
            't1.col = ( SELECT MAX( t1.col ) FROM t1 ) ) );')
        self.assertEqual(
            t1.where(t1.select(t1.col.max()) == t1.col).compile(),
            'SELECT * FROM t1 WHERE ( ( '
            '( SELECT MAX( t1.col ) FROM t1 ) = t1.col ) );')
        self.assertEqual(
            t1.group(t1.col)
              .having(t1.col.avg() > t1.select(t1.col.avg())).compile(),
            'SELECT * FROM t1 GROUP BY t1.col HAVING ( ( AVG( t1.col ) > ( '
            'SELECT AVG( t1.col ) FROM t1 ) ) );')

    def test_set_operations(self):
        t1 = self.t1
        t2 = self.t2
        t3 = self.t3
        self.assertEqual(
            t1.union(t2).compile(),
            'SELECT * FROM t1 UNION SELECT * FROM t2;')
        self.assertEqual(
            t1.intersect(t2.where(t2.col > 1)).compile(),
            'SELECT * FROM t1 INTERSECT '
            'SELECT * FROM t2 WHERE ( ( t2.col > 1 ) );')
        self.assertEqual(
            t1.select(t1.col).except_(t2.where(t2.col > 1)).compile(),
            'SELECT t1.col FROM t1 EXCEPT '
            'SELECT * FROM t2 WHERE ( ( t2.col > 1 ) );')
        self.assertEqual(
            t1.union(t2).union(t3).compile(),
            'SELECT * FROM t1 UNION SELECT * FROM t2 UNION SELECT * FROM t3;')


class TestCompilerRewrites(unittest.TestCase):
    def setUp(self):
        self.t1 = PDTable("t1")
        self.t2 = PDTable("t2")
        self.t3 = PDTable("t3")

    def test_select_star(self):
        t = self.t1.where(self.t1.col1 > 5)
        self.assertEqual(t.compile(),
            'SELECT * FROM t1 WHERE ( ( t1.col1 > 5 ) );')

    def test_exists_to_in(self):
        e = PDTable("employees")
        o = PDTable("orders")

        # 11.5.3.4.1 Bad exists query
        # Correlated subquery that is highly selective
        # Should be rewritten to use in.

        query = e.select(e.employee_id, e.first_name, e.last_name, e.salary)\
            .where_exists(o.select(1).where(e.employee_id == o.sales_rep_id)\
                .where(o.customer_id == 144))
        self.assertEqual(
            query.compile(),
            'SELECT employees.employee_id , employees.first_name , '
            'employees.last_name , employees.salary FROM employees '
            'WHERE ( ( employees.employee_id IN ( SELECT orders.sales_rep_id '
            'FROM orders WHERE ( ( orders.customer_id = 144 ) ) ) ) );')

        t1 = self.t1
        t2 = self.t2
        query = t1.select(t1.col1).where(t1.col2 > t1.col1) \
            .where_exists(t2.where(t2.id2 == t1.id1)\
                .where(t2.val1 == 123).where(t2.val2.in_(('a',))))

        self.assertEqual(
            query.compile(),
            'SELECT t1.col1 FROM t1 WHERE ( ( t1.col2 > t1.col1 ) ) AND ( ( '
            't1.id1 IN ( SELECT t2.id2 FROM t2 WHERE ( ( t2.val1 = 123 ) ) '
            'AND ( ( t2.val2 IN ("a") ) ) ) ) );')


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


class TestQueries(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect('tests/db.sqlite3')
        self.cursor = self.connection.cursor()
        self.states = PDTable('states', cursor=self.cursor)
        self.counties = PDTable('counties', cursor=self.cursor)
        self.senators = PDTable('senators', cursor=self.cursor)
        self.committees = PDTable('committees', cursor=self.cursor)

    def test_query01(self):
        print('Query 1')
        c = self.counties
        counties = reversed(
            c.where(c.population_2010 > 2000000)
             .select(c.statecode, c.name, c.population_2010)
             .order(c.population_2010))
        print(counties)
        print('')
        for county in counties.run():
            print('{}|{}|{}'.format(county[0], county[1], county[2]))

    def test_query02(self):
        print('\nQuery 2')
        c = self.counties
        counties = c.group(c.statecode) \
                    .select(c.statecode, c.count()) \
                    .order(c.count())
        print(counties)
        print('')
        for county in counties.run():
            print('{}|{}'.format(county[0], county[1]))

    def test_query03(self):
        print('\nQuery 3')
        c = self.counties
        nc = PDTable(c.group(c.statecode).select(('num_counties', c.count())))
        avg_num_counties = nc.select(nc.num_counties.avg())
        print(avg_num_counties)
        print('')
        print(avg_num_counties.run().fetchall()[0][0])

    def test_query04(self):
        print('\nQuery 4')
        c = self.counties
        nc = PDTable(c.group(c.statecode).select(('num_counties', c.count())))
        avg_num_counties = nc.select(nc.num_counties.avg())
        avg_nc = avg_num_counties.run().fetchall()[0][0]
        st = PDTable(c.group(c.statecode)
                      .having(c.count() > avg_nc)
                      .select(('num_states', c.statecode)))
        num_states = st.select(st.num_states.count())
        print(num_states)
        print('')
        print(num_states.run().fetchall()[0][0])

    def test_query05(self):
        print('\nQuery 5')
        c = self.counties
        s = self.states
        pop_sums = c.where(c.statecode == s.statecode) \
                    .select(c.population_2010.sum())
        statecodes = s.where(s.population_2010 != pop_sums) \
                      .select(s.statecode)
        print(statecodes)
        print('')
        for statecode in statecodes.run():
            print(statecode[0])

    def test_query6(self):
        # TODO: once EXISTS is implemented
        pass

    # Skip query 7 because it uses strfitme which isn't implemented

    def test_query08(self):
        print('\nQuery 8')
        c = self.counties
        s = self.states
        counties = c.join(s, cond=s.statecode == c.statecode) \
                    .where((s.statecode == 'WV')
                           & (c.population_1950 > c.population_2010)) \
                    .select(c.name, c.population_1950 - c.population_2010)
        print(counties)
        print('')
        for county in counties.run():
            print('{}|{}'.format(county[0], county[1]))

    def test_query09(self):
        print('\nQuery 9')
        se = self.senators
        c = self.committees
        chairmen = se.join(c, cond=c.chairman == se.name) \
                     .group(se.statecode)
        nc = PDTable(chairmen.select(('num_chairmen', se.count())))
        max_chairmen = nc.select(nc.num_chairmen.max()).run().fetchall()[0][0]
        statecodes = chairmen.having(se.count() == max_chairmen) \
                             .select(se.statecode)
        print(statecodes)
        print('')
        for statecode in statecodes.run():
            print(statecode[0])

    def test_query10(self):
        print('\nQuery 10')
        se = self.senators
        st = self.states
        c = self.committees
        st_with_chairmen = se.join(c, se.name == c.chairman) \
                             .select(se.statecode)
        statecodes = st.where(~st.statecode.in_(st_with_chairmen)) \
                       .select(st.statecode)
        print(statecodes)
        print('')
        for statecode in statecodes.run():
            print(statecode[0])

    def test_query11(self):
        print('\nQuery 11')
        pc = PDTable('committees', alias='pc', cursor=self.cursor)
        sc = PDTable('committees', alias='sc', cursor=self.cursor)
        subcommittees = sc.join(pc, cond=(pc.id == sc.parent_committee)
                                & (pc.chairman == sc.chairman)) \
                          .select(pc.id, pc.chairman, sc.id, sc.chairman)
        print(subcommittees)
        print('')
        for sub in subcommittees.run():
            print('{}|{}|{}|{}'.format(sub[0], sub[1], sub[2], sub[3]))

    def test_query12(self):
        print('\nQuery 12')
        pc = PDTable('committees', alias='pc', cursor=self.cursor)
        sc = PDTable('committees', alias='sc', cursor=self.cursor)
        s1 = PDTable('senators', alias='s1', cursor=self.cursor)
        s2 = PDTable('senators', alias='s2', cursor=self.cursor)
        values = sc.join(pc, cond=pc.id == sc.parent_committee) \
                   .join(s1, cond=s1.name == pc.chairman) \
                   .join(s2, cond=s2.name == sc.chairman) \
                   .where(s1.born > s2.born) \
                   .select(pc.id, pc.chairman, s1.born, sc.id, sc.chairman,
                           s2.born)
        print(values)
        print('')
        for val in values.run():
            print('{}|{}|{}|{}|{}'.format(
                val[0], val[1], val[2], val[3], val[4]))

    def tearDown(self):
        self.connection.close()


if __name__ == '__main__':
    unittest.main()
