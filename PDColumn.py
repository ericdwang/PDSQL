
import PDTable

class PDColumn:

    # General list available to all PDColumn instances
    aggregate_list = ['_sum', '_avg', '_count', '_first', '_last', \
                  '_max', '_min']

    # Unary mathematical operators.
    #
    # These will be available both as chained methods, e.g.,
    # col.abs() and as built in functions, e.g., abs(col)
    unary_math_list = ['_abs', '_ceil', '_floor', '_round']

    
    def __init__(self, table=None):
        """
        Initializes column to be empty. Optional table argument allows
        creator to specify the base table if necessary.
        """

        # Initialize comparison lists
        # We use lists to allow for multiple comparisons on the same column
        self._eq = []
        self._ne = []
        self._lt = []
        self._gt = []
        self._le = []
        self._ge = []

        self.agg = None
        self.unary_op = None
        self._table = table
        self.children = []


    ################################################################
    # Evaluation methods
    ################################################################
    
    def evaluate(self):
        """
        Evaluates into AST and returns it.
        """
        raise NotImplementedError()


    def __str__(self):
        """
        Returns string representation of this column.
        """
        raise NotImplementedError()


    def __unicode__(self):
        """
        Returns unicode representation of this column.
        """
        raise NotImplementedError()


    ################################################################
    # Magic Methods for comparisons
    #
    # More than one at a time is legal, in case you wish to make
    # multiple comparisons, hence the list formats
    ################################################################

    def __eq__(self, other):
        self._eq.append(other)

    def __ne__(self, other):
        self._ne.append(other)
            
    def __lt__(self, other):
        self._lt.append(other)
            
    def __gt__(self, other):
        self._gt.append(other)
            
    def __le__(self, other):
        self._le.append(other)
            
    def __ge__(self, other):
        self._ge.append(other)

            
    ################################################################
    # Aggregation Methods
    #
    # Invariant: Only one can be active at a time.
    ################################################################
   
    def has_aggregate(self):
        '''
        Returns true if column has an aggregate function set. False otherwise.
        '''
        return bool(self.agg)

    
    def _has_member_list(self, l):
        """
        Helper function to see if any attributes in a list have been set yet.
        
        Returns false if there are none set, and true if there are.
        """
        for attr in l:
            if getattr(self, attr, False):
                return true
        
        return false
   
    
    def _set_aggregate(self, agg):
        """
        Helper function to set aggregate function, validating and doing any
        bookkeeping necessary.
        """
        if self._has_member_list(PDColumn.aggregate_list):
            #TODO:  Figure out how to deal with separate instances of
            #       aggregations called on same column.
            raise Exception('Attempting to assign multiple aggregate functions \
                to same column')
        else:
            self.agg = agg
            setattr(self, agg, True)

    
    def sum(self):
        self._set_aggregate('_sum')
    
    def avg(self):
        self._set_aggregate('_avg')

    def count(self):
        self._set_aggregate('_count')

    def first(self):
        self._set_aggregate('_first')

    def last(self):
        self._set_aggregate('_last')

    def max(self):
        self._set_aggregate('_max')

    def min(self):
        self._set_aggregate('_min')

    
    ################################################################
    # Unary Math Methods
    #
    # Invariant: Only one can be active at a time.
    ################################################################

    def has_unary_op(self):
        '''
        Returns true if column has an aggregate function set. False otherwise.
        '''
        return bool(self.unary_op)

    
    def _set_unary_math(self, op):
        """
        Helper function to set unary math ops, validating and doing any
        bookkeeping necessary.
        """
        if self._has_member_list(PDColumn.unary_math_list):
            raise Exception('Attempting to assign multiple math functions \
                to same column')
        else:
            self.unary_op = op
            setattr(self, op, True)

   
    def __abs__(self):
        _set_unary_math('_abs')
    def abs(self):
        _set_unary_math('_abs')

    def __ceil__(self):
        _set_unary_math('_ceil')
    def ceil(self):
        _set_unary_math('_ceil')

    def __floor__(self):
        _set_unary_math('_floor')
    def floor(self):
        _set_unary_math('_floor')

    def __round__(self):
        _set_unary_math('_round')
    def round(self):
        _set_unary_math('_round')


    ################################################################
    # Binary Math Methods
    #
    # Returns a new PDColumn object that represents the combined
    # operation. For instance, col1 + col2 will return a new
    # PDColumn instance that points
    #
    ################################################################

