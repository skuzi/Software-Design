import os
import re
from enum import Enum


class State(Enum):
    """
    Enum for storing current state of the string
    UNQUOTED means that current position is neither in strong quotes nor in weak
    STRONG_QUOTED means that there was opening ' earlier in the string but it was not yet closed
    WEAK_QUOTED means that there was opening " earlier in the string but it was not yet closed
    """
    UNQUOTED = 0
    STRONG_QUOTED = 1
    WEAK_QUOTED = 2


def eval_state(state, c):
    """
    Evaluates next state after appending character to a string

    :param state: state before appending character
    :param c: character appended to a string
    :return: next state after reevaluation
    """
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
    """
    Finds first unquoted occurrence of pattern in the string
    :param line: string to find occurrences in
    :param pattern: pattern to search for
    :return: first unquoted occurrence of pattern or len(line) if no occurrences were found
    """
    state = State.UNQUOTED
    for i, c in enumerate(line):
        state = eval_state(state, c)
        if state is State.UNQUOTED and pattern.match(c):
            return i
    return len(line)


def find_unquoted(line, pattern, begin=0):
    """
    Finds all unquoted occurrences of pattern in the string
    :param line: string to find occurrences in
    :param pattern: pattern to search for
    :return: all unquoted occurrences of pattern
    or [len(line)] if no occurrences were found
    or [] if line is empty or None
    """
    if not line:
        return []
    ind = find_first_unquoted(line, pattern)
    return find_unquoted(line[ind + 1:], pattern, begin + ind + 1) + [begin + ind]


def split_with_quotes(command, pattern):
    """
    Splits line by pattern with respect to quotes (i.e. only unquoted occurrences of pattern matter)
    :param command: string to find occurrences in
    :param pattern: pattern to search for
    :return: result of split, list of string, each string does not contain any unquoted occurrence of pattern
    """
    split_indices = find_unquoted(command, pattern) + [-1]
    return [command[split_indices[i + 1] + 1:split_indices[i]].strip() for i in range(len(split_indices) - 2, -1, -1)]


def split_into_commands(command):
    """
    Splits pipeline into single commands. More accurately, splits string by unquoted occurrences of '|'
    :param command: string to split
    :return: split string
    """
    return split_with_quotes(command, re.compile(r'\|'))


def substitute_variables(command):
    """
    Substitutes all strings like '$something' not in single quotes according to os.environ
    (i.e. if such 'something' occurs in os.environ, substitutes its value in place of '$something',
     or else substitutes it with ""

     :param command: line to substitute variables in
    """
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
    """
    Splits command into arguments by whitespaces which are not contained between some quotes
    """
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
    """
    Removes all quotes from a string, does not remove quotes which are contained between other quotes
    """
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
