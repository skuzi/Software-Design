from argparse import ArgumentParser


class Parser(ArgumentParser):
    def error(self, message):
        raise ParsingException(message)

    def add_string(self, *args, **kwargs):
        self.add_argument(*args, **kwargs, type=str)

    def add_int(self, *args, **kwargs):
        self.add_argument(*args, **kwargs, type=int)

    def add_flag(self, *args, **kwargs):
        self.add_argument(*args, **kwargs, action='store_true')

    def add_string_args(self, *args, **kwargs):
        self.add_argument(*args, **kwargs, type=str, nargs='*')


class ParsingException(Exception):
    pass


class ParserBuilder:
    def __init__(self):
        self.parser = Parser()

    def with_string(self, name, value, help):
        if name.startswith('-'):
            self.parser.add_string(name, dest=value, help=help)
        else:
            self.parser.add_string(name, help=help)
        return self

    def with_optional_string(self, name, value, help):
        if name.startswith('-'):
            self.parser.add_string(name, dest=value, help=help, nargs='?')
        else:
            self.parser.add_string(name, help=help, nargs='?')
        return self

    def with_int(self, name, value, default, help):
        self.parser.add_int(name, dest=value, default=default, help=help)
        return self

    def with_flag(self, name, value, help):
        self.parser.add_flag(name, dest=value, help=help)
        return self

    def with_params(self, name, value, help):
        self.parser.add_string_args(name, dest=value, help=help)
        return self

    def build(self):
        return self.parser


grep_parser = ParserBuilder()\
    .with_string('pattern', 'pattern', 'search pattern')\
    .with_optional_string('file', 'file', 'file to look into')\
    .with_flag('-i', 'ignore_case', 'grep will be ignore case if flag is present')\
    .with_flag('-w', 'word_match', 'grep will look only for matches that are full words if flag is present')\
    .with_int('-A', 'lines_after', 0, 'how many lines will be printed after each match')\
    .build()
