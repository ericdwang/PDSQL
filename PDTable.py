
import copy
from PDColumn import PDColumn

class PDTable:

    # List of valid operations
    operations = [ '_limit', '_where', '_select', '_group', \
                   '_join', '_having', '_order']

    def __init__(self, name):
        '''
        Initializes tables to be empty. Requires name
        '''
        self.name = name

        # List of tuples in order of operation (operation, column)
        self._operation_ordering = []

        self.reverse_val = False

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
            elif op == '_select':
                for d in col:
                    n = ""
                    if 'name' in d:
                        n += 'key=' + str(d['name']) + ' '
                    b = "\t"*(level+1) + n + str(d['column'])
                    s += b + '\n'
            else:
                s += "\t"*(level+1) + str(col)
            s += "\n"
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
        join_dict = {'table':tableB, 'cond':cond}
        return self._set_query('_join', join_dict)

    def having(self, column):
        return self._set_query('_having', column)

    def order(self, column):
        return self._set_query('_order', column)

    def reverse(self):
        new_table = copy.deepcopy(self)
        new_table.reverse_val = True
        return new_table

    # select is a special case because can have multiple columns with single query
    def select(self, *args):
        table_copy = copy.deepcopy(self)
        columns = []
        for column in args:
            if isinstance(column, tuple):
                columns.append({'name': column[0], 'column' : column[1]})
            else:
                columns.append({'column' : column})
        operation = ("_select", columns)
        table_copy._operation_ordering.append(operation)
        return table_copy

    ################################################################
    # Magic methods
    ################################################################

    # NOTE: This breaks a lot of things if you're not careful.
    # It should be an invariant that you cannot define non-columns as attributes
    # since this method is being used to create PDColumns when they aren't found
    def __getattr__(self, name):
        return PDColumn(name, self)

    def __getitem__(self, key):
        if type(key) == str:
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
        return new_table

    def __nonzero__(self):
        # Always truthy if this exists.
        return True

