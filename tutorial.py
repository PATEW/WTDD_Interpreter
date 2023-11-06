INTEGER, PLUS, EOF = 'INTEGER', 'PLUS', 'EOF'


class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return "Token({type}, {value})".format(
                type=self.type,
                value=repr(self.value)
                )

    def __repr__(self):
        return self.__str__()


class Interpreter(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_token = None

    def error(self):
        raise Exception("Error parsing input")

    # breaks apart sentence into tokens one at a time
    def get_next_token(self):
        # Lexer (aka tokenizer)
        text = self.text

        # is self.pos inddex past end of self.text?
        # if so, return EOF token bc we're at the end
        if self.pos > len(text) - 1:
            return Token(EOF, None)

        # gets char at position self.pos and
        # decide what token to create based on single char
        current_char = text[self.pos]

        # if char is digit, make it an integer token
        # increment self.pos index
        # return INTEGER token
        if current_char.isdigit():
            token = Token(INTEGER, int(current_char))
            self.pos += 1
            return token

        if current_char == '+':
            token = Token(PLUS, current_char)
            self.pos += 1
            return token

        # nothing found
        self.error()

    # compare current token with passed token
    # if type matches, 'eat' the token
    # and assign next token to self.current_token
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.get_next_token()
        else:
            self.error()

    def expression(self):
        # currently int + int
        self.current_token = self.get_next_token()

        # expect single digit int
        left = self.current_token
        self.eat(INTEGER)

        # expect '+' token
        operator = self.current_token
        self.eat(PLUS)

        # expect single digit int
        right = self.current_token
        self.eat(INTEGER)

        # current token set to EOF after

        # if here, sequence is correct, perform operation
        result = left.value + right.value
        return result


def main():
    while True:
        try:
            text = input("calc> ")
        except EOFError:
            break
        if not text:
            continue
        interpreter = Interpreter(text)
        result = interpreter.expression()
        print(result)


if __name__ == "__main__":
    main()
