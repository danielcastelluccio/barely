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

class NumberToken:
    def __init__(self, number):
        self.number = number

    def __str__(self) -> str:
        return "[Number: '" + str(self.number) + "']"

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

keywords = ["function", "return", "variable"]

def tokenize_small(contents):
    tokens = []

    if contents in keywords:
        tokens.append(KeywordToken(contents))
    elif "_" in contents and is_num(contents.split("_")[0]) and is_num(contents.split("_")[1]):
        split = contents.split("_")
        tokens.append(NumberSplitToken(int(split[0]), int(split[1])))
    elif is_num(contents):
        tokens.append(NumberToken(int(contents)))
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
            tokens.append(NameToken(buffer))
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

class LongNode:
    def __init__(self, integer1, integer2):
        self.integer1 = integer1
        self.integer2 = integer2

class ReturnNode:
    pass

def generate_ast(tokens):
    ast = []
    
    current_function = None
    index = 0
    while index < len(tokens):
        token = tokens[index]

        if isinstance(token, KeywordToken):
            if token.word == "function":
                current_function, index = get_function_declaration(tokens, index + 1)
                ast.append(current_function)
            elif token.word == "return":
                statement, index = get_expression(tokens, index + 1)

                if current_function:
                    current_function.instructions.extend(statement)
                    current_function.instructions.append(ReturnNode())
            elif token.word == "variable":
                name = tokens[index + 1].name
                type = tokens[index + 3].name
                statement, index = get_assign(tokens, index + 5, name)

                if current_function:
                    current_function.instructions.append(DeclareNode(name, type))
                    current_function.instructions.extend(statement)
        elif isinstance(token, NameToken) and isinstance(tokens[index + 1], NameToken) and tokens[index + 1].name == "=":
            statement, index = get_assign(tokens, index + 2, tokens[index].name)

            if current_function:
                current_function.instructions.extend(statement)
        else:
            statement, index = get_expression(tokens, index)

            if current_function:
                current_function.instructions.extend(statement)

        index += 1

    for function in ast:
        for instruction in function.instructions:
            if isinstance(instruction, AssignNode):
                if not instruction.name in function.locals:
                    function.locals.append(instruction.name)

    return ast

def get_function_declaration(tokens, index):
    name = None
    searching_returns = False
    parameters = OrderedDict()
    returns = []

    name_index = 0
    parameter_name_cache = ""

    while not isinstance(tokens[index], OpenCurlyBracketToken):
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

def get_expression(tokens, index):
    statement = []

    if isinstance(tokens[index], NameToken) and isinstance(tokens[index + 1], OpenParenthesisToken):
        invoke, index = get_invoke(tokens, index + 1, tokens[index].name)
        statement.extend(invoke)
    elif isinstance(tokens[index], NameToken):
        retrieve, index = get_retrieve(index + 1, tokens[index].name)
        statement.extend(retrieve)
    elif isinstance(tokens[index], StringToken):
        statement.append(StringNode(tokens[index].string))
        index += 1
    elif isinstance(tokens[index], NumberToken):
        statement.append(IntegerNode(tokens[index].number))
        index += 1
    elif isinstance(tokens[index], NumberSplitToken):
        statement.append(LongNode(tokens[index].number1, tokens[index].number2))
        index += 1

    return statement, index

def get_invoke(tokens, index, name):
    statement = []

    index += 1
    while not isinstance(tokens[index], ClosedParenthesisToken):
        expression, index = get_expression(tokens, index)
        statement = expression + statement
        if isinstance(tokens[index], CommaToken):
            index += 1

    statement.append(InvokeNode(name))

    index += 1

    return statement, index

def get_assign(tokens, index, name):
    statement = []

    while not isinstance(tokens[index], SemiColonToken):
        expression, index = get_expression(tokens, index)
        statement.extend(expression)

    statement.append(AssignNode(name))

    return statement, index

def get_retrieve(index, name):
    statement = []

    statement.append(RetrieveNode(name))

    return statement, index

def type_check(ast, functions):
    for function in ast:
        variables = {}
        types = []

        for parameter in function.parameters:
            variables[parameter] = function.parameters[parameter]

        for instruction in function.instructions:
            if isinstance(instruction, DeclareNode):
                variables[instruction.name] = instruction.type
            elif isinstance(instruction, IntegerNode):
                types.append("integer")
            elif isinstance(instruction, LongNode):
                types.append("long")
            elif isinstance(instruction, AssignNode):
                popped = types.pop()
                if not variables[instruction.name] == popped:
                    print("TYPECHECK: Assign of " + instruction.name + " in " + function.name + " expected " + variables[instruction.name] + ", got " + popped + ".")
                    exit()
            elif isinstance(instruction, RetrieveNode):
                types.append(variables[instruction.name])
            elif isinstance(instruction, InvokeNode):
                called_function = functions[instruction.name]
                for parameter in called_function.parameters.values():
                    popped = types.pop()
                    if not parameter == popped:
                        print("TYPECHECK: Invoke of " + instruction.name + " in " + function.name + " expected " + parameter + ", got " + popped + ".")
                        exit()

                for return_ in called_function.returns:
                    types.append(return_)
            elif isinstance(instruction, ReturnNode):
                for return_ in function.returns:
                    popped = types.pop()
                    if not return_ == popped:
                        print("TYPECHECK: Return in " + function.name + " expected " + return_ + ", got " + popped + ".")
                        exit()
            else:
                print(instruction)
        

def get_size_linux_x86_64(types):
    size = 0

    if isinstance(types, str):
        types = [types]

    for type in types:
        if type == "*" or type == "integer":
            size += 8
        elif type == "long":
            size += 16

    return size

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

    contents += "@print:\n"
    contents += "push rbp\n"
    contents += "mov rbp, rsp\n"
    contents += "mov rax, 1\n"
    contents += "mov rdi, 1\n"
    contents += "mov rsi, [rbp+16]\n"
    contents += "mov rdx, [rbp+24]\n"
    contents += "syscall\n"
    contents += "mov rsp, rbp\n"
    contents += "pop rbp\n"
    contents += "ret\n"

    contents += "@length:\n"
    contents += "push rbp\n"
    contents += "mov rbp, rsp\n"
    contents += "mov rax, 0\n"
    contents += "mov rdi, [rbp+16]\n"
    contents += "mov rcx, -1\n"
    contents += "repne scasb\n"
    contents += "not rcx\n"
    contents += "sub rcx, 1\n"
    contents += "mov [return_memory], rcx\n"
    contents += "mov rsp, rbp\n"
    contents += "pop rbp\n"
    contents += "ret\n"

    contents += "@add_long:\n"
    contents += "push rbp\n"
    contents += "mov rbp, rsp\n"
    contents += "mov rax, 0\n"
    contents += "mov rax, [rbp+16]\n"
    contents += "add rax, [rbp+24]\n"
    contents += "mov [return_memory], rax\n"
    contents += "mov rsp, rbp\n"
    contents += "pop rbp\n"
    contents += "ret\n"

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
ret
"""

    contents_data = ""
    data_index = 0

    for function in ast:
        contents += function.name + ":\n"

        local_types = [None] * len(function.locals)

        for instruction in function.instructions:
            if isinstance(instruction, DeclareNode):
                local_types[function.locals.index(instruction.name)] = instruction.type

        contents += "push rbp\n"
        contents += "mov rbp, rsp\n"
        contents += "sub rsp, " + str(get_size_linux_x86_64(local_types)) + "\n"

        variables = {}

        local_types = [None] * len(function.locals)

        for instruction in function.instructions:
            if isinstance(instruction, InvokeNode):
                contents += "call " + instruction.name + "\n"
                contents += "add rsp, " + str(get_size_linux_x86_64(functions[instruction.name].parameters.values())) + "\n"
                size = get_size_linux_x86_64(functions[instruction.name].returns)
                contents += "sub rsp, " + str(size) + "\n"
                i = 0
                while i < size:
                    if size - i >= 8:
                        contents += "mov rax, [return_memory+" + str(i) + "]\n"
                        contents += "mov [rsp+" + str(i) + "], rax\n"
                        i += 8
                    else:
                        print("non multiple of 8 size 1")
                        exit()
                    #elif size - i >= 4:
                    #    contents += "mov eax, [return_memory+" + str(i) + "]\n"
                    #    contents += "mov [rsp+" + str(i) + "], eax\n"
                    #    i += 4
                    #elif size - i >= 2:
                    #    contents += "mov ax, [return_memory+" + str(i) + "]\n"
                    #    contents += "mov [rsp+" + str(i) + "], ax\n"
                    #    i += 2
                    #else:
                    #    contents += "mov ah, [return_memory+" + str(i) + "]\n"
                    #    contents += "mov [rsp+" + str(i) + "], ah\n"
                    #    i += 1
            elif isinstance(instruction, DeclareNode):
                variables[instruction.name] = instruction.type
                local_types[function.locals.index(instruction.name)] = instruction.type
            elif isinstance(instruction, RetrieveNode):
                if instruction.name in function.parameters:
                    i = -1

                    for index, parameter in enumerate(function.parameters):
                        if parameter == instruction.name:
                            i = index

                    location = get_size_linux_x86_64(list(function.parameters.values())[0 : i])
                    size = get_size_linux_x86_64(function.parameters[instruction.name])
                    contents += "sub rsp, " + str(size) + "\n"
                    j = 0
                    while j < size:
                        if size - j >= 8:
                            contents += "mov rax, [rbp+" + str(16 + location + j) + "]\n"
                            contents += "mov [rsp+" + str(j) + "], rax\n"
                            j += 8
                        else:
                            print("non multiple of 8 size 2")
                            exit()
                else:
                    i = function.locals.index(instruction.name)
                    location = get_size_linux_x86_64(local_types[0 : i])
                    size = get_size_linux_x86_64(local_types[i])

                    contents += "sub rsp, " + str(size) + "\n"

                    j = 0
                    while j < size:
                        if size - j >= 8:
                            contents += "mov rax, [rbp-" + str(8 + location + size - j - 8) + "]\n"
                            contents += "mov [rsp+" + str(j) + "], rax\n"
                            j += 8
                        else:
                            print("non multiple of 8 size 5")
                            exit()

            elif isinstance(instruction, AssignNode):
                i = function.locals.index(instruction.name)

                size = get_size_linux_x86_64(variables[instruction.name])
                location = get_size_linux_x86_64(local_types[0 : i])
                i = 0
                while i < size:
                    if size - i >= 8:
                        contents += "mov rax, [rsp+" + str(i) + "]\n"
                        contents += "mov [rbp-" + str(8 + size - (location + i) - 8) + "], rax\n"
                        i += 8
                    else:
                        print("non multiple of 8 size 3")
                        exit()
                contents += "add rsp, " + str(((size + 7) & (-8))) + "\n"
            elif isinstance(instruction, StringNode):
                contents += "push _" + str(data_index) + "\n"
                contents_data += "_" + str(data_index) + ": db \"" + instruction.string + "\", 0\n"
                data_index += 1
            elif isinstance(instruction, IntegerNode):
                contents += "push " + str(instruction.integer) + "\n"
            elif isinstance(instruction, LongNode):
                contents += "push " + str(instruction.integer2) + "\n"
                contents += "push " + str(instruction.integer1) + "\n"
            elif isinstance(instruction, ReturnNode):
                size = get_size_linux_x86_64(functions[function.name].returns)
                i = 0
                while i < size:
                    if size - i >= 8:
                        contents += "mov rax, [rsp+" + str(i) + "]\n"
                        contents += "mov [return_memory+" + str(i) + "], rax\n"
                        i += 8
                    else:
                        print("non multiple of 8 size 4")
                        exit()

                contents += "mov rsp, rbp\n"
                contents += "pop rbp\n"
                contents += "ret\n"

        contents += "mov rsp, rbp\n"
        contents += "pop rbp\n"
        contents += "ret\n"

    contents += "segment readable\n"
    contents += contents_data

    contents += "segment readable writable\n"
    contents += "return_memory: rb 128"

    fasm_file.write(contents)
    fasm_file.close()

    os.system("fasm " + fasm_file.name + " build/" + name)

file = open(sys.argv[1])
contents = file.read()

tokens = tokenize(contents)
ast = generate_ast(tokens)

#Builtin functions
functions = {}
functions["@print"] = FunctionNode("@print", [], {"string": "*", "size": "integer"}, [], [])
functions["@length"] = FunctionNode("@length", [], {"string": "*"}, ["integer"], [])
functions["@print_integer"] = FunctionNode("@print_integer", [], {"integer": "integer"}, [], [])
functions["@add_long"] = FunctionNode("@add_long", [], {"long": "long"}, ["integer"], [])

for function in ast:
    functions[function.name] = function

type_check(ast, functions)

if not os.path.exists("build"):
    os.makedirs("build")

compile_linux_x86_64(ast, file.name.replace(".barely", ""), functions)
