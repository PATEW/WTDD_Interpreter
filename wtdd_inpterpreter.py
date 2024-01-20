# Token types:
INTEGER, PLUS, MINUS, MUL, FLDIV, LPAREN, RPAREN, EOF = (
    'INTEGER', 'PLUS', 'MINUS', 'MUL', 'FLDIV',
    '(', ')',  'EOF'
)


class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    # string representaiton
    def __str__(self):
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
            )

    def __repr__(self):
        return self.__str__()


class Lexer(object):
    def __init__(self, text):
        # client string input, e.g. "4 + 2 * 3 - 6 / 2"
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        """Return a (multidigit) integer consumed from the input."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def word(self):
        """Return a word consumed from the input"""
        result = ''
        while self.current_char is not None and self.current_char.isalpha():
            result += self.current_char
            self.advance()
        return result

    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)

        This method is responsible for breaking a sentence
        apart into tokens/words. One token at a time.
        """
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalpha():
                word = self.word()
                if word == 'the':
                    return Token(INTEGER, 0)
                elif word == 'that':
                    return Token(INTEGER, 1)
                elif word == 'this':
                    return Token(INTEGER, 2)
                elif word == 'um':
                    return Token(PLUS, 'um')
                elif word == 'umm':
                    return Token(MINUS, 'umm')
                elif word == 'uh':
                    return Token(MUL, 'uh')
                elif word == 'uhh':
                    return Token(FLDIV, 'uhh')
                elif word == 'be':
                    return Token(LPAREN, 'be')
                elif word == 'gon':
                    return Token(RPAREN, 'gon')

            self.error()

        return Token(EOF, None)

    def peek_next_char(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        return self.text[peek_pos]

###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################

class AST(object):
    pass


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Concat(AST):
    def __init__(self, items):
        self.items = items


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        """factor : INTEGER | LPAREN expr RPAREN"""
        token = self.current_token
        if token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node

    def term(self):
        """Parse terms which can be either a single number or concatenation of numbers."""
        # Start with a single factor (number)
        node = self.factor()

        # If the next token is a number, it's a concatenation
        while self.current_token.type == INTEGER:
            concat_values = [node]

            # Keep concatenating while there are numbers
            while self.current_token.type == INTEGER:
                concat_values.append(self.factor())

            # Create a Concat node with all concatenated values
            if len(concat_values) > 1:
                node = Concat(concat_values)

        return node

    def expr(self):
        # Start by parsing a term (which might be a number or a concatenation of numbers)
        node = self.term()

        # Process any arithmetic operations following the term
        while self.current_token.type in (PLUS, MINUS, MUL, FLDIV):
            token = self.current_token

            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)
            elif token.type == MUL:
                self.eat(MUL)
            elif token.type == FLDIV:
                self.eat(FLDIV)

            # Create a BinOp node with the current arithmetic operation
            node = BinOp(left=node, op=token, right=self.term())

        return node

    def parse(self):
        return self.expr()


###############################################################################
#                                                                             #
#  INTERPRETER                                                                #
#                                                                             #
###############################################################################

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):
        if node.op.type in (PLUS, MINUS, MUL, FLDIV):
            left = self.visit(node.left)
            right = self.visit(node.right)
            if node.op.type == PLUS and node.op.value != 'concat':
                return left + right
            elif node.op.type == MINUS:
                return left - right
            elif node.op.type == MUL:
                return left * right
            elif node.op.type == FLDIV:
                return left // right
            elif node.op.value == 'concat':
                # Concatenation
                return str(left) + str(right)

    def visit_Num(self, node):
        return node.value

    def visit_Concat(self, node):
        result = ''
        for item in node.items:
            result += str(self.visit(item))
        return int(result)

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)


def main():
    while True:
        try:
            try:
                text = raw_input('wtdd> ')
            except NameError:  # Python3
                text = input('wtdd> ')
        except EOFError:
            break
        if not text:
            continue

        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        print(result)


if __name__ == '__main__':
    main()
