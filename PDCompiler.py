
from PDColumn import PDColumn
from PDTable import PDTable

# Structure taken from Berkeley's Fall 2014 CS164 projects
def compile(ast):

    # Does not have not -- must be desugared down.
    unary_map = {
        '_sum':'SUM', '_avg':'AVG', '_count':'COUNT', '_first':'FIRST', \
        '_last':'LAST', '_max':'MAX', '_min':'MIN', \
        '_abs':'ABS', '_ceil':'CEIL', '_floor':'FLOOR', '_round':'ROUND'
    }

    binary_middle_map = {
        '_add':'+', '_sub':'-', '_mul':'*', '_div':'/', '_concat':'+', \
        '_or':'OR', '_and':'AND', '_eq':'=', '_ne':'<>', '_lt':'<', '_gt':'>', \
        '_le':'<=', '_ge':'>=', '_in':'IN', '_between':'BETWEEN', '_like':'LIKE'
    }

    binary_function_map = {
        '_mod':'MOD'
    }

    _uniquegen_counter = 0
    def uniquegen():
        _uniquegen_counter += 1
        return '#reg-' + str(_uniquegen_counter)

    def compilenode(node):
        strings = []
        children = []

        if isinstance(node, PDColumn):

            if len(node.children) > 0:
                children = [compilenode(child) for child in node.children]

                # Switch on all binary ops

                if node.binary_op in binary_middle_map:
                    strings = ['('] + children[0] + [binary_middle_map[node.binary_op]] + \
                            children[1] + [')']

                elif node.binary_op in binary_function_map:
                    strings = [binary_function_map[node.binary_op] + '('] + \
                            children[0] + [','] + children[1] + [')']

                else:
                    raise Exception("AST column contains unrecognized binary op: "\
                             + node.binary_op)


            # In the case where no children, fill strings with basic
            # information about the column.
            else:
                if hasattr(node.table, 'name'):
                    strings = [node.table.name + '.' + node.name]
                else:
                    strings = [node.name]

            # At this point, we have either a base column or some composition
            # of columns in 'strings'. Now we apply unary operators.

            # TODO: Determine if we need to maintain ordering on aggs and ops.
            # If so, we'll need to loop through node.ops. Ordering is there.

            # TODO: Push nots down AST next to condition (binary)

            for op in node.ops:
                if op in unary_map:
                    strings = [unary_map[op] + '('] + strings + [')']
                else:
                    raise Exception("AST column contains unrecognized unary op: "\
                             + op)

        elif isinstance(node, PDTable):
            #TODO: Fill in
            raise NotImplementedError()

        elif isinstance(node, tuple):
            new_elements = []
            for item in node:
                if isinstance(item, basestring):
                    new_elements += ['\'' + item + '\'']
                else:
                    new_elements += [str(item)]
            new_elements = ','.join(new_elements)
            strings = ['(' + new_elements + ')']

        elif isinstance(node, basestring):
            strings = ['\'' + node + '\'']

        else:
            strings = [str(node)]

        return strings


    return " ".join(compilenode(ast))


