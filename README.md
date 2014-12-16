PDSQL (Python Domain Specific Query Language)
=====
Final project for CS 164 at UC Berkeley, Fall 2014.

## Deliverables:

 * [Project Proposal](https://docs.google.com/document/d/141D9-n_DV7kJmmUu6Ch9VDrfQ42T-PNHU5XS2sAAf6U/edit?usp=sharing)
 * [PA6 Report](https://docs.google.com/document/d/1ZgxrjlmODSQ0HYuyguPP62Qs30rfCEIC8Wv4gfYOfk0/edit?usp=sharing)
 * [Design Document](https://docs.google.com/document/d/18KWyiBUfb6JnDHI4QdIQ3IDjvp1p1BRbMfeMUomUEoQ/edit?usp=sharing)
 * [Presentation Slides](https://docs.google.com/presentation/d/15ugGxwreWVDfhtZbnlbXfS_V1FLOHQc8ooyohIpGIog/edit?usp=sharing)
 * [Poster Slides](https://docs.google.com/presentation/d/1MfunGSdlq9CQJbk0tnRBBW_2c2dXBeHhtk-6_XlGWXM/edit?usp=sharing)
 * [Demo Video](http://youtu.be/_Zlhz1kgxB0)

## Example Query

    import sqlite3
    from PDTable import PDTable

    # Connect to the database
    connection = sqlite3.connect('tests/db.sqlite3')
    cursor = connection.cursor()
    # Create a PDTable for the "counties" table
    c = PDTable('counties', cursor=cursor)

    # Get all the counties with a 2010 population greater than 2 million,
    # get their statecodes, names, and 2010 populations,
    # and show them in descending order by 2010 population
    counties = reversed(
        c.where(c.population_2010 > 2000000)
         .select(c.statecode, c.name, c.population_2010)
         .order(c.population_2010))

    # Print the compiled SQL statement
    print(counties.compile())
    # Print the actual results of running the query
    print(counties)
