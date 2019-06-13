from lark import Lark, Transformer
import sys

grammar = """
    start: instruction+
    ?instruction: assignment
                | while
                | if
                | function
                | for
    code_block: "{" instruction+ "}"
    
    ?logic_expression: logic1
                     | logic_expression "||" logic1 -> lor
    ?logic1: logic2
           | logic1 "&&" logic2 -> land
    ?logic2: "true" -> true
           | "false" -> false
           | "!" logic2 -> lnot
           | int_expression "<=" int_expression -> less_equal
           | int_expression ">=" int_expression -> bigger_equal
           | int_expression "<" int_expression -> less
           | int_expression ">" int_expression -> bigger
           | int_expression "==" int_expression -> equal 
           | "(" logic_expression ")"                   
                      
    ?int_expression: product
                   | int_expression "+" product -> add
                   | int_expression "-" product -> sub
    ?product: atom
            | product "*" atom -> mul
            | product "/" atom -> div
    ?atom: SIGNED_INT -> number
         | "-" atom -> unary_minus
         | var
         | int_function
         | "(" int_expression ")"
         
    ?var: NAME -> variable
        | NAME "[" int_expression "]" -> array
    ?assignment: NAME "=" int_expression -> variable_assignment
               | NAME "=" "[" int_expression "]" -> create_array
               | NAME "[" int_expression "]" "=" int_expression -> array_assignment
    ?while: "while" logic_expression code_block -> while_
    ?for: "for" "(" assignment ";" logic_expression ";" assignment ")" code_block -> for_
    ?if: "if" logic_expression code_block "else" code_block -> if_else
       | "if" logic_expression code_block -> if_
    ?function: "write" "(" var ")" -> write
             | "write" "(" ESCAPED_STRING ")" -> write_string
    ?int_function: "read" "(" ")" -> read
    
    %import common.CNAME -> NAME
    %import common.SIGNED_INT
    %import common.WS
    %import common.ESCAPED_STRING
    %ignore WS
"""

class Interpreter(Transformer):
    start = list
    code_block = list

    def lor(self, args):
        return lambda context: args[0](context) or args[1](context)

    def land(self, args):
        return lambda context: args[0](context) and args[1](context)

    def true(self, args):
        return lambda context: True

    def false(self, args):
        return lambda context: False

    def lnot(self, args):
        return lambda context: not args[0](context)

    def less_equal(self, args):
        return lambda context: args[0](context) <= args[1](context)

    def bigger_equal(self, args):
        return lambda context: args[0](context) >= args[1](context)

    def less(self, args):
        return lambda context: args[0](context) < args[1](context)

    def bigger(self, args):
        return lambda context: args[0](context) > args[1](context)

    def equal(self, args):
        return lambda context: args[0](context) == args[1](context)

    def add(self, args):
        return lambda context: args[0](context) + args[1](context)

    def sub(self, args):
        return lambda context: args[0](context) - args[1](context)

    def mul(self, args):
        return lambda context: args[0](context) * args[1](context)

    def div(self, args):
        return lambda context: args[0](context) / args[1](context)

    def number(self, args):
        return lambda context: int(args[0])

    def unary_minus(self, args):
        return lambda context: -args[0](context)

    def variable(self, args):
        return lambda context: context[str(args[0])]

    def array(self, args):
        return lambda context: context[str(args[0])][args[1](context)]

    def variable_assignment(self, args):
        def f(context):
            context[str(args[0])] = args[1](context)
        return f

    def create_array(self, args):
        def f(context):
            context[str(args[0])] = [0] * args[1](context)
        return f

    def array_assignment(self, args):
        def f(context):
            context[str(args[0])][args[1](context)] = args[2](context)
        return f

    def while_(self, args):
        def f(context):
            while args[0](context):
                for instr in args[1]:
                    instr(context)
        return f

    def for_(self, args):
        def f(context):
            args[0](context)
            while args[1](context):
                for instr in args[3]:
                    instr(context)
                args[2](context)
        return f
    def if_else(self, args):
        def f(context):
            if args[0](context):
                for instr in args[1]:
                    instr(context)
            else:
                for instr in args[2]:
                    instr(context)
        return f

    def if_(self, args):
        def f(context):
            if args[0](context):
                for instr in args[1]:
                    instr(context)
        return f


    def read(self, args):
        return lambda context: int(input())

    def write(self, args):
        def f(context):
            print(args[0](context))
        return f

    def write_string(self, args):
        def f(context):
            print(str(args[0])[1:-1])
        return f

def run(code):
    parser = Lark(grammar)
    tree = parser.parse(code)
    pseudo_virtual_machine_code = Interpreter().transform(tree)
    context = {}
    print("program starts")
    for instr in pseudo_virtual_machine_code:
        #print(instr)
        instr(context)
    print("program finished")


if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        run(f.read())