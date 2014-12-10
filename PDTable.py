
from PDColumn import PDColumn

class PDTable:

    # List of valid operations
    operations = [ '_limit', '_where', '_select', '_group', \
                   '_join', '_having']

    def __init__(self, name):
        '''
        Initializes tables to be empty. Requires name
        '''
        # Hash of columns
        self.table = {}
        self.name = name

        # Initialize internal variables as lists. Used to store columns
        # join can store tables
        self._operations = {}
        for op in PDTable.operations:
            self._operations[op] = []

        # List of tuples in order of operation (operation, column)
        self._operation_ordering = []

    def __str__(self):
        """
        Returns string representation of this table
        """
        raise NotImplementedError()


    def __repr__(self, level=0):
        """
        Returns a string representation of this table
        """
        s = "\t"*level
        s += self.name+"\n"

        for opTup in self._operation_ordering:
            op = opTup[0]
            col = opTup[1]
            s += "\t"*(level+1) + op + ": \n"
            if op == '_join':
                b = col.__repr__(level+1)
                s += "\t" + b
            else:
                #s += str(self._operations[op][count[op]])
                s += "\t"*(level+1) + str(col)
            s += "\n"
            #count[op] += 1
        return s

    def __unicode__(self):
        """
        Returns unicode representation of this column.
        """
        raise NotImplementedError()

    ################################################################
    # Query methods
    ################################################################

    def has_query(self, query):
        return not self._operations[query].isEmpty()

    def _set_query(self, query, column):
        if query not in PDTable.operations:
            raise Exception("Unsupported query: " + query)
        copy = self._copy_table()
        copy._operations[query].append(column)
        copy._operation_ordering.append((query, column))
        return copy

    def limit(self, lim):
        return self._set_query('_limit', lim)

    def where(self, column):
        return self._set_query('_where', column)

    def group(self, column):
        return self._set_query('_group', column)

    def join(self, tableB):
        return self._set_query('_join', tableB)

    def having(self, column):
        return self._set_query('_having', column)

    # select is a special case because can have multiple columns with single query
    def select(self, *args, **kwargs):
        copy = self._copy_table()
        for column in args:
            copy._operations['_select'].append((column.name, column))
        for name, column in kwargs.items():
            assert name == column.name # need to make sure we set the name during column creation
            copy._operations['_select'].append((column.name, column))
        operation = ("_select", column)
        copy._operation_ordering.append(operation)
        return copy

    ################################################################
    # Magic methods
    ################################################################

    def __getattr__(self, name):
        if name in self.table:
            column = self.table[name]
        else:
            column = PDColumn(name, self)
            self.table[name] = column
        return column

    def __getitem__(self, key):
        if type(key) == str:
            return self.table[key]
        else:
            return [v for k, v in self.table.iteritems() if k == key]

    ################################################################
    # Internal Methods
    ################################################################

    def _copy_table(self):
        copy = PDTable(self.name)
        for k, v in self.table:
            copy.table[k] = v
        for op in PDTable.operations:
            for lst in self._operations:
                for v in lst:
                    copy._operations[op].append(v)
        for op in self._operation_ordering:
            copy._operation_ordering.append(op)
        return copy
