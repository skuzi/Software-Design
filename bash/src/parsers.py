from argparse import ArgumentParser


class Parser(ArgumentParser):
    """Class inheriting argparse.ArgumentParser in order to process errors correctly"""
    def error(self, message):
        """Raises ParsingException if parsing error occurred"""
        raise ParsingException(message)

    def add_string(self, *args, **kwargs):
        """Adds string as argument"""
        self.add_argument(*args, **kwargs, type=str)

    def add_int(self, *args, **kwargs):
        """Adds int as argument"""
        self.add_argument(*args, **kwargs, type=int)

    def add_flag(self, *args, **kwargs):
        """Adds boolean flag as argument"""
        self.add_argument(*args, **kwargs, action='store_true')

    def add_string_args(self, *args, **kwargs):
        """Adds list of string as argument"""
        self.add_argument(*args, **kwargs, type=str, nargs='*')


class ParsingException(Exception):
    """Exception for all errors during parsing"""
    pass


class ParserBuilder:
    """Class for easy parsers building"""
    def __init__(self):
        """Inits this instance of builder with parser containing no arguments"""
        self.parser = Parser()

    def with_string(self, name, value, help):
        """
        Adds string as argument to parser
        :param name: argument name in command arguments
        :param value: argument name in dictionary of parser
        :param help: short description of what this argument specifies
        :return: this builder with new argument in parser
        """
        if name.startswith('-'):
            self.parser.add_string(name, dest=value, help=help)
        else:
            self.parser.add_string(name, help=help)
        return self

    def with_optional_string(self, name, value, help):
        """
        Adds string as optional argument to parser
        :param name: argument name in command arguments
        :param value: argument name in dictionary of parser
        :param help: short description of what this argument specifies
        :return: this builder with new argument in parser
        """
        if name.startswith('-'):
            self.parser.add_string(name, dest=value, help=help, nargs='?')
        else:
            self.parser.add_string(name, help=help, nargs='?')
        return self

    def with_int(self, name, value, default, help):
        """
        Adds integer as argument to parser
        :param name: argument name in command arguments
        :param value: argument name in dictionary of parser
        :param default: default value of argument
        :param help: short description of what this argument specifies
        :return: this builder with new argument in parser
        """
        self.parser.add_int(name, dest=value, default=default, help=help)
        return self

    def with_flag(self, name, value, help):
        """
        Adds boolean flag as argument to parser
        :param name: argument name in command arguments
        :param value: argument name in dictionary of parser
        :param help: short description of what this argument specifies
        :return: this builder with new argument in parser
        """
        self.parser.add_flag(name, dest=value, help=help)
        return self

    def with_params(self, name, value, help):
        """
        Adds list of strings as argument to parser
        :param name: argument name in command arguments
        :param value: argument name in dictionary of parser
        :param help: short description of what this argument specifies
        :return: this builder with new argument in parser
        """
        self.parser.add_string_args(name, dest=value, help=help)
        return self

    def build(self):
        """Returns built parser with all arguments provided"""
        return self.parser


grep_parser = ParserBuilder()\
    .with_string('pattern', 'pattern', 'search pattern')\
    .with_optional_string('file', 'file', 'file to look into')\
    .with_flag('-i', 'ignore_case', 'grep will be ignore case if flag is present')\
    .with_flag('-w', 'word_match', 'grep will look only for matches that are full words if flag is present')\
    .with_int('-A', 'lines_after', 0, 'how many lines will be printed after each match')\
    .build()
