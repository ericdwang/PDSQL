
import PDColumn

class PDTable:

    def __init__(self, name):
        '''
        Initializes tables to be empty. Requires name
        '''
        # Hash of columns
        self.table = {}
        self.name = name

        # Initialize internal variables as lists. Used to store columnrs
        _where = []
        _select = []
        _limit = []
        _group = []
        _join = []
        _having = []
        _operation_ordering = [] # list of tuples in order of operation

    def __str__(self):
        """
        Returns string representation of this table
        """
        raise NotImplementedError()


    def __repr__(self, level=0):
        """
        Returns a string representation of this table (in terms of AST for devs).
        """
        raise NotImplementedError()

    def __unicode__(self):
        """
        Returns unicode representation of this column.
        """
        raise NotImplementedError()

    ################################################################
    # Query methods
    ################################################################

    def limit(self, lim):
        self._limit.append(lim)
        operation = ("_limit", lim)
        _operation_ordering.append(operation)


    def where(self, column):
        self.table[column] = column
        self._where.append(column)
        operation = ("_where", column)
        _operation_ordering.append(operation)
        return self

    def select(self, *args, **kwargs):
        for column in args:
            self.table[column] = column
            self._select.append(column)
        for name, column in kwargs.items():
            self.table[column] = column
            self._select.append(column)
        operation = ("_select", column)
        _operation_ordering.append(operation)
        return self

    def group(self, column):
        self.table[column] = column
        _group.append(column)
        operation = ("_group", column)
        _operation_ordering.append(operation)
        return self

    def join(self, tableA, tableB):
        _join.append((tableA, tableB))
        operation = ("_join", column)
        _operation_ordering.append(operation)
        return self

    def having(self, column):
        self.table[column] = column
        self.having.append(column)
        operation = ("_having", column)
        _operation_ordering.append(operation)
        return self

    ################################################################
    # Magic methods
    ################################################################

    def __getattr__(self, name):
        return self.table[name]

    #def __setattr__(self, name, value):
    #    pass

    def __getitem__(self, key):
        if type(key) == str:
            return self.table[key]
        else:
            return [v for k, v in self.table.iteritems() if k == key]
