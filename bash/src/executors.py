import os
import subprocess
from abc import abstractmethod
from parsers import grep_parser, ParsingException
import re


class Executor:
    @staticmethod
    @abstractmethod
    def execute(args, stdin=None):
        raise NotImplementedError


class ExecutionException(Exception):
    pass


class EchoExecutor(Executor):
    @staticmethod
    def execute(args, stdin=None):
        return " ".join(args)


class CatExecutor(Executor):
    @staticmethod
    def execute(args, stdin=None):
        buffer_size = 512
        if not args:
            return stdin
        else:
            output = ''
            for filename in args:
                try:
                    with open(filename, 'r') as file:
                        bytes_read = -1
                        last_pos = 0
                        while bytes_read != 0:
                            output += file.read(buffer_size)
                            cur_pos = file.tell()
                            bytes_read = cur_pos - last_pos
                            last_pos = cur_pos
                except IOError as error:
                    raise ExecutionException(f"cat error: {error}")
            return output


class WcExecutor(Executor):
    @staticmethod
    def execute(args, stdin=None):
        def lines(string):
            return len(string.split('\n'))

        def words(string):
            return len(string.split())

        def bytes(string):
            return len(string.encode('utf-8'))

        if not args:
            if not stdin:
                raise ExecutionException("no input given to wc")
            return "%d %d %d" % (lines(stdin), words(stdin), bytes(stdin))
        else:
            total_lines = 0
            total_words = 0
            total_bytes = 0
            output = ''
            for filename in args:
                try:
                    file_lines = 0
                    file_words = 0
                    file_bytes = 0
                    with open(filename, 'r') as file:
                        for line in file:
                            file_lines += 1
                            file_words += words(line)
                            file_bytes += bytes(line)

                    total_lines += file_lines
                    total_words += file_words
                    total_bytes += file_bytes

                    output += f"{file_lines} {file_words} {file_bytes}\n"
                except IOError as error:
                    raise ExecutionException(f"wc error: {error}")

            output += f"total {total_lines} {total_words} {total_bytes}"
            return output


class PwdExecutor(Executor):
    @staticmethod
    def execute(args, stdin=None):
        return os.getcwd()


class GrepExecutor(Executor):
    @staticmethod
    def execute(args, stdin=None):
        def find_matches(lines, args):
            pattern_word = args.pattern
            if args.word_match:
                pattern_word = '\b' + pattern_word + '\b'
            if args.ignore_case:
                pattern = re.compile(pattern_word, re.IGNORECASE)
            else:
                pattern = re.compile(pattern_word)

            output = ""
            lines_to_print = 0
            for line in lines:
                if pattern.search(line):
                    lines_to_print = args.lines_after + 1
                if lines_to_print > 0:
                    output += line + '\n'
                lines_to_print -= 1

            return output[:-1]

        try:
            args = grep_parser.parse_args(args)
        except ParsingException as error:
            raise ExecutionException(f"grep error: {error}")

        if not args.file and stdin is None:
            raise ExecutionException("grep error: no input passed to grep")

        if args.file:
            try:
                with open(args.file, 'r') as file:
                    return find_matches([line.rstrip() for line in file], args)
            except IOError as error:
                raise ExecutionException(f"grep error: {error}")
        else:
            return find_matches(stdin.split('\n'), args)


class ExternalExecutor(Executor):
    @staticmethod
    def execute(args, stdin=None):
        if args is None:
            return
        if stdin:
            stdin = stdin.encode()
        try:
            process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, input=stdin)
            return process.stdout.decode().rstrip()
        except subprocess.CalledProcessError as error:
            raise ExecutionException(f"{args[0]} error: {error.stderr.decode()}")
        except FileNotFoundError:
            raise ExecutionException(f"{args[0]} command not found")
