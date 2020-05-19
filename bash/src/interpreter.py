import re

from src.utils import remove_quotes, substitute_variables, split_into_commands, split_command_into_args
from src.executors import WcExecutor, PwdExecutor, CatExecutor, EchoExecutor, ExternalExecutor, ExecutionException, GrepExecutor
import os

executors = {
    'wc': WcExecutor,
    'pwd': PwdExecutor,
    'cat': CatExecutor,
    'echo': EchoExecutor,
    'grep': GrepExecutor
}
assignment_pattern = re.compile("([a-zA-Z_]+\w*)=(.*)")


def execute_pipeline(commands):
    """
    Parses commands from given string and executes them as a pipeline
    Each command output is passed as input to next command

    :param commands: string containing commands separated by pipe symbol (|)
    :return: string containing result of last command, or None if it returns nothing
    """
    pipeline = list(map(substitute_variables, split_into_commands(commands)))
    if '' in pipeline:
        return 'error while parsing'
    stdin = None
    for command in pipeline:
        args = list(map(remove_quotes, split_command_into_args(command)))
        if is_assignment(args):
            match = assignment_pattern.match(args[0])
            os.environ[match[1]] = match[2]
            continue
        if is_exit(args):
            return None

        try:
            if args[0] in executors:
                stdin = executors[args[0]].execute(args[1:], stdin)
            else:
                stdin = ExternalExecutor.execute(args, stdin)
        except ExecutionException as exception:
            return exception

    return stdin if stdin else ''


def is_assignment(args):
    """Determines whether command is an assignment"""
    return len(args) == 1 and assignment_pattern.match(args[0]) is not None


def is_exit(args):
    """Determines whether command is an exit command"""
    return len(args) == 1 and args[0] == 'exit'
