import copy


class PDColumn(object):

    # General list available to all PDColumn instances
    aggregate_list = (
        '_sum', '_avg', '_count', '_first', '_last', '_max', '_min'
    )

    # Unary mathematical operators.
    #
    # These will be available both as chained methods, e.g.,
    # col.abs() and as built in functions, e.g., abs(col)
    unary_list = (
        '_abs', '_ceil', '_floor', '_round', '_not'
    )

    # Binary operators.
    #
    # These will be available using raw python syntax when possible, e.g.,
    # col1 + col2, with the exception of methods like concat which have no
    # raw equivalent.
    binary_list = (
        '_add', '_sub', '_mul', '_div', '_mod', '_concat', '_or', '_and',
        '_eq', '_ne', '_lt', '_gt', '_le', '_ge', '_in', '_between', '_like'
    )

    def __init__(self, name='Column', table=None):
        """
        Initializes column to be empty. Optional table argument allows
        creator to specify the base table if necessary.
        """
        self.agg = None
        self.unary_op = None
        self._binary_op = None
        self.null = None

        if name == '*':
            self._count = True
        else:
            self._count = False

        self.table = table
        self.name = name
        self._children = []
        self.ops = []

    ################################################################
    # Evaluation methods
    ################################################################

    def __str__(self):
        """
        Returns string representation of this column (in terms of table+column
        for users).
        """
        s = self.name
        if self.table:
            s += '(' + str(self.table.name) + ')'
        if self.agg:
            s += ' agg:' + self.agg
        if self.unary_op:
            s += ' unary:' + self.unary_op
        if self._binary_op:
            s += ' binary:' + self._binary_op
        return s

    def _repr_helper(self, level=0):
        s = "\t" * level
        s += str(self)
        s += "\n"
        for child in self._children:
            if isinstance(child, PDColumn):
                s += child._repr_helper(level=level + 1)
            else:
                s += "\t" * (level + 1) + repr(child)
        return s

    def __repr__(self):
        """
        Returns a string representation of this column (in terms of AST for
        devs).
        """
        return str(self)

    def __unicode__(self):
        """
        Same as __str__.
        """
        return str(self)

    ################################################################
    # Aggregation Methods
    #
    # Invariant: Only one can be active at a time.
    # Can only be used in SELECT and HAVING.
    ################################################################

    def has_aggregate(self):
        """
        Returns true if column has an aggregate function set. False otherwise.
        """
        return bool(self.agg)

    def _set_aggregate(self, agg):
        """
        Helper function to set aggregate function, validating and doing any
        bookkeeping necessary.
        """
        if self.has_aggregate():
            raise Exception('Attempting to assign multiple aggregate functions \
                to same column')

        elif agg not in PDColumn.aggregate_list:
            raise Exception('Attempting to assign invalid aggregate function')

        else:
            new_col = copy.copy(self)
            new_col.agg = agg
            setattr(new_col, agg, True)
            new_col.ops.append(agg)
            return new_col

    def sum(self):
        return self._set_aggregate('_sum')

    def avg(self):
        return self._set_aggregate('_avg')

    def count(self):
        return self._set_aggregate('_count')

    def first(self):
        return self._set_aggregate('_first')

    def last(self):
        return self._set_aggregate('_last')

    def max(self):
        return self._set_aggregate('_max')

    def min(self):
        return self._set_aggregate('_min')

    ################################################################
    # Unary Math Methods
    ################################################################

    def has_unary(self):
        """
        Returns true if column has an aggregate function set. False otherwise.
        """
        return bool(self.unary_op)

    def _set_unary(self, op):
        """
        Helper function to set unary math ops, validating and doing any
        bookkeeping necessary.
        """
        if op not in PDColumn.unary_list:
            raise Exception('Attempting to assign invalid unary function')

        else:
            new_col = copy.copy(self)
            new_col.unary_op = op
            setattr(new_col, op, True)
            new_col.ops.append(op)
            return new_col

    def __abs__(self):
        return self._set_unary('_abs')

    def abs(self):
        return self._set_unary('_abs')

    def __ceil__(self):
        return self._set_unary('_ceil')

    def ceil(self):
        return self._set_unary('_ceil')

    def __floor__(self):
        return self._set_unary('_floor')

    def floor(self):
        return self._set_unary('_floor')

    def __round__(self):
        return self._set_unary('_round')

    def round(self):
        return self._set_unary('_round')

    def __invert__(self):
        return self._set_unary('_not')

    ################################################################
    # Binary Math Methods
    #
    # Returns a new PDColumn object that represents the combined
    # operation. For instance, col1 + col2 will return a new
    # PDColumn instance that points
    #
    # Invariant: Only one binary op exists, exactly 2 children
    ################################################################

    def has_binary(self):
        """
        Returns true if column has an binary op set. False otherwise.
        """
        return bool(self._binary_op)

    def _set_binary(self, op, other):
        """
        Helper function to set binary ops, validating and doing any
        bookkeeping necessary.
        """
        if op not in PDColumn.binary_list:
            raise Exception('Attempting to assign invalid binary function')

        else:
            new_col = PDColumn()
            new_col._binary_op = op
            setattr(new_col, op, True)

            c1 = copy.copy(self)
            c2 = copy.copy(other)

            new_col._children.append(c1)
            new_col._children.append(c2)
            return new_col

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

    ################################################################
    # Null Checking Methods
    #
    # Invariant: Only one null checking method can be called
    ################################################################

    def has_null(self):
        """
        Returns true if column has null set. False otherwise.
        """
        return self.null is not None

    def _set_is_null(self, null):
        """
        Helper function to set is null, validating and doing any
        bookkeeping necessary.
        """
        if self.has_null():
            raise Exception('Already checking column for null values')

        new_col = copy.copy(self)
        new_col.null = null
        return new_col

    def is_null(self):
        return self._set_is_null(True)

    def not_null(self):
        return self._set_is_null(False)
