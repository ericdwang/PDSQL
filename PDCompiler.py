
from PDColumn import PDColumn
from PDTable import PDTable

# Structure taken from Berkeley's Fall 2014 CS164 projects
def compile(ast):

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
                if node.binary_op == '_add':
                    strings = ['('] + children[0] + ['+'] + children[1] + [')']

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

            if node.agg:
                op = node.agg

                if op == '_sum':
                    strings = ['SUM('] + strings + [')']

                else:
                    raise Exception("AST column contains unrecognized unary op: "\
                             + op)


            if node.unary_op:
                op = node.unary_op

                if op == '_abs':
                    strings = ['ABS('] + strings + [')']

                else:
                    raise Exception("AST column contains unrecognized unary op: "\
                             + op)


        elif isinstance(node, PDTable):
            #TODO: Fill in
            raise NotImplementedError()

        else:
            strings = [str(node)]

        return strings


    return " ".join(compilenode(ast))


