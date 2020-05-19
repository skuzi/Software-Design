import os
import subprocess
from abc import abstractmethod
from src.parsers import grep_parser, ParsingException
import re


class Executor:
    """Base class for all executors"""
    @staticmethod
    @abstractmethod
    def execute(args, stdin=None):
        """Executes a command
        Returns a string with result of running a command on args with given input

        :param args: arguments of a command
        :param stdin: input string given to a command
        :return: string with a result of running a command on args with given input
        """
        raise NotImplementedError


class ExecutionException(Exception):
    """Class for all exceptions occurring during execution of commands"""
    pass


class EchoExecutor(Executor):
    """"Class for executing echo command"""
    @staticmethod
    def execute(args, stdin=None):
        """Returns all its arguments, separated by whitespace"""
        return " ".join(args)


class CatExecutor(Executor):
    """Class for executing cat command"""
    @staticmethod
    def execute(args, stdin=None):
        """
        Returns contents of given files, or stdin if none are given

        :param args: list of strings specifying paths to files
        :param stdin: string which is to be returned when no files are given
        :return: contents of given files, or stdin if none are given
        """
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
    """Class for executing wc command"""
    @staticmethod
    def execute(args, stdin=None):
        """
        For each file in args returns a line, containing the following information:
        amount of lines in file, amount of words in file, amount of bytes in file
        If no files are given, returns one line with such information for stdin

        :param args: list of strings specifying paths to files
        :param stdin: string which is to be counted when no files are given
        :return: 3 integers for each file, separated by line break ('\n')
        :raise: ExecutionException if IOError occurred while reading files, or not args nor stdin were provided
        """
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
    """Class for executing pwd command"""
    @staticmethod
    def execute(args, stdin=None):
        """Returns current working directory"""
        return os.getcwd()


class GrepExecutor(Executor):
    """Class for executing grep command"""
    @staticmethod
    def execute(args, stdin=None):
        """
        Executes grep command like in bash
        usage: grep [-h] [-i] [-w] [-A LINES_AFTER] pattern [file]
        optional arguments:
          -h, --help      shows help message
          -i              ignores case while pattern matching if provided
          -w              looks only for matches that are full words if provided
          -A LINES_AFTER  how many lines will be printed after each matching line (default is 0)

        :param args: a list of arguments matching usage
        :param stdin: string used as input if no file is provided
        :return: string containing matching lines and LINES_AFTER after each matching line
        :raise: ExecutionException, if IOError occurred while reading from the file,
        or args list does not match the usage pattern,
        or neither file nor stdin are provided
        """
        def find_matches(lines, args):
            pattern_word = args.pattern
            if args.word_match:
                pattern_word = r'\b' + pattern_word + r'\b'
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
    """Executes command which are not builtin"""
    @staticmethod
    def execute(args, stdin=None):
        """
        Executes a command
        :param args: list of arguments for the command. First argument must be command name
        :param stdin: string passed to command as input
        :return: result of command execution
        :raise: ExecutionException, if either command was not found in PATH, or error occurred during command execution
        """
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
