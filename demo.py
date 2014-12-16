import sqlite3
from PDTable import PDTable

connection = sqlite3.connect('tests/db.sqlite3')
cursor = connection.cursor()

s = PDTable('states', cursor=cursor)
c = PDTable('counties', cursor=cursor)
se = PDTable('senators', cursor=cursor)
co = PDTable('committees', cursor=cursor)

counties = reversed(
    c.where(c.population_2010 > 2000000)
     .select(c.statecode, c.name, c.population_2010)
     .order(c.population_2010))
print(counties.compile())
print('')
print(counties)

counties = c.group(c.statecode) \
            .select(c.statecode, c.count()) \
            .order(c.count())
print(counties.compile())
print('')
print(counties)

nc = PDTable(c.group(c.statecode).select(('num_counties', c.count())))
avg_num_counties = nc.select(nc.num_counties.avg())
print(avg_num_counties.compile())
print('')
print(avg_num_counties)

nc = PDTable(c.group(c.statecode).select(('num_counties', c.count())))
avg_num_counties = nc.select(nc.num_counties.avg())
avg_nc = avg_num_counties.run().fetchall()[0][0]
st = PDTable(c.group(c.statecode)
              .having(c.count() > avg_nc)
              .select(('num_states', c.statecode)))
num_states = st.select(st.num_states.count())
print(num_states.compile())
print('')
print(num_states)

pop_sums = c.where(c.statecode == s.statecode) \
            .select(c.population_2010.sum())
statecodes = s.where(s.population_2010 != pop_sums) \
              .select(s.statecode)
print(statecodes.compile())
print('')
print(statecodes)

counties = c.join(s, cond=s.statecode == c.statecode) \
            .where((s.statecode == 'WV')
                   & (c.population_1950 > c.population_2010)) \
            .select(c.name, c.population_1950 - c.population_2010)
print(counties.compile())
print('')
print(counties)

chairmen = se.join(co, cond=co.chairman == se.name) \
             .group(se.statecode)
nc = PDTable(chairmen.select(('num_chairmen', se.count())))
max_chairmen = nc.select(nc.num_chairmen.max()).run().fetchall()[0][0]
statecodes = chairmen.having(se.count() == max_chairmen) \
                     .select(se.statecode)
print(statecodes.compile())
print('')
print(statecodes)

st_with_chairmen = se.join(co, se.name == co.chairman) \
                     .select(se.statecode)
statecodes = s.where(~s.statecode.in_(st_with_chairmen)) \
              .select(s.statecode)
print(statecodes.compile())
print('')
print(statecodes)

pc = PDTable('committees', alias='pc', cursor=cursor)
sc = PDTable('committees', alias='sc', cursor=cursor)
subcommittees = sc.join(pc, cond=(pc.id == sc.parent_committee)
                        & (pc.chairman == sc.chairman)) \
                  .select(pc.id, pc.chairman, sc.id, sc.chairman)
print(subcommittees.compile())
print('')
print(subcommittees)

s1 = PDTable('senators', alias='s1', cursor=cursor)
s2 = PDTable('senators', alias='s2', cursor=cursor)
values = sc.join(pc, cond=pc.id == sc.parent_committee) \
           .join(s1, cond=s1.name == pc.chairman) \
           .join(s2, cond=s2.name == sc.chairman) \
           .where(s1.born > s2.born) \
           .select(pc.id, pc.chairman, s1.born, sc.id, sc.chairman,
                   s2.born)
print(values.compile())
print('')
print(values)
