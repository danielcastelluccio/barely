import sys
import os

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

class OpenBracketToken:
    def __str__(self) -> str:
        return "[OpenBracket]"

class ClosedBracketToken:
    def __str__(self) -> str:
        return "[ClosedBracket]"

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

def is_num(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def tokenize_small(contents):
    tokens = []

    if contents == "function" or contents == "return":
        tokens.append(KeywordToken(contents))
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
            tokens.append(ClosedParenthesisToken())
        elif character == '{' and not in_quotes:
            tokens.append(OpenBracketToken())
        elif character == '}' and not in_quotes:
            tokens.append(ClosedBracketToken())
        elif character == ';' and not in_quotes:
            tokens.extend(tokenize_small(buffer))
            tokens.append(SemiColonToken())
            buffer = ""
        elif character == ',' and not in_quotes:
            tokens.extend(tokenize_small(buffer))
            tokens.append(CommaToken())
            buffer = ""
        elif character == ':' and not in_quotes:
            tokens.append(ColonToken())
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
    def __init__(self, name, instructions, parameters, returns):
        self.name = name
        self.instructions = instructions
        self.parameters = parameters
        self.returns = returns

class InvokeNode:
    def __init__(self, name):
        self.name = name

class StringNode:
    def __init__(self, string):
        self.string = string

class IntegerNode:
    def __init__(self, integer):
        self.integer = integer

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
            elif token.word == "return":
                statement, index = get_expression(tokens, index + 1)

                if current_function:
                    current_function.instructions.extend(statement)
                    current_function.instructions.append(ReturnNode())
        elif isinstance(token, ClosedBracketToken):
            ast.append(current_function)
        else:
            statement, index = get_expression(tokens, index)

            if current_function:
                current_function.instructions.extend(statement)

        index += 1

    return ast

def get_function_declaration(tokens, index):
    name = None
    searching_returns = False
    returns = []
    while not isinstance(tokens[index], OpenBracketToken):
        token = tokens[index]

        if isinstance(token, NameToken) and not name:
            name = token.name
        elif isinstance(token, ClosedParenthesisToken):
            searching_returns = True
        elif isinstance(token, NameToken) and searching_returns:
            returns.append(token.name)

        index += 1

    # TODO: actually calculate
    return FunctionNode(name, [], [], returns), index

def get_expression(tokens, index):
    statement = []

    if isinstance(tokens[index], NameToken):
        invoke, index = get_invoke(tokens, index + 2, tokens[index].name)
        statement.extend(invoke)
    elif isinstance(tokens[index], StringToken):
        statement.append(StringNode(tokens[index].string))
        index += 1
    elif isinstance(tokens[index], NumberToken):
        statement.append(IntegerNode(tokens[index].number))
        index += 1

    return statement, index

def get_invoke(tokens, index, name):
    statement = []

    while not isinstance(tokens[index], ClosedParenthesisToken):
        expression, index = get_expression(tokens, index)
        statement.extend(expression)

    statement.append(InvokeNode(name))

    return statement, index

def get_size_linux_x86_64(types):
    size = 0

    for type in types:
        if type == "*" or type == "integer":
            size += 8

    return size

def compile_linux_x86_64(ast, name):
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

    contents_data = ""
    data_index = 0

    function_parameters = {}
    function_returns = {}

    #Builtin functions
    function_parameters["@print"] = ["*", "integer"]
    function_returns["@print"] = []

    for function in ast:
        function_parameters[function.name] = function.parameters
        function_returns[function.name] = function.returns

    for function in ast:
        contents += function.name + ":\n"

        contents += "push rbp\n"
        contents += "mov rbp, rsp\n"

        for instruction in function.instructions:
            if isinstance(instruction, InvokeNode):
                contents += "call " + instruction.name + "\n"
                contents += "add rsp, " + str(get_size_linux_x86_64(function_parameters[instruction.name])) + "\n"
                for i in range(0, get_size_linux_x86_64(function_returns[instruction.name]) // 8):
                    contents += "push r" + str(8 + i) + "\n"
            elif isinstance(instruction, StringNode):
                contents += "push " + str(len(instruction.string)) + "\n"
                contents += "push _" + str(data_index) + "\n"
                contents_data += "_" + str(data_index) + ": db \"" + instruction.string + "\", 10\n"
                data_index += 1
            elif isinstance(instruction, IntegerNode):
                contents += "push " + str(instruction.integer) + "\n"
            elif isinstance(instruction, ReturnNode):
                for i in range(0, len(function_returns[function.name])):
                    contents += "pop r" + str(8 + i) + "\n"

                contents += "mov rsp, rbp\n"
                contents += "pop rbp\n"
                contents += "ret\n"

        contents += "mov rsp, rbp\n"
        contents += "pop rbp\n"
        contents += "ret\n"

    contents += "segment readable\n"
    contents += contents_data

    fasm_file.write(contents)
    fasm_file.close()

    os.system("fasm " + fasm_file.name + " build/" + name)

file = open(sys.argv[1])
contents = file.read()

tokens = tokenize(contents)
ast = generate_ast(tokens)

if not os.path.exists("build"):
    os.makedirs("build")

compile_linux_x86_64(ast, file.name.replace(".barely", ""))
