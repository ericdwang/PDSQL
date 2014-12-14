import copy

from PDColumn import PDColumn
from PDCompiler import compile_to_sql


class PDTable(object):

    # List of valid operations
    operations = (
        '_limit', '_where', '_select', '_group', '_join', '_having', '_order'
    )

    def __init__(self, name, cursor=None):
        """
        Initializes tables to be empty. Requires name, database cursor optional.

        If verbose is True, the compiled SQL query will be printed along with
        the results.
        """
        self.name = name
        self.cursor = cursor

        # List of tuples in order of operation (operation, column)
        self._operation_ordering = []

        self.reverse_val = False

        self._compiled = False
        self.query = None

    def __str__(self):
        """
        Compile the query and print it.
        """
        if not self.cursor:
            raise Exception(
                'Attempting to execute query without setting database cursor '
                'first')

        self.compile()
        return self.query

    def __repr__(self, level=0):
        """
        Returns a string representation of this table for debugging purposes.
        """
        s = "\t" * level
        s += self.name + "\n"

        for opTup in self._operation_ordering:
            op = opTup[0]
            col = opTup[1]
            s += "\t" * (level + 1) + op + ": \n"
            if op == '_join':
                b = col.__repr__(level + 1)
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
        self.cursor = cursor

    def compile(self):
        """
        Compile the underlying query to SQL, checking first if it was already
        compiled.
        """
        if not self._compiled:
            self.query = compile_to_sql(self)
            self._compiled = True

    def run(self):
        """
        Compile the query, run it, and return the results.
        """
        if not self.cursor:
            raise Exception(
                'Attempting to execute query without setting database cursor '
                'first')

        self.compile()
        return self.cursor.execute(self.query)

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

    def limit(self, lim):
        return self._set_query('_limit', lim)

    def where(self, column):
        return self._set_query('_where', column)

    def group(self, column):
        return self._set_query('_group', column)

    def join(self, tableB, cond=None):
        join_dict = {'table': tableB, 'cond': cond}
        return self._set_query('_join', join_dict)

    def having(self, column):
        return self._set_query('_having', column)

    def order(self, column):
        return self._set_query('_order', column)

    def reverse(self):
        new_table = copy.deepcopy(self)
        new_table.reverse_val = True
        return new_table

    # select is a special case because can have multiple columns with single
    # query
    def select(self, *args):
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
        if isinstance(key, str):
            return PDColumn(key, self)
        else:
            raise Exception("Attempting to get column with non-string key")

    def __copy__(self):
        new_table = PDTable(self.name)
        new_table.__dict__.update(self.__dict__)
        return new_table

    def __deepcopy__(self, memo):
        new_table = PDTable(self.name)
        new_table.reverse_val = copy.copy(self.reverse_val)
        new_table._operation_ordering = copy.copy(self._operation_ordering)
        new_table.cursor = self.cursor
        new_table._compiled = False
        return new_table

    def __nonzero__(self):
        # Always truthy if this exists.
        return True
