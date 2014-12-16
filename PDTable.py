import copy

from PDColumn import PDColumn
from PDCompiler import compile_to_sql


class PDTable(object):

    # List of valid operations
    operations = (
        '_limit', '_where', '_select', '_group', '_join', '_having', '_order',
        '_where_exists'
    )

    # Binary operators.
    #
    # These will be available using raw python syntax when possible, e.g.,
    # col1 + col2, with the exception of methods like concat which have no
    # raw equivalent.
    binary_list = (
        '_add', '_sub', '_mul', '_div', '_mod', '_concat', '_or', '_and',
        '_eq', '_ne', '_lt', '_gt', '_le', '_ge', '_in', '_between', '_like',
        '_union', '_intersect', '_except'
    )

    def __init__(self, name, alias=None, cursor=None):
        """
        Initializes tables to be empty. Requires name, database cursor optional.

        If verbose is True, the compiled SQL query will be printed along with
        the results.
        """
        # Can either be a string referencing an actual table or another
        # PDTable referencing a subquery
        self._name = name
        self._alias = alias
        if isinstance(name, PDTable):
            self._cursor = name._cursor
        else:
            self._cursor = cursor

        # List of tuples in order of operation (operation, column)
        self._operation_ordering = []

        self._reverse_val = False
        self._distinct = False
        self._limit = None
        self._binary_op = None
        self._children = []

        self._compiled = False
        self._query = None

    def __str__(self):
        """
        Compile the query and print it.
        """
        self.compile()
        return self._query

    def _repr_helper(self, level=0):
        s = "\t" * level
        s += self._name + "\n"

        for opTup in self._operation_ordering:
            op = opTup[0]
            col = opTup[1]
            s += "\t" * (level + 1) + op + ": \n"
            if op == '_join':
                b = col._repr_helper(level=level + 1)
                s += "\t" + b
            elif op == '_select':
                for d in col:
                    n = ""
                    if 'name' in d:
                        n += 'key=' + str(d['name']) + ' '
                    b = "\t" * (level + 1) + n + str(d['column'])
                    s += b + '\n'
            else:
                s += "\t" * (level + 1) + str(col)
            s += "\n"
        return s

    def __repr__(self, level=0):
        """
        Returns a string representation of this table for debugging purposes.
        """
        return str(self)

    def __unicode__(self):
        """
        Same as __str__.
        """
        return str(self)

    ################################################################
    # Database methods
    ################################################################

    def set_cursor(self, cursor):
        """
        Set the database cursor for this table to be used for executing queries.
        """
        execute_method = getattr(cursor, 'execute')
        if not callable(execute_method):
            raise Exception(
                'Database connector does not have an execute method')
        self._cursor = cursor

    def compile(self):
        """
        Compile the underlying query to SQL, checking first if it was already
        compiled.
        """
        if not self._compiled:
            self._query = compile_to_sql(self)
            self._compiled = True
        return self._query

    def run(self):
        """
        Compile the query, run it, and return the results.
        """
        if not self._cursor:
            raise Exception(
                'Attempting to execute query without setting database cursor '
                'first')

        self.compile()
        return self._cursor.execute(self._query)

    ################################################################
    # Query methods
    ################################################################

    def has_query(self, query):
        return query in dict(self._operation_ordering)

    def _set_query(self, query, column):
        if query not in PDTable.operations:
            raise Exception("Unsupported query: " + query)
        table_copy = copy.deepcopy(self)
        table_copy._operation_ordering.append((query, column))
        return table_copy

    def _check_aggregate(self, column, clause):
        if isinstance(column, PDColumn) and column.has_aggregate():
            raise Exception(
                'Aggregation in {} clause not allowed'.format(clause))

    def limit(self, lim):
        if not isinstance(lim, int):
            raise Exception('Only integers accepted in LIMIT clause')
        if self._limit is not None:
            raise Exception('Only one LIMIT clause allowed in queries')

        new_table = copy.deepcopy(self)
        new_table._limit = lim
        return new_table

    def where(self, column):
        self._check_aggregate(column, 'WHERE')
        return self._set_query('_where', column)

    def where_exists(self, tableB):
        if not isinstance(tableB, PDTable):
            raise Exception('Only tables accepted in WHERE EXISTS clause')
        return self._set_query('_where_exists', tableB)

    def group(self, column):
        self._check_aggregate(column, 'GROUP BY')
        return self._set_query('_group', column)

    def join(self, tableB, cond=None):
        if not isinstance(tableB, PDTable):
            raise Exception('Only tables accepted in JOIN clause')
        join_dict = {'table': tableB, 'cond': cond}
        return self._set_query('_join', join_dict)

    def having(self, column):
        return self._set_query('_having', column)

    def order(self, column):
        return self._set_query('_order', column)

    def __reversed__(self):
        return self.reverse()

    def reverse(self):
        new_table = copy.deepcopy(self)
        new_table._reverse_val = not self._reverse_val
        return new_table

    # select is a special case because can have multiple columns with single
    # query
    def select(self, *args):
        # Doesn't affect the query
        if len(args) == 0:
            return self

        table_copy = copy.deepcopy(self)
        columns = []
        for column in args:
            if isinstance(column, tuple):
                columns.append({'name': column[0], 'column': column[1]})
            else:
                columns.append({'column': column})

        operation = ("_select", columns)
        table_copy._operation_ordering.append(operation)
        return table_copy

    def distinct(self):
        new_table = copy.deepcopy(self)
        new_table._distinct = True
        return new_table

    def count(self):
        """Returns a PDColumn equal to COUNT(*)."""
        return PDColumn('*', self).count()

    ################################################################
    # Magic methods
    ################################################################

    # NOTE: This breaks a lot of things if you're not careful.
    # It should be an invariant that you cannot define non-columns as attributes
    # since this method is being used to create PDColumns when they aren't
    # found
    def __getattr__(self, name):
        return PDColumn(name, self)

    def __getitem__(self, key):
        # Getting a column
        if isinstance(key, str):
            return PDColumn(key, self)

        # Getting the first or last row
        elif isinstance(key, int):
            if key == 0:
                return self.limit(1)
            elif key == -1:
                table_copy = copy.deepcopy(self)
                table_copy._reverse_val = not self._reverse_val
                table_copy._limit = 1
                return table_copy
            else:
                raise Exception(
                    'Getting a single row that is not the first or last row is '
                    'unsupported.')

        # Getting the first or last n rows
        elif isinstance(key, slice):
            if not key.start and key.stop > 0:
                return self.limit(key.stop)
            elif key.start < 0 and not key.stop:
                table_copy = copy.deepcopy(self)
                table_copy._reverse_val = not self._reverse_val
                table_copy._limit = abs(key.start)
                return table_copy

        else:
            raise Exception("Attempting to get column with non-string key")

    def __copy__(self):
        new_table = PDTable(self._name)
        new_table.__dict__.update(self.__dict__)
        return new_table

    def __deepcopy__(self, memo):
        new_table = PDTable(self._name)
        new_table._reverse_val = copy.copy(self._reverse_val)
        new_table._distinct = copy.copy(self._distinct)
        new_table._operation_ordering = copy.copy(self._operation_ordering)
        new_table._cursor = self._cursor
        new_table._compiled = False
        new_table._binary_op = copy.copy(self._binary_op)
        new_table._children = copy.copy(self._children)
        new_table._limit = copy.copy(self._limit)
        new_table._alias = copy.copy(self._alias)
        return new_table

    def __nonzero__(self):
        # Always truthy if this exists.
        return True

    ################################################################
    # Binary Math Methods
    #
    # Returns a new PDTable object that represents the combined
    # operation. For instance, table1 + table2 will return a new
    # PDTable instance that points
    #
    # Invariant: Only one binary op exists, exactly 2 children
    ################################################################

    def has_binary(self):
        """
        Returns true if column has an binary op set. False otherwise.
        """
        return bool(self.binary_op)

    def _set_binary(self, op, other):
        """
        Helper function to set binary ops, validating and doing any
        bookkeeping necessary.
        """
        if op not in PDTable.binary_list:
            raise Exception('Attempting to assign invalid binary function')

        else:
            new_table = PDTable(self._name)
            new_table._binary_op = op
            setattr(new_table, op, True)

            t1 = copy.copy(self)
            t2 = copy.copy(other)

            new_table._children.append(t1)
            new_table._children.append(t2)
            return new_table

    def _check_table(self, table, clause):
        if not isinstance(table, PDTable):
            raise Exception(
                'Only subqueries accepted in {} clause'.format(clause))

    def __add__(self, other):
        return self._set_binary('_add', other)

    def __sub__(self, other):
        return self._set_binary('_sub', other)

    def __mul__(self, other):
        return self._set_binary('_mul', other)

    def __div__(self, other):
        return self._set_binary('_div', other)

    def __mod__(self, other):
        return self._set_binary('_mod', other)

    def __and__(self, other):
        return self._set_binary('_and', other)

    def __or__(self, other):
        return self._set_binary('_or', other)

    def concat(self, other):
        return self._set_binary('_concat', other)

    def __eq__(self, other):
        return self._set_binary('_eq', other)

    def __ne__(self, other):
        return self._set_binary('_ne', other)

    def __lt__(self, other):
        return self._set_binary('_lt', other)

    def __gt__(self, other):
        return self._set_binary('_gt', other)

    def __le__(self, other):
        return self._set_binary('_le', other)

    def __ge__(self, other):
        return self._set_binary('_ge', other)

    # in_ is used because 'in' is a keyword in python. You can override
    # the __contains__ operator, but it always casts results to bools.
    def in_(self, other):
        return self._set_binary('_in', other)

    def between(self, other):
        return self._set_binary('_between', other)

    def like(self, other):
        return self._set_binary('_like', other)

    def union(self, other):
        self._check_table(other, '_union')
        return self._set_binary('_union', other)

    def intersect(self, other):
        self._check_table(other, '_intersect')
        return self._set_binary('_intersect', other)

    # except_ is used because 'except' is a keyword in python.
    def except_(self, other):
        self._check_table(other, '_except')
        return self._set_binary('_except', other)
