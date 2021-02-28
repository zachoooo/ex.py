import sys

import lark
import traceback

GRAMMAR = r"""
start: stmt_list
stmt_list: stmt | stmt_list "\n" stmt |
?stmt: quit_stmt | assign_stmt | return_stmt | delete_stmt
return_stmt: "return" exp_list | exp_list
assign_stmt: factor "=" exp_list
delete_stmt: "del" factor
quit_stmt: "quit"
?exp: ternary_exp
?exp_list: exp_list "," exp | exp
?ternary_exp: ternary_exp "if" ternary_exp "else" ternary_exp | concat_exp
?concat_exp: exp "&" rel_exp | rel_exp
?rel_exp: rel_exp REL_OP sum_exp | sum_exp
?sum_exp: sum_exp SUM_OP mul_exp | mul_exp
?mul_exp: mul_exp MUL_OP factor | factor
REL_OP: ">=" | "<=" | "<>" | "=" | ">" | "<"
SUM_OP: "+" | "-"
MUL_OP: "*" | "/"
?factor: immutable | mutable 
mutable: SYMBOL
immutable: constant | call | "(" exp ")"
call: EXCEL_SYMBOL "(" call_args ")"
?call_args: call_args_list | 
?call_args_list: call_args_list "," exp | exp
constant: CELL | CELL_RANGE | BOOL | NUMBER | ESCAPED_STRING | SHEET

SYMBOL: LETTER_OR_UNDERSCORE (ALPHA_NUM | "_" )*
EXCEL_SYMBOL: LETTER LETTER*
CELL: "$"? LETTER~1..3 "$"? NUMBER
CELL_RANGE: CELL ":" CELL
CELL_OR_RANGE: CELL_RANGE | CELL
SHEET: ALPHA_NUM "!" CELL_OR_RANGE | /'[^']+'!/ CELL_OR_RANGE

LETTER_OR_UNDERSCORE: LETTER | "_"
LETTER: "a".."z" | "A".."Z"
BOOL: "TRUE" | "FALSE"
ALPHA_NUM: (LETTER | "0".."9")+

%import common.NUMBER
%import common.ESCAPED_STRING
%import common.WS
%ignore WS
"""
DEBUG = False

symbol_table = {}
input_code = ""

def dbg_print(str):
    if DEBUG:
        print(str)

def err(str):
    print(f"ERROR: {str}")

def get_deepest_child(tree):
    if tree is None:
        return None
    visitor = tree
    while isinstance(visitor, lark.Tree):
        visitor = visitor.children[0]
    return visitor

def traverse(tree, interpreted=False):
    global input_code
    is_tree = isinstance(tree, lark.Tree)
    if is_tree:
        dbg_print(f"Checking tree {tree.data}")
        t = tree.data
        if t == "assign_stmt":
            child = get_deepest_child(tree)
            var = child.value
            dbg_print(f"Type is: {child.type}")
            if child.type == "CELL":
                err(f"Variable {var} could collide with a valid cell!")
                return ""
            elif child.type != "SYMBOL":
                err(f"Left hand side is not assignable!")
                return ""
            symbol_table[var] = traverse(tree.children[1], interpreted)
            dbg_print(symbol_table)
            return ""
        elif t == "delete_stmt":
            child = get_deepest_child(tree)
            var = child.value
            if child.type != "SYMBOL":
                err(f"Cannot delete constant {var}!")
                return ""
            elif not var in symbol_table:
                err(f"Cannot delete undefined variable {var}!")
                return ""
            del symbol_table[var]
            dbg_print(symbol_table)
            print(f"Deleted variable {var}.")
            return ""
        elif t == "quit_stmt":
            print("Exiting ex.py... Goodbye!")
            quit()
        elif t == "constant":
            return traverse(tree.children[0], interpreted)
        elif t == "call":
            call_name = traverse(tree.children[0], interpreted)
            args = traverse(tree.children[1], interpreted)
            args = args if args else ""
            return call_name + "(" + args + ")"
        elif t == "call_args_list":
            s = ""
            for child in tree.children:
                s += traverse(child, interpreted) + ","
            return s[:-1]
        elif t == "exp_list":
            s = ""
            for child in tree.children:
                s += traverse(child, interpreted) + ","
            return s[:-1]
        elif t == "ternary_exp":
            return "IF(" + traverse(tree.children[1], interpreted) + "," + traverse(tree.children[0], interpreted) + "," + traverse(tree.children[2], interpreted) + ")"
        elif t == "concat_exp":
            return traverse(tree.children[0], interpreted) + "&" + traverse(tree.children[1], interpreted)
        elif t == "return_stmt":
            s = "="
            for child in tree.children:
                s += traverse(child, interpreted)
            if not interpreted:
                visitor = get_deepest_child(tree)
                line = visitor.line
                print(f"Found return on line {line}: \"{input_code.splitlines()[line - 1]}.\" Result is:")
            print(s)
            print()
            return ""
        else: # Default behavior is just to process children
            s = ""
            for sub_tree in tree.children:
                s+= traverse(sub_tree, interpreted)
            return s
    else:
        val = tree.value
        dbg_print(f"Checking token {val}, type: {tree.type}")
        if tree.type == "SYMBOL":  
            if val in symbol_table:
                val = symbol_table[val]
            else:
                print(f"WARNING: Received symbol {val}, but it doesn't seem to be defined.")
        return val

def parse_process(input_string, interpreted=False):
    parser = lark.Lark(GRAMMAR, parser="earley")
    try:
        tree = parser.parse(input_string)
        traverse(tree, interpreted=interpreted)
    except Exception as e:
        print("An error occurred while parsing input!")
        traceback.print_exc() if DEBUG else print(e)
    return

def intrepreter():
    global input_code
    while True:
        try:
            input_code = input("> ")
            if not input_code:
                raise EOFError
        except EOFError:
            return
        parse_process(input_code, interpreted=True)


def main():
    global input_code
    s = ""
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        try:
            with open(file_name, 'r') as f:
                input_code = f.read()
        except IOError as e:
            print(f"Unable to open file \"{file_name}\"!")
            print(f"ERROR: {e}")
            return
    else:
        print("No input files detected. Enter code manually:")
        intrepreter()
    print()
    parse_process(input_code)

if __name__ == "__main__":
    main()