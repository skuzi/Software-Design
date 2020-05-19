import os
import subprocess
from abc import abstractmethod


class Executor:
    """ Class representing executor of some command """
    @staticmethod
    @abstractmethod
    def execute(args, stdin=None):
        """ Executes command bash-like 
        :param args: arguments of a command, list of strings
        :param stdin: input string of a command (e.g in 'echo "123" | cat' 123 would be an stdin in cat command)
        """
        pass


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
