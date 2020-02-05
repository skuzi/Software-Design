import os
import re
from enum import Enum


class State(Enum):
    UNQUOTED = 0
    STRONG_QUOTED = 1
    WEAK_QUOTED = 2


def eval_state(state, c):
    if state is State.STRONG_QUOTED and c == '\'':
        return State.UNQUOTED
    if state is State.WEAK_QUOTED and c == '"':
        return State.UNQUOTED
    if state is State.UNQUOTED:
        if c == '"':
            return State.WEAK_QUOTED
        if c == '\'':
            return State.STRONG_QUOTED
    return state


def find_first_unquoted(line, pattern):
    state = State.UNQUOTED
    for i, c in enumerate(line):
        state = eval_state(state, c)
        if state is State.UNQUOTED and pattern.match(c):
            return i
    return len(line)


def find_unquoted(line, pattern, begin=0):
    if not line:
        return []
    ind = find_first_unquoted(line, pattern)
    return find_unquoted(line[ind + 1:], pattern, begin + ind + 1) + [begin + ind]


def split_with_quotes(command, pattern):
    split_indices = find_unquoted(command, pattern) + [-1]
    return [command[split_indices[i + 1] + 1:split_indices[i]].strip() for i in range(len(split_indices) - 2, -1, -1)]


def split_into_commands(command):
    return split_with_quotes(command, re.compile(r'\|'))


def substitute_variables(command):
    if not command:
        return ''
    state = State.UNQUOTED
    result = ''
    for (i, c) in enumerate(command):
        state = eval_state(state, c)
        if state is State.STRONG_QUOTED:
            result += c
            continue
        if c == '$':
            match = re.match(r"\$(\w+)", command[i:])
            if not match:
                result += c
            else:
                result += os.environ[match[1]] if match[1] in os.environ else ""
                return result + substitute_variables(command[i + len(match[1]) + 1:])
        else:
            result += c
    return result


def split_command_into_args(command):
    state = State.UNQUOTED
    args = []
    last_arg = ''
    for i, c in enumerate(command):
        state = eval_state(state, c)
        if state is State.UNQUOTED and re.match('\s', c):
            if last_arg != '':
                args += [last_arg]
            last_arg = ''
            continue
        last_arg += c
    if last_arg != '':
        args += [last_arg]
    return args


def remove_quotes(word):
    state = State.UNQUOTED
    result = ''
    for (i, c) in enumerate(word):
        if c in ['"', '\''] and state is State.UNQUOTED:
            state = eval_state(state, c)
            continue

        state = eval_state(state, c)
        if c in ['"', '\''] and state is State.UNQUOTED:
            continue
        result += c
    return result
