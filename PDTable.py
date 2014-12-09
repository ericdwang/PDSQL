
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

    ################################################################
    # Query methods
    ################################################################

    def limit(self, lim):
        self._limit.append(lim)

    def where(self, column):
        self.table[column] = column
        self._where.append(column)
        return self

    def select(self, *args, **kwargs):
        for column in args:
            self.table[column] = column
            self._select.append(column)
        for name, column in kwargs.items():
            self.table[column] = column
            self._select.append(column)
        return self

    def group(self, column):
        self.table[column] = column
        _group.append(column)
        return self

    def join(self, tableA, tableB):
        _join.append((tableA, tableB))
        return self

    def having(self, column)
        self.table[column] = column
        self.having.append(column)
        return self

    ################################################################
    # Magic methods
    ################################################################

    def __getattr_(self, name):
        return self.table[name]

    def __getitem__(self, key):
        if type(key) == str:
            return self.table[key]
        else:
            return [v for k, v in self.table.iteritems() if k == key]
