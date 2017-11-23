
NAME = 0
NUMBER = 1
STRING = 2
OP = 3
IF = 4
WHILE = 5
END = 6
OUTPUT = 7
SUBROUTINE = 8
ARGS = 9
ASSIGN = 10
FOR = 11
ELSE = 12
INDEX = 13

backlog = '\0'
def get_type(name):
    if name == "IF":
        return IF
    elif name == "WHILE":
        return WHILE
    elif name == "END":
        return END
    elif name == "OUTPUT":
        return OUTPUT
    elif name == "SUBROUTINE":
        return SUBROUTINE
    elif name == "FOR":
        return FOR
    elif name == "ELSE":
        return ELSE
    return NAME

def read_name(f, c):
    global backlog
    name = ""
    while c.isalpha() or c.isdigit() or c == '.':
        name += c
        c = f.read(1).decode("ASCII")
    backlog = c
    return (name, get_type(name))

def read_number(f, c):
    global backlog
    number = ""
    dot_count = 0
    while c.isdigit() or c == '.':
        number += c
        if c == '.':
            dot_count += 1
        c = f.read(1).decode("ASCII")
    backlog = c

    if dot_count > 1:
        return None
    return (number, NUMBER)

def read_string(f, end_char):
    string = ""
    while True:
        c = f.read(1).decode("ASCII")
        if c == end_char:
            break
        string += c
    return string

def next_token(f):
    global backlog
    while True:
        c = backlog if backlog != '\0' else f.read(1).decode("ASCII")
        backlog = '\0'
        if not c:
            break

        if c in ['>', '<', '=']:
            temp = c
            c = f.read(1).decode("ASCII")
            if c == '-':
                return ("<-", ASSIGN)
            elif c == '=':
                return (temp + c, OP)
            c = temp

        if c.isalpha():
            return read_name(f, c)
        elif c.isdigit():
            return read_number(f, c)
        elif c == '"':
            return ('"' + read_string(f, '"') + '"', STRING)
        elif c == '(':
            return ('(' + read_string(f, ')') + ')', ARGS)
        elif c == '[':
            return ('[' + read_string(f, ']') + ']', INDEX)
        elif c in ['+', '-', '*', '/', '<', '>', '=']:
            return (c, OP)
    return None

look = None
def look_next(f):
    global look
    ret = look
    look = next_token(f)
    return ret

out = ""
def output(code, indent):
    global out
    out += ' '*indent*4 + code + '\n'

def parse_expression(f):
    global look
    left = look_next(f)[0]
    if not look:
        return left

    if look[1] == ARGS or look[1] == INDEX:
        left += look[0]
        look_next(f)
    
    if look[1] == OP:
        op = look_next(f)[0]
        right = parse_expression(f)
        return left + ' ' + op + ' ' + right
    return left

def parse_if(f, indent):
    global look
    look_next(f)
    expression = parse_expression(f)
    look_next(f)

    output("if " + expression + ":", indent)
    parse_code(f, indent+1)

def parse_print(f, indent):
    look_next(f)
    expression = parse_expression(f)
    output("print(" + expression + ")", indent)

def parse_function(f, indent):
    look_next(f)
    name = look_next(f)[0]
    params = look_next(f)[0]

    output("def " + name + params + ":", indent)
    parse_code(f, indent+1)

def parse_assign(f, indent):
    global look
    name = look_next(f)[0]
    if look[1] == ARGS:
        args = look_next(f)[0]
        output(name + args, indent)
        return
    
    look_next(f)
    expression = parse_expression(f)
    output(name + " = " + expression, indent)

def parse_while(f, indent):
    look_next(f)
    expression = parse_expression(f)
    look_next(f)

    output("while " + expression + ":", indent)
    parse_code(f, indent+1)

def parse_for(f, indent):
    look_next(f) # FOR
    name = look_next(f)[0]
    look_next(f) # <-
    from_exp = parse_expression(f)
    look_next(f) # TO
    to_exp = parse_expression(f)
    look_next(f) # DO

    output("for " + name + " in range(" + from_exp + ", " + to_exp + "):", indent)
    parse_code(f, indent+1)

def parse_code(f, indent):
    global look
    while True:
        if not look:
            break
        
        if look[1] == IF:
            parse_if(f, indent)
        elif look[1] == OUTPUT:
            parse_print(f, indent)
        elif look[1] == SUBROUTINE:
            parse_function(f, indent)
        elif look[1] == NAME:
            parse_assign(f, indent)
        elif look[1] == WHILE:
            parse_while(f, indent)
        elif look[1] == FOR:
            parse_for(f, indent)
        elif look[1] == ELSE:
            output("else:", indent-1)
            look_next(f)
        elif look[1] == END:
            look_next(f)
            look_next(f)
            break

def parse(path):
    global out
    out = ""
    
    f = open(path, "rb")
    look_next(f)
    parse_code(f, 0)

    # Run code kek
    print(out)
    exec(out)

parse("test.sudo")
