
import PDTable

class PDColumn:

    # General list available to all PDColumn instances
    aggregate_list = ['_sum', '_avg', '_count', '_first', '_last', \
                      '_max', '_min']

    # Unary mathematical operators.
    #
    # These will be available both as chained methods, e.g.,
    # col.abs() and as built in functions, e.g., abs(col)
    unary_list = ['_abs', '_ceil', '_floor', '_round', '_not']


    # Binary operators.
    #
    # These will be available using raw python syntax when possible, e.g.,
    # col1 + col2, with the exception of methods like concat which have no
    # raw equivalent.
    binary_list = ['_add', '_sub', '_mul', '_div', '_mod', '_concat', \
                   '_or', '_and']
    
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
        self.binary_op = None
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
        return self

    def __ne__(self, other):
        self._ne.append(other)
        return self
            
    def __lt__(self, other):
        self._lt.append(other)
        return self
            
    def __gt__(self, other):
        self._gt.append(other)
        return self
            
    def __le__(self, other):
        self._le.append(other)
        return self
            
    def __ge__(self, other):
        self._ge.append(other)
        return self

            
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

    
    #TODO:  Determine if there is a case where this is necessary, instead of
    #       simply checking if a single variable is set.
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
            return self

    
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
    #
    # Invariant: Only one can be active at a time.
    ################################################################

    def has_unary_op(self):
        '''
        Returns true if column has an aggregate function set. False otherwise.
        '''
        return bool(self.unary_op)

    
    def _set_unary(self, op):
        """
        Helper function to set unary math ops, validating and doing any
        bookkeeping necessary.
        """
        if self._has_member_list(PDColumn.unary_list):
            raise Exception('Attempting to assign multiple math functions \
                to same column')
        else:
            self.unary_op = op
            setattr(self, op, True)
            return self

   
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

    def is_binary(self):
        '''
        Returns true if column has an binary op set. False otherwise.
        '''
        return bool(self.binary_op)
   
    
    def _set_binary(self, op, other):
        """
        Helper function to set binary ops, validating and doing any
        bookkeeping necessary.
        """
        if self._has_member_list(PDColumn.binary_list):
            raise Exception('Attempting to assign multiple binary functions \
                to same column')
        else:
            bin_col = PDColumn()
            bin_col.binary_op = op
            setattr(bin_col, op, True)
            bin_col.children.append(self)
            bin_col.children.append(other)
            return bin_col

    
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
    

