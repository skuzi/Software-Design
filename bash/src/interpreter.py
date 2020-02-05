import re

from src.utils import remove_quotes, substitute_variables, split_into_commands, split_command_into_args
from src.executors import WcExecutor, PwdExecutor, CatExecutor, EchoExecutor, ExternalExecutor, ExecutionException
import os

executors = {
    'wc': WcExecutor,
    'pwd': PwdExecutor,
    'cat': CatExecutor,
    'echo': EchoExecutor
}
assignment_pattern = re.compile("([a-zA-Z_]+\w*)=(.*)")


def execute_pipeline(commands):
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
    return len(args) == 1 and assignment_pattern.match(args[0]) is not None


def is_exit(args):
    return len(args) == 1 and args[0] == 'exit'
