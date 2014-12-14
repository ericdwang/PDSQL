import copy


# Does not have not -- must be desugared down.
unary_map = {
    '_sum': 'SUM',
    '_avg': 'AVG',
    '_count': 'COUNT',
    '_first': 'FIRST',
    '_last': 'LAST',
    '_max': 'MAX',
    '_min': 'MIN',
    '_abs': 'ABS',
    '_ceil': 'CEIL',
    '_floor': 'FLOOR',
    '_round': 'ROUND',
    '_not': 'NOT'
}

binary_middle_map = {
    '_add': '+',
    '_sub': '-',
    '_mul': '*',
    '_div': '/',
    '_concat': '+',
    '_or': 'OR',
    '_and': 'AND',
    '_eq': '=',
    '_ne': '<>',
    '_lt': '<',
    '_gt': '>',
    '_le': '<=',
    '_ge': '>=',
    '_in': 'IN',
    '_between': 'BETWEEN',
    '_like': 'LIKE'
}

binary_function_map = {
    '_mod': 'MOD'
}

_uniquegen_counter = 0


# Structure taken from Berkeley's Fall 2014 CS164 projects
def compile_to_sql(ast):
    # Import here to avoid circular imports
    from PDColumn import PDColumn
    from PDTable import PDTable

    def uniquegen():
        global _uniquegen_counter
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
                    strings = ['('] + children[0] + \
                        [binary_middle_map[node.binary_op]] + \
                        children[1] + [')']

                elif node.binary_op in binary_function_map:
                    strings = [binary_function_map[node.binary_op] + '('] + \
                        children[0] + [','] + children[1] + [')']

                else:
                    raise Exception(
                        "AST column contains unrecognized binary op: "
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

            for op in node.ops:
                if op in unary_map:
                    strings = [unary_map[op] + '('] + strings + [')']
                else:
                    raise Exception(
                        "AST column contains unrecognized unary op: "
                        + op)

        elif isinstance(node, PDTable):
            ops = node._operation_ordering

            # SELECT
            select_list = ['SELECT']
            for col_list in [i[1] for i in ops if i[0] == '_select']:
                for col in col_list:
                    s = []
                    if 'name' in col:
                        s += ['AS \"' + col['name'] + '\"']
                    s = compilenode(col['column']) + s
                    select_list += s + [',']
            select_list.pop()

            # FROM + JOIN
            join = [i[1] for i in ops if i[0] == '_join']

            from_list = ['FROM']

            if not join:
                from_list += [node.name]
            else:
                from_list += ['('] + [node.name] + ['INNER JOIN'] + \
                    [join['table'].name]
                if join['cond']:
                    from_list += ['ON'] + compilenode(join['cond'])
                from_list += [')']

            # WHERE
            where_list = ['WHERE']
            for col in [i[1] for i in ops if i[0] == '_where']:
                where_list += ['('] + compilenode(col) + [')'] + ['AND']
            where_list.pop()

            # GROUP BY
            group_list = ['GROUP BY']
            for col in [i[1] for i in ops if i[0] == '_group']:
                group_list += compilenode(col) + [',']
            group_list.pop()

            # HAVING
            having_list = ['HAVING']
            for col in [i[1] for i in ops if i[0] == '_having']:
                having_list += ['('] + compilenode(col) + [')'] + ['AND']
            having_list.pop()

            # ORDER
            order_list = ['ORDER BY']
            for col in [i[1] for i in ops if i[0] == '_order']:
                order_list += compilenode(col) + [',']
            order_list.pop()
            if node.reverse_val and len(order_list) > 0:
                order_list += ['DESC']
            else:
                order_list += ['ASC']

            # LIMIT TODO: Need to enforce only one limit
            limit_list = []
            for col in [i[1] for i in ops if i[0] == '_limit']:
                limit_list += ['LIMIT'] + compilenode(col)

            strings = select_list + from_list + where_list + group_list + \
                having_list + order_list + limit_list

        elif isinstance(node, tuple):
            new_elements = []
            for item in node:
                if isinstance(item, basestring):
                    new_elements += ['"' + item + '"']
                else:
                    new_elements += [str(item)]
            new_elements = ','.join(new_elements)
            strings = ['(' + new_elements + ')']

        elif isinstance(node, basestring):
            strings = ['"' + node + '"']

        else:
            strings = [str(node)]

        return strings

    def apply_children(node, func):
        if isinstance(node, PDColumn):
            func(node)
            for child in node.children:
                apply_children(child, func)

        elif isinstance(node, PDTable):
            func(node)
            ops = node._operation_ordering
            for op in ops:
                if op[0] == '_select':
                    for col in op[1]:
                        apply_children(col['column'], func)
                else:
                    apply_children(op[1], func)

        elif hasattr(node, '__iter__'):
            for child in node:
                apply_children(child, func)

    def rewrite_select(node):
        if isinstance(node, PDTable):
            ops = node._operation_ordering
            if len([i[1] for i in ops if i[0] == '_select']) == 0:
                node._operation_ordering.append(
                    ('_select', [{'column': PDColumn(name='*')}]))

    ast = copy.deepcopy(ast)
    apply_children(ast, rewrite_select)
    return " ".join(compilenode(ast)) + ';'
