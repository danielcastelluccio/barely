import sys
import os
from collections import OrderedDict

class KeywordToken:
    def __init__(self, word):
        self.word = word

    def __str__(self) -> str:
        return "[Keyword: '" + self.word + "']"

class NameToken:
    def __init__(self, name):
        self.name = name

    def __str__(self) -> str:
        return "[Name: '" + self.name + "']"

class OpenParenthesisToken:
    def __str__(self) -> str:
        return "[OpenParenthesis]"

class ClosedParenthesisToken:
    def __str__(self) -> str:
        return "[ClosedParenthesis]"

class OpenCurlyBracketToken:
    def __str__(self) -> str:
        return "[OpenCurlyBracket]"

class ClosedCurlyBracketToken:
    def __str__(self) -> str:
        return "[ClosedCurlyBracket]"

class SemiColonToken:
    def __str__(self) -> str:
        return "[SemiColon]"

class ColonToken:
    def __str__(self) -> str:
        return "[Colon]"

class CommaToken:
    def __str__(self) -> str:
        return "[Comma]"

class StringToken:
    def __init__(self, string):
        self.string = string

    def __str__(self) -> str:
        return "[String: '" + self.string + "']"

class IntegerToken:
    def __init__(self, integer):
        self.integer = integer

    def __str__(self) -> str:
        return "[Integer: '" + str(self.integer) + "']"

class BooleanToken:
    def __init__(self, boolean):
        self.boolean = boolean

    def __str__(self) -> str:
        return "[Boolean: '" + str(self.boolean) + "']"

class NumberSplitToken:
    def __init__(self, number1, number2):
        self.number1 = number1
        self.number2 = number2

    def __str__(self) -> str:
        return "[NumberSplit: '" + str(self.number1) + "', '" + str(self.number2) + "']"

def is_num(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

keywords = ["function", "return", "variable", "structure", "constant", "if", "while"]

def tokenize_small(contents):
    tokens = []

    if contents in keywords:
        tokens.append(KeywordToken(contents))
    elif "_" in contents and is_num(contents.split("_")[0]) and is_num(contents.split("_")[1]):
        split = contents.split("_")
        tokens.append(NumberSplitToken(int(split[0]), int(split[1])))
    elif is_num(contents):
        tokens.append(IntegerToken(int(contents)))
    elif contents == "true" or contents == "false":
        tokens.append(BooleanToken(contents == "true"))
    elif contents.strip():
        tokens.append(NameToken(contents))

    return tokens

def tokenize(contents):
    tokens = []

    buffer = ""
    in_quotes = False
    for character in contents:
        if character == ' ' and not in_quotes:
            tokens.extend(tokenize_small(buffer))
            buffer = ""
        elif character == '(' and not in_quotes:
            tokens.extend(tokenize_small(buffer))
            tokens.append(OpenParenthesisToken())
            buffer = ""
        elif character == ')' and not in_quotes:
            tokens.extend(tokenize_small(buffer))
            tokens.append(ClosedParenthesisToken())
            buffer = ""
        elif character == '{' and not in_quotes:
            tokens.append(OpenCurlyBracketToken())
        elif character == '}' and not in_quotes:
            tokens.append(ClosedCurlyBracketToken())
        elif character == ';' and not in_quotes:
            tokens.extend(tokenize_small(buffer))
            tokens.append(SemiColonToken())
            buffer = ""
        elif character == ',' and not in_quotes:
            tokens.extend(tokenize_small(buffer))
            tokens.append(CommaToken())
            buffer = ""
        elif character == ':' and not in_quotes:
            tokens.extend(tokenize_small(buffer))
            tokens.append(ColonToken())
            buffer = ""
        elif character == '"':
            if in_quotes:
                tokens.append(StringToken(buffer))
                buffer = ""
                in_quotes = False
            else:
                in_quotes = True
        elif character == '\t' or character == '\n':
            pass
        else:
            buffer += character


    return tokens

class ConstantNode:
    def __init__(self, name, type, value_token):
        self.name = name
        self.type = type
        self.value_token = value_token

class StructureNode:
    def __init__(self, name, items):
        self.name = name
        self.items = items

class FunctionNode:
    def __init__(self, name, instructions, parameters, returns, locals):
        self.name = name
        self.instructions = instructions
        self.parameters = parameters
        self.returns = returns
        self.locals = locals

class InvokeNode:
    def __init__(self, name):
        self.name = name

class RetrieveNode:
    def __init__(self, name):
        self.name = name

class AssignNode:
    def __init__(self, name):
        self.name = name

class DeclareNode:
    def __init__(self, name, type):
        self.name = name
        self.type = type

class StringNode:
    def __init__(self, string):
        self.string = string

class IntegerNode:
    def __init__(self, integer):
        self.integer = integer

class BooleanNode:
    def __init__(self, boolean):
        self.boolean = boolean

class LongNode:
    def __init__(self, integer1, integer2):
        self.integer1 = integer1
        self.integer2 = integer2

class TargetNode:
    def __init__(self, id):
        self.id = id

class JumpNode:
    def __init__(self, id):
        self.id = id

class ConditionalJumpNode:
    def __init__(self, wants_true, id):
        self.wants_true = wants_true
        self.id = id

class ReturnNode:
    pass

class PointerNode:
    pass

def get_statement_lisp(tokens, index, current_function, ast):
    statement1 = []
    token = tokens[index]

    if isinstance(token, OpenParenthesisToken):
        index += 1
    elif isinstance(token, ClosedParenthesisToken):
        index += 1
    elif isinstance(token, KeywordToken):
        if token.word == "function":
            current_function, index = get_function_declaration_lisp(tokens, index + 1)
            ast.append(current_function)
        elif token.word == "variable":
            name = tokens[index + 2].name
            type = tokens[index + 3].name

            statement = []

            if not isinstance(tokens[index + 5], ClosedParenthesisToken):
                statement, index = get_assign_lisp(tokens, index + 5, name)
            else:
                index += 6

            statement1.append(DeclareNode(name, type))
            statement1.extend(statement)
        elif token.word == "return":
            statement, index = get_expression_lisp(tokens, index + 1)

            statement1.extend(statement)
            statement1.append(ReturnNode())
        elif token.word == "structure":
            name = tokens[index + 1].name
            items = OrderedDict()

            index += 2

            name_cache = None
            indent = 0
            while not isinstance(tokens[index], ClosedParenthesisToken) or not indent == 1:
                token = tokens[index]

                if isinstance(token, OpenParenthesisToken):
                    name_cache = None
                    indent += 1
                elif isinstance(token, ClosedParenthesisToken):
                    indent -= 1
                elif isinstance(token, NameToken):
                    if not name_cache:
                        name_cache = token.name
                    else:
                        items[name_cache] = token.name

                index += 1

            index += 1

            ast.append(StructureNode(name, items))

            for item_name in items:
                item_type = items[item_name]

                instructions = []
                ast.append(FunctionNode(name + "->" + item_name, instructions, {"struct": "*" + name}, [item_type], []))
                ast.append(FunctionNode("*" + name + "->" + item_name, instructions, {"struct": "*" + name}, ["*" + item_type], []))
                ast.append(FunctionNode(name + "<-" + item_name, instructions, {"struct": "*" + name, "item": item_type}, [], []))
        elif token.word == "constant":
            name = tokens[index + 2].name
            type = tokens[index + 3].name

            value_token = tokens[index + 5]

            ast.append(ConstantNode(name, type, value_token))

            index += 5
    elif isinstance(token, NameToken) and isinstance(tokens[index + 1], OpenParenthesisToken):
        statement, index = get_invoke_lisp(tokens, index + 1, tokens[index].name)
        index += 1

        statement1.extend(statement)
    elif isinstance(token, NameToken) and isinstance(tokens[index - 1], OpenParenthesisToken) and isinstance(tokens[index + 1], ClosedParenthesisToken):
        statement, index = get_assign_lisp(tokens, index + 2, tokens[index].name)

        index += 1
        statement1.extend(statement)
    else:
        expression, index = get_expression_lisp(tokens, index)

        index += 1
        statement1.extend(expression)

    return statement1, index, current_function

def generate_ast_lisp(tokens):
    ast = []

    current_function = None
    index = 0
    while index < len(tokens):
        statement, index, current_function = get_statement_lisp(tokens, index, current_function, ast)
        if len(statement) > 0 and current_function:
            current_function.instructions.extend(statement)

    for function in ast:
        if isinstance(function, FunctionNode):
            for instruction in function.instructions:
                if isinstance(instruction, DeclareNode):
                    if not instruction.name in function.locals:
                        function.locals.append(instruction.name)

    return ast

def get_statement_c(tokens, index):
    statement = []

    token = tokens[index]
    if isinstance(token, KeywordToken):
        if token.word == "function":
            current_function, index = get_function_declaration_c(tokens, index + 1)

            while not isinstance(tokens[index], SemiColonToken):
                statement, index = get_statement_c(tokens, index)
                current_function.instructions.extend(statement)

            statement.append(current_function)
        elif token.word == "return":
            index += 1
            while not isinstance(tokens[index], SemiColonToken):
                if isinstance(tokens[index], CommaToken):
                    index += 1

                expression, index = get_expression_lisp(tokens, index)
                statement.extend(expression)

            statement.append(ReturnNode())
        elif token.word == "variable":
            variables = {}
            names = []

            i = 1
            while (not isinstance(tokens[index + i - 1], NameToken) or not tokens[index + i - 1].name == "=") and not isinstance(tokens[index + i - 1], SemiColonToken):
                name = tokens[index + i].name
                type = tokens[index + i + 2].name

                names.append(name)
                variables[name] = type
                i += 4

            statement0 = []

            if not isinstance(tokens[index + 4], SemiColonToken):
                statement0, index = get_assign_c(tokens, index + i, names)
            else:
                index += 4

            for name in names:
                statement.append(DeclareNode(name, variables[name]))
            statement.extend(statement0)
        elif token.word == "structure":
            name = tokens[index + 1].name
            items = OrderedDict()

            index += 2

            name_cache = None
            while not isinstance(tokens[index], ClosedCurlyBracketToken):
                token = tokens[index]

                if isinstance(token, SemiColonToken):
                    name_cache = None
                elif isinstance(token, NameToken):
                    if not name_cache:
                        name_cache = token.name
                    else:
                        items[name_cache] = token.name

                index += 1

            index += 1

            ast.append(StructureNode(name, items))

            for item_name in items:
                item_type = items[item_name]

                instructions = []
                ast.append(FunctionNode(name + "->" + item_name, instructions, {"struct": "*" + name}, [item_type], []))
                ast.append(FunctionNode("*" + name + "->" + item_name, instructions, {"struct": "*" + name}, ["*" + item_type], []))
                ast.append(FunctionNode(name + "<-" + item_name, instructions, {"struct": "*" + name, "item": item_type}, [], []))
        elif token.word == "constant":
            name = tokens[index + 1].name
            type = tokens[index + 3].name

            value_token = tokens[index + 5]

            ast.append(ConstantNode(name, type, value_token))

            index += 4
        elif token.word == "if":
            index += 1

            global target_id
            id = target_id
            target_id += 1

            while not isinstance(tokens[index], OpenCurlyBracketToken):
                expression, index = get_expression_c(tokens, index)
                statement.extend(expression)
                #print(expression)
                
                statement.append(ConditionalJumpNode(False, id))


            index += 1

            while not isinstance(tokens[index], ClosedCurlyBracketToken):
                statement0, index = get_statement_c(tokens, index)
                statement.extend(statement0)
                #print(expression)

                statement.append(TargetNode(id))

            index += 1

        elif token.word == "while":
            index += 1

            id1 = target_id
            target_id += 1

            id2 = target_id
            target_id += 1

            statement.append(TargetNode(id2))

            while not isinstance(tokens[index], OpenCurlyBracketToken):
                expression, index = get_expression_c(tokens, index)
                statement.extend(expression)
                
                statement.append(ConditionalJumpNode(False, id1))


            index += 1

            while not isinstance(tokens[index], ClosedCurlyBracketToken):
                statement0, index = get_statement_c(tokens, index)
                statement.extend(statement0)
                #print(expression)

            statement.append(JumpNode(id2))
            statement.append(TargetNode(id1))
            index += 1

    elif isinstance(token, NameToken) and isinstance(tokens[index + 1], NameToken) and tokens[index + 1].name == "=":
        assign, index = get_assign_c(tokens, index + 2, [tokens[index].name])

        statement.extend(assign)
    else:
        expression, index = get_expression_c(tokens, index)

        statement.extend(expression)

    index += 1
    
    return statement, index

def generate_ast_c(tokens):
    ast = []
    
    #current_function = None
    index = 0
    while index < len(tokens):
        statement, index = get_statement_c(tokens, index)
        ast.extend(statement)
        #if current_function:
            #current_function.instructions.extend(statement)

    for function in ast:
        if isinstance(function, FunctionNode):
            for instruction in function.instructions:
                if isinstance(instruction, DeclareNode):
                    if not instruction.name in function.locals:
                        function.locals.append(instruction.name)

    return ast

def get_function_declaration_lisp(tokens, index):
    name = None
    if isinstance(tokens[index], NameToken):
        name = tokens[index].name

    index += 1

    parameters = {}
    current_param_name = None
    indent = 0
    while not isinstance(tokens[index], ClosedParenthesisToken) or not indent == 1:
        if isinstance(tokens[index], OpenParenthesisToken):
            current_param_name = None
            indent += 1
        elif isinstance(tokens[index], ClosedParenthesisToken):
            indent -= 1
        else:
            if not current_param_name:
                current_param_name = tokens[index].name
            else:
                parameters[current_param_name] = tokens[index].name

        index += 1

    index += 2

    returns = []

    while not isinstance(tokens[index], ClosedParenthesisToken):
        returns.append(tokens[index].name)
        index += 1

    index += 1

    return FunctionNode(name, [], parameters, returns, []), index

def get_function_declaration_c(tokens, index):
    name = None
    searching_returns = False
    parameters = OrderedDict()
    returns = []

    name_index = 0
    parameter_name_cache = ""

    while not isinstance(tokens[index], OpenCurlyBracketToken) and not isinstance(tokens[index], SemiColonToken):
        token = tokens[index]

        if isinstance(token, NameToken) and not name:
            name = token.name
        elif isinstance(token, ClosedParenthesisToken):
            searching_returns = True
        elif isinstance(token, NameToken) and searching_returns:
            returns.append(token.name)
        elif isinstance(token, NameToken):
            if name_index % 2 == 1:
                parameters[parameter_name_cache] = token.name
            else:
                parameter_name_cache = token.name
            name_index += 1

        index += 1

    return FunctionNode(name, [], parameters, returns, []), index

def get_expression_lisp(tokens, index):
    statement = []

    count = 0
    while isinstance(tokens[index], OpenParenthesisToken):
        count += 1
        index += 1

    if isinstance(tokens[index], NameToken) and isinstance(tokens[index + 1], OpenParenthesisToken):
        invoke, index = get_invoke_lisp(tokens, index + 1, tokens[index].name)
        statement.extend(invoke)
    elif isinstance(tokens[index], NameToken):
        retrieve, index = get_retrieve_lisp(index + 1, tokens[index].name)
        statement.extend(retrieve)
    elif isinstance(tokens[index], StringToken):
        statement.append(StringNode(tokens[index].string))
        index += 1
    elif isinstance(tokens[index], IntegerToken):
        statement.append(IntegerNode(tokens[index].integer))
        index += 1
    elif isinstance(tokens[index], BooleanToken):
        statement.append(BooleanNode(tokens[index].boolean))
        index += 1
    #elif isinstance(tokens[index], NumberSplitToken):
    #    statement.append(LongNode(tokens[index].number1, tokens[index].number2))
    #    index += 1

    index += count

    return statement, index

def get_expression_c(tokens, index):
    statement = []

    #print(tokens[index])
    if isinstance(tokens[index], NameToken) and isinstance(tokens[index + 1], OpenParenthesisToken):
        invoke, index = get_invoke_c(tokens, index + 1, tokens[index].name)
        statement.extend(invoke)
    elif isinstance(tokens[index], NameToken):
        retrieve, index = get_retrieve_c(index + 1, tokens[index].name)
        statement.extend(retrieve)
    elif isinstance(tokens[index], StringToken):
        statement.append(StringNode(tokens[index].string))
        index += 1
    elif isinstance(tokens[index], IntegerToken):
        statement.append(IntegerNode(tokens[index].integer))
        index += 1
    elif isinstance(tokens[index], BooleanToken):
        statement.append(BooleanNode(tokens[index].boolean))
        index += 1
    elif isinstance(tokens[index], NumberSplitToken):
        statement.append(LongNode(tokens[index].number1, tokens[index].number2))
        index += 1

    return statement, index

target_id = 0

def get_invoke_lisp(tokens, index, name):
    statement = []
    global target_id


    if name == "if":
        id1 = target_id
        target_id += 1

        iteration = 0
        index += 1
        while not isinstance(tokens[index], ClosedParenthesisToken):

            while isinstance(tokens[index], OpenParenthesisToken) and (not isinstance(tokens[index + 1], NameToken) or not isinstance(tokens[index + 1], ClosedParenthesisToken)):
                index += 1

            expression, index, _ = get_statement_lisp(tokens, index, None, None)
            statement.extend(expression)

            index += 1

            if iteration == 0:
                statement.append(ConditionalJumpNode(False, id1))
                index += 1

            iteration += 1

        statement.append(TargetNode(id1))
    elif name == "while":
        id1 = target_id
        target_id += 1
        id2 = target_id
        target_id += 1

        statement.append(TargetNode(id1))

        iteration = 0
        index += 1
        while not isinstance(tokens[index], ClosedParenthesisToken):
            while isinstance(tokens[index], OpenParenthesisToken) and (not isinstance(tokens[index + 1], NameToken) or not isinstance(tokens[index + 1], ClosedParenthesisToken)):
                index += 1

            expression, index, _ = get_statement_lisp(tokens, index, None, None)
            statement.extend(expression)

            index += 1

            if iteration == 0:
                statement.append(ConditionalJumpNode(False, id2))
                index += 1

            iteration += 1

        statement.append(JumpNode(id1))
        statement.append(TargetNode(id2))
    else:
        index += 1
        while not isinstance(tokens[index], ClosedParenthesisToken):
            expression, index = get_expression_lisp(tokens, index)
            statement = expression + statement

        if name == "&":
            statement.append(PointerNode())
        else:
            statement.append(InvokeNode(name))

    index += 1

    return statement, index

def get_invoke_c(tokens, index, name):
    statement = []
    statement1 = []

    index += 1
    #print(tokens[index - 3])
    #print(tokens[index])
    while not isinstance(tokens[index], ClosedParenthesisToken):
        #print(name)
        #print(tokens[index])
        expression, index = get_expression_c(tokens, index)
        statement = expression + statement
        if isinstance(tokens[index], CommaToken):
            statement = statement1 + statement
            statement1.clear()
            index += 1

    statement = statement1 + statement

    if name == "&":
        statement.append(PointerNode())
    else:
        statement.append(InvokeNode(name))

    index += 1

    return statement, index

def get_assign_lisp(tokens, index, name):
    statement = []

    expression, index = get_expression_lisp(tokens, index)
    statement.extend(expression)

    statement.append(AssignNode(name))

    return statement, index

def get_assign_c(tokens, index, names):
    statement = []

    while not isinstance(tokens[index], SemiColonToken):
        expression, index = get_expression_c(tokens, index)
        statement.extend(expression)

    for name in reversed(names):
        statement.append(AssignNode(name))

    return statement, index

def is_type(given, wanted):
    if wanted == given:
        return True

    if wanted == "any":
        return True

    if wanted.startswith("any"):
        size = int(wanted.split("_")[1])
        if get_size_linux_x86_64(given, None) == size:
            return True

    return False

def get_retrieve_lisp(index, name):
    statement = []

    statement.append(RetrieveNode(name))

    return statement, index

def get_retrieve_c(index, name):
    statement = []

    statement.append(RetrieveNode(name))

    return statement, index

def type_check(ast, functions):
    constants = {}

    for constant in ast:
        if isinstance(constant, ConstantNode):
            constants[constant.name] = constant.type

    for function in ast:
        if isinstance(function, FunctionNode):
            variables = {}
            types = []

            for parameter in function.parameters:
                variables[parameter] = function.parameters[parameter]

            #print(function.instructions)

            for instruction in function.instructions:
                if isinstance(instruction, DeclareNode):
                    variables[instruction.name] = instruction.type
                elif isinstance(instruction, IntegerNode):
                    types.append("integer")
                elif isinstance(instruction, LongNode):
                    types.append("long")
                elif isinstance(instruction, StringNode):
                    types.append("*")
                elif isinstance(instruction, BooleanNode):
                    types.append("boolean")
                elif isinstance(instruction, AssignNode):
                    popped = types.pop()
                    if not is_type(popped, variables[instruction.name]):
                        print("TYPECHECK: Assign of " + instruction.name + " in " + function.name + " expected " + variables[instruction.name] + ", got " + popped + ".")
                        exit()
                elif isinstance(instruction, RetrieveNode):
                    if instruction.name in variables:
                        types.append(variables[instruction.name])
                    else:
                        types.append(constants[instruction.name])
                elif isinstance(instruction, InvokeNode):
                    if instruction.name.startswith("@cast_"):
                        types.pop()
                        types.append(instruction.name[6:])
                    else:
                        called_function = functions[instruction.name]
                        for parameter in called_function.parameters.values():
                            popped = types.pop()
                            if not is_type(popped, parameter):
                                print("TYPECHECK: Invoke of " + instruction.name + " in " + function.name + " expected " + parameter + ", got " + popped + ".")
                                exit()

                        for return_ in called_function.returns:
                            types.append(return_)
                elif isinstance(instruction, ReturnNode):
                    for return_ in reversed(function.returns):
                        popped = types.pop()
                        if not is_type(popped, return_):
                            print("TYPECHECK: Return in " + function.name + " expected " + return_ + ", got " + popped + ".")
                            exit()

                    if len(types) > 0:
                        print("TYPECHECK: Return in " + function.name + " has extra data on stack.")
                        exit()
                elif isinstance(instruction, PointerNode):
                    popped = types.pop()
                    types.append("*" + popped)
                elif isinstance(instruction, TargetNode):
                    pass
                elif isinstance(instruction, JumpNode):
                    pass
                elif isinstance(instruction, ConditionalJumpNode):
                    popped = types.pop()

                    if not popped == "boolean":
                            print("TYPECHECK: If in " + function.name + " expected boolean, got " + popped + ".")
                            exit()
                else:
                    print(str(instruction) + " not handled in typecheck!")
                    exit()

            if len(types) > 0:
                #print(function.name)
                #print(types)
                print("TYPECHECK: Return in " + function.name + " has extra data on stack.")
                exit()
        

def get_size_linux_x86_64(types, ast):
    size = 0

    if isinstance(types, str):
        types = [types]

    for type in types:
        #TODO: make boolean 1 byte
        if type[0] == "*" or type == "integer" or type == "any":
            size += 8
        elif type.startswith("any"):
            size += int(type.split("_")[1])
        elif type == "boolean":
            size += 1
        else:
            added = False
            for struct in ast:
                if isinstance(struct, StructureNode):
                    if struct.name == type:
                        size += get_size_linux_x86_64(struct.items.values(), ast)
                        added = True
                        break

            if not added:
                print("unknown type " + type)
                exit()

    return size

def remove_invalid_linux_x86_64(name):
    invalid = "-><*"

    for character in invalid:
        name = name.replace(character, str(ord(character)))

    if is_num(name[0]):
        name = "_" + name

    return name

def compile_linux_x86_64(ast, name, functions):
    fasm_file = open("build/" + name + ".asm", 'w')
    contents = "format ELF64 executable\n"
    contents += "entry start\n"
    contents += "segment readable executable\n"
    contents += "start:\n"
    contents += "call main\n"
    contents += "mov rax, 60\n"
    contents += "mov rdi, 1\n"
    contents += "syscall\n"

    contents += """@print_integer:
pop rsi
pop rdi
push rdi
push rsi
mov r9, -3689348814741910323
sub rsp, 40
mov BYTE [rsp+31], 10
lea rcx, [rsp+30]
.L2:
mov rax, rdi
lea r8, [rsp+32]
mul r9
mov rax, rdi
sub r8, rcx
shr rdx, 3
lea rsi, [rdx+rdx*4]
add rsi, rsi
sub rax, rsi
add eax, 48
mov BYTE [rcx], al
mov rax, rdi
mov rdi, rdx
mov rdx, rcx
sub rcx, 1
cmp rax, 9
ja .L2
lea rax, [rsp+32]
mov edi, 1
sub rdx, rax
xor eax, eax
lea rsi, [rsp+32+rdx]
mov rdx, r8
mov rax, 1
syscall
add     rsp, 40
pop     rax
add     rsp, 8
push     rax
ret
"""

    for struct in ast:
        if isinstance(struct, StructureNode):
            items = struct.items

            k = 0
            for item_name in items:
                item_type = items[item_name]
                location = get_size_linux_x86_64(list(items.values())[0 : k], ast)
                size = get_size_linux_x86_64(item_type, ast)
                size = (((size) + 7) & (-8))

                contents +=  remove_invalid_linux_x86_64(struct.name + "->" + item_name) + ":\n"
                contents += "push rbp\n"
                contents += "mov rbp, rsp\n"
                contents += "mov rax, [rbp+16]\n"

                contents += "sub rsp, " + str(size) + "\n"

                j = 0
                while j < size:
                    if size - j >= 8:
                        contents += "mov rbx, [rax+" + str(location + j) + "]\n"
                        contents += "mov [rsp+" + str(j) + "], rbx\n"
                        j += 8
                    elif size - j >= 4:
                        contents += "mov ebx, [rax+" + str(location + j) + "]\n"
                        contents += "mov [rsp+" + str(j) + "], ebx\n"
                        j += 4
                    elif size - j >= 2:
                        contents += "mov bx, [rax+" + str(location + j) + "]\n"
                        contents += "mov [rsp+" + str(j) + "], bx\n"
                        j += 2
                    else:
                        print("sizing error")
                        exit()

                contents += "mov rcx, [rsp+" + str(size + 8) + "]\n"
                contents += "mov rdx, [rsp+" + str(size) + "]\n"
                size_rounded = (((size) + 7) & (-8))
                size += 8
                i = 0
                while i < size:
                    if size - i >= 8:
                        contents += "mov rax, [rsp+" + str(size - i - 8) + "]\n"
                        contents += "mov [rbp+" + str(size - i + 16 - size + 8) + "], rax\n"
                        i += 8
                    #elif size - i >= 4:
                    #    contents += "mov eax, [rsp+" + str(size - i - 4) + "]\n"
                    #    contents += "mov [rbp+" + str(16 + 8 - size - i + size_rounded) + "], eax\n"
                    #    i += 4
                    #elif size - i >= 2:
                    #    contents += "mov ax, [rsp+" + str(size - i - 2) + "]\n"
                    #    contents += "mov [rbp+" + str(16 + 8 - size - i + size_rounded) + "], ax\n"
                    #    i += 2
                    else:
                        print("sizing error")
                        exit()
            
                size -= 8

                contents += "mov rsp, rbp\n"
                contents += "add rsp, " + str(16 + 8 - size) + "\n"
                contents += "push rdx\n"
                contents += "pop rbp\n"
                contents += "push rcx\n"
                contents += "ret\n"

                contents += remove_invalid_linux_x86_64("*" + struct.name + "->" + item_name) + ":\n"
                contents += "push rbp\n"
                contents += "mov rbp, rsp\n"
                contents += "mov rax, [rbp+16]\n"
                contents += "add rax, " + str(location) + "\n"

                contents += "pop rdx\n"
                contents += "pop rcx\n"

                #contents += "sub rsp, 8\n"

                contents += "mov rsp, rbp\n"
                contents += "add rsp, 24\n"
                contents += "push rax\n"
                contents += "push rdx\n"
                contents += "pop rbp\n"
                contents += "push rcx\n"
                contents += "ret\n"


                contents += remove_invalid_linux_x86_64(struct.name + "<-" + item_name) + ":\n"
                contents += "push rbp\n"
                contents += "mov rbp, rsp\n"
                contents += "mov rax, [rbp+16]\n"

                contents += "sub rsp, " + str(size) + "\n"

                j = 0
                while j < size:
                    if size - j >= 8:
                        contents += "mov rbx, [rbp+" + str(24 + j) + "]\n"
                        contents += "mov [rax+" + str(location + j) + "], rbx\n"
                        j += 8
                    elif size - j >= 4:
                        contents += "mov ebx, [rbp+" + str(24 + j) + "]\n"
                        contents += "mov [rax+" + str(location + j) + "], ebx\n"
                        j += 4
                    elif size - j >= 2:
                        contents += "mov bx, [rbp+" + str(24 + j) + "]\n"
                        contents += "mov [rax+" + str(location + j) + "], bx\n"
                        j += 2
                    else:
                        print("sizing error")
                        exit()

                contents += "mov rcx, [rbp+" + str(8) + "]\n"
                contents += "mov rdx, [rbp+" + str(0) + "]\n"

                contents += "mov rsp, rbp\n"
                contents += "add rsp, " + str(size + 16 + 8) + "\n"
                contents += "push rdx\n"
                contents += "pop rbp\n"
                contents += "push rcx\n"
                contents += "ret\n"

                k += 1

    contents_data = ""
    data_index = 0

    constants = {}
    for constant in ast:
        if isinstance(constant, ConstantNode):
            constants[constant.name] = constant.type

    for function in ast:
        if isinstance(function, FunctionNode):
            if len(function.instructions) == 0:
                continue

            contents += remove_invalid_linux_x86_64(function.name) + ":\n"

            local_types = [None] * len(function.locals)

            for instruction in function.instructions:
                if isinstance(instruction, DeclareNode):
                    local_types[function.locals.index(instruction.name)] = instruction.type

            contents += "push rbp\n"
            contents += "mov rbp, rsp\n"
            contents += "sub rsp, " + str(get_size_linux_x86_64(local_types, ast) + 16) + "\n"

            variables = {}

            local_types = [None] * len(function.locals)

            for index0, instruction in enumerate(function.instructions):
                if isinstance(instruction, InvokeNode):
                    if instruction.name == ">":
                        contents += "pop rax\n"
                        contents += "pop rbx\n"
                        contents += "cmp rax, rbx\n"
                        contents += "mov rcx, 0\n"
                        contents += "mov rbx, 1\n"
                        contents += "cmova rcx, rbx\n"
                        contents += "push rcx\n"
                    elif instruction.name == "=":
                        contents += "pop rax\n"
                        contents += "pop rbx\n"
                        contents += "cmp rax, rbx\n"
                        contents += "mov rcx, 0\n"
                        contents += "mov rbx, 1\n"
                        contents += "cmove rcx, rbx\n"
                        contents += "push rcx\n"
                    elif instruction.name == "=1":
                        contents += "pop rax\n"
                        contents += "pop rbx\n"
                        contents += "cmp rax, rbx\n"
                        contents += "mov rcx, 0\n"
                        contents += "mov rbx, 1\n"
                        contents += "cmove rcx, rbx\n"
                        contents += "push rcx\n"
                    elif instruction.name == "!":
                        contents += "pop rax\n"
                        contents += "cmp rax, 0\n"
                        contents += "mov rcx, 0\n"
                        contents += "mov rbx, 1\n"
                        contents += "cmove rcx, rbx\n"
                        contents += "push rcx\n"
                    elif instruction.name == "+":
                        contents += "pop rax\n"
                        contents += "pop rbx\n"
                        contents += "add rax, rbx\n"
                        contents += "push rax\n"
                    elif instruction.name == "-":
                        contents += "pop rax\n"
                        contents += "pop rbx\n"
                        contents += "sub rax, rbx\n"
                        contents += "push rax\n"
                    elif instruction.name == "*1":
                        contents += "pop rcx\n"
                        contents += "mov rax, 0\n"
                        contents += "mov al, [rcx]\n"
                        contents += "push rax\n"
                    elif instruction.name == "@syscall3":
                        contents += "pop rax\n"
                        contents += "pop rdi\n"
                        contents += "pop rsi\n"
                        contents += "pop rdx\n"
                        contents += "syscall\n"
                        contents += "push rax\n"
                    elif instruction.name == "byte":
                        contents += "pop rax\n"
                        contents += "push rax\n"
                    elif not instruction.name.startswith("@cast_"):
                        called_name = instruction.name

                        if len(function.instructions) > index0 + 1 and isinstance(function.instructions[index0 + 1], PointerNode) and "->" in called_name:
                            called_name = "*" + called_name

                        contents += "call " + remove_invalid_linux_x86_64(called_name) + "\n"
                elif isinstance(instruction, DeclareNode):
                    variables[instruction.name] = instruction.type
                    local_types[function.locals.index(instruction.name)] = instruction.type
                elif isinstance(instruction, RetrieveNode):
                    if instruction.name in function.parameters:
                        i = -1

                        for index, parameter in enumerate(function.parameters):
                            if parameter == instruction.name:
                                i = index

                        location = get_size_linux_x86_64(list(function.parameters.values())[0 : i], ast)
                        if isinstance(function.instructions[index0 + 1], PointerNode):
                            contents += "lea rax, [rbp+" + str(16 + location) + "]\n"
                            contents += "push rax\n"
                        else:
                            size = get_size_linux_x86_64(function.parameters[instruction.name], ast)
                            size = (((size) + 7) & (-8))
                            contents += "sub rsp, " + str(size) + "\n"
                            j = 0
                            while j < size:
                                if size - j >= 8:
                                    contents += "mov rax, [rbp+" + str(16 + location + j) + "]\n"
                                    contents += "mov [rsp+" + str(j) + "], rax\n"
                                    j += 8
                                elif size - j >= 4:
                                    contents += "mov eax, [rbp+" + str(16 + location + j) + "]\n"
                                    contents += "mov [rsp+" + str(j) + "], eax\n"
                                    j += 4
                                elif size - j >= 2:
                                    contents += "mov ax, [rbp+" + str(16 + location + j) + "]\n"
                                    contents += "mov [rsp+" + str(j) + "], ax\n"
                                    j += 2
                                else:
                                    print("sizing error")
                                    exit()
                    elif instruction.name in function.locals:
                        i = function.locals.index(instruction.name)
                        location = get_size_linux_x86_64(local_types[0 : i], ast)
                        size = get_size_linux_x86_64(local_types[i], ast)
                        size = (((size) + 7) & (-8))

                        #print(instruction.name)
                        if isinstance(function.instructions[index0 + 1], PointerNode):
                            contents += "lea rax, [rbp-" + str(location + size) + "]\n"
                            contents += "push rax\n"
                        else:
                            contents += "sub rsp, " + str(size) + "\n"

                            j = 0
                            while j < size:
                                if size - j >= 8:
                                    contents += "mov rax, [rbp-" + str(8 + location + size - j - 8) + "]\n"
                                    contents += "mov [rsp+" + str(j) + "], rax\n"
                                    j += 8
                                elif size - j >= 4:
                                    contents += "mov eax, [rbp-" + str(8 + location + size - j - 8) + "]\n"
                                    contents += "mov [rsp+" + str(j) + "], eax\n"
                                    j += 4
                                elif size - j >= 2:
                                    contents += "mov ax, [rbp-" + str(8 + location + size - j - 8) + "]\n"
                                    contents += "mov [rsp+" + str(j) + "], ax\n"
                                    j += 2
                                else:
                                    print("sizing error")
                                    exit()
                    else:
                        #i = function.locals.index(instruction.name)
                        #location = get_size_linux_x86_64(local_types[0 : i], ast)
                        size = get_size_linux_x86_64(constants[instruction.name], ast)
                        size = (((size) + 7) & (-8))

                        if isinstance(function.instructions[index0 + 1], PointerNode):
                            contents += "mov rax, _" + instruction.name + "\n"
                            contents += "push rax\n"
                        else:
                            contents += "sub rsp, " + str(size) + "\n"

                            j = 0
                            while j < size:
                                if size - j >= 8:
                                    contents += "mov rax, [_" + instruction.name + "+" + str(j) + "]\n"
                                    contents += "mov [rsp+" + str(j) + "], rax\n"
                                    j += 8
                                elif size - j >= 4:
                                    contents += "mov eax, [_" + instruction.name + "+" + str(j) + "]\n"
                                    contents += "mov [rsp+" + str(j) + "], eax\n"
                                    j += 4
                                elif size - j >= 2:
                                    contents += "mov ax, [_" + instruction.name + "+" + str(j) + "]\n"
                                    contents += "mov [rsp+" + str(j) + "], ax\n"
                                    j += 2
                                else:
                                    print("sizing error")
                                    exit()
                elif isinstance(instruction, AssignNode):
                    i = function.locals.index(instruction.name)

                    size = get_size_linux_x86_64(variables[instruction.name], ast)
                    size = (((size) + 7) & (-8))
                    location = get_size_linux_x86_64(local_types[0 : i], ast)
                    i = 0
                    while i < size:
                        if size - i >= 8:
                            contents += "mov rax, [rsp+" + str(i) + "]\n"
                            contents += "mov [rbp-" + str(8 + size + location - i - 8) + "], rax\n"
                            i += 8
                        elif size - i >= 4:
                            contents += "mov eax, [rsp+" + str(i) + "]\n"
                            contents += "mov [rbp-" + str(8 + size + location - i - 8) + "], eax\n"
                            i += 4
                        elif size - i >= 2:
                            contents += "mov ax, [rsp+" + str(i) + "]\n"
                            contents += "mov [rbp-" + str(8 + size + location - i - 8) + "], ax\n"
                            i += 2
                        else:
                            print("sizing error")
                            exit()
                    contents += "add rsp, " + str(((size + 7) & (-8))) + "\n"
                elif isinstance(instruction, StringNode):
                    contents += "push _" + str(data_index) + "\n"
                    contents_data += "_" + str(data_index) + ": db \"" + instruction.string + "\", 0\n"
                    data_index += 1
                elif isinstance(instruction, IntegerNode):
                    contents += "push " + str(instruction.integer) + "\n"
                elif isinstance(instruction, BooleanNode):
                    contents += "push " + str(1 if instruction.boolean else 0) + "\n"
                elif isinstance(instruction, ReturnNode):
                    params_size = get_size_linux_x86_64(functions[function.name].parameters.values(), ast)
                    params_size = (((params_size) + 7) & (-8))
                    size = get_size_linux_x86_64(functions[function.name].returns, ast)
                    size = (((size) + 7) & (-8))
                    size_rounded = (((size + 8) + 7) & (-8))
                    i = 0
                    j = size + 8
                    contents += "mov rcx, [rbp+8]\n"
                    contents += "mov rdx, [rbp]\n"
                    size += 8
                    while i < size:
                        if size - i >= 8:
                            j -= 8
                            contents += "mov rax, [rsp+" + str(size - i - 8) + "]\n"
                            contents += "mov [rbp+" + str(16 + params_size - size - i + size_rounded) + "], rax\n"
                            i += 8
                        elif size - i >= 4:
                            j -= 4
                            contents += "mov eax, [rsp+" + str(size - i - 4) + "]\n"
                            contents += "mov [rbp+" + str(16 + params_size - size - i + size_rounded) + "], eax\n"
                            i += 4
                        elif size - i >= 2:
                            j -= 2
                            contents += "mov ax, [rsp+" + str(size - i - 2) + "]\n"
                            contents += "mov [rbp+" + str(16 + params_size - size - i + size_rounded) + "], ax\n"
                            i += 2
                        else:
                            print("sizing error")
                            exit()

                    size -= 8

                    contents += "mov rsp, rbp\n"
                    #contents += "add rsp, " + str(size + 16) + "\n"
                    contents += "add rsp, " + str(16 + params_size - size) + "\n"
                    contents += "push rdx\n"
                    contents += "pop rbp\n"
                    contents += "push rcx\n"
                    contents += "ret\n"
                elif isinstance(instruction, PointerNode):
                    pass
                elif isinstance(instruction, TargetNode):
                    contents += "target_" + str(instruction.id) + ":\n"
                elif isinstance(instruction, ConditionalJumpNode):
                    contents += "pop rax\n"
                    contents += "cmp rax, " + str(1 if instruction.wants_true else 0) + "\n"
                    contents += "je target_" + str(instruction.id) + "\n"
                elif isinstance(instruction, JumpNode):
                    contents += "jmp target_" + str(instruction.id) + "\n"
                else:
                    print(str(instruction) + " not handled in linux codegen!")
                    exit()

            contents += "mov rbx, [rbp]\n"
            contents += "mov rdx, [rbp+8]\n"
            contents += "mov rsp, rbp\n"
            contents += "add rsp, " + str(16 + get_size_linux_x86_64(function.parameters.values(), ast)) + "\n"
            contents += "push rbx\n"
            contents += "pop rbp\n"
            contents += "push rdx\n"
            contents += "ret\n"

    contents += "segment readable\n"
    contents += contents_data

    for constant in ast:
        if isinstance(constant, ConstantNode):
            contents += "_" + constant.name + ":"

            if isinstance(constant.value_token, IntegerToken):
                contents += "dq " + str(constant.value_token.integer)

            contents += "\n"

    fasm_file.write(contents)
    fasm_file.close()

    os.system("fasm " + fasm_file.name + " build/" + name)

#syntax = sys.argv[1]
ast = []
name = None
for file in sys.argv[1:]:
    file = open(file)

    if not name:
        name = file.name

    contents = file.read()

    tokens = tokenize(contents)

    ast.extend(generate_ast_c(tokens))
#match syntax:
#    case "lisp":
#        ast = generate_ast_lisp(tokens)
#    case "c":
#        ast = generate_ast_c(tokens)

#for function in ast:
#    if function.name == "main":
#        for intruction in function.instructions:
#            print(intruction)

#for function in ast:
#    if isinstance(function, FunctionNode):
#        if function.name == "main":
#            print(function.instructions)

functions = {}

for function in ast:
    if isinstance(function, FunctionNode):
        functions[function.name] = function

type_check(ast, functions)

if not os.path.exists("build"):
    os.makedirs("build")

if name:
    compile_linux_x86_64(ast, name.replace(".barely", ""), functions)
