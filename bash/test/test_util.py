from unittest import TestCase, main
from src.utils import *


class TestRemoveQuotes(TestCase):
    def test_without_quotes(self):
        self.assertEqual("word", remove_quotes("word"))
        self.assertEqual("a", remove_quotes("a"))
        self.assertEqual("", remove_quotes(""))
        self.assertEqual("I am a word", remove_quotes("I am a word"))

    def test_double_quotes(self):
        self.assertEqual('i am almost a word', remove_quotes('"i am almost a word"'))
        self.assertEqual('i am a sentence', remove_quotes('"i am" a "sentence"'))
        self.assertEqual('i am in trouble', remove_quotes('i am in "trouble"'))
        self.assertEqual('i am almost a word', remove_quotes('i am"""""" almost a word'))

    def test_single_quotes(self):
        self.assertEqual('i am almost a word', remove_quotes("'i am almost a word'"))
        self.assertEqual('i am a sentence', remove_quotes("'i am' a 'sentence'"))
        self.assertEqual('i am in trouble', remove_quotes("i am in 'trouble'"))
        self.assertEqual('i am almost a word', remove_quotes("i am'''' almost a word"))

    def test_mixed(self):
        self.assertEqual('i\' am\' almost \'a\' word', remove_quotes('"i\' am\' "almost "\'a\' word"'))
        self.assertEqual('"i am" a "sentence"', remove_quotes('\'"\'i am\'"\' a \'"sentence"\''))
        self.assertEqual('i """am in trouble', remove_quotes('i \'""\'""\'"\'am in "trouble"'))
        self.assertEqual('i am almost a word', remove_quotes('i am""""""\'\'""""\'\' almost a word'))


class TestSplitCommandIntoArgs(TestCase):
    def test_one_command(self):
        self.assertListEqual(["ls"], split_command_into_args("ls"))
        self.assertListEqual(["dir"], split_command_into_args("dir"))
        self.assertListEqual(["echo"], split_command_into_args("echo"))
        self.assertListEqual(["pwd"], split_command_into_args("pwd"))

    def test_command_with_args(self):
        self.assertListEqual(["ls", "-l", "-a"], split_command_into_args("ls -l -a"))
        self.assertListEqual(["echo", "123"], split_command_into_args("echo 123"))

    def test_different_whitespaces(self):
        self.assertListEqual(["ls", "-l", "-a"], split_command_into_args("ls   -l   -a"))
        self.assertListEqual(["ls", "-l", "-a"], split_command_into_args("ls\t   -l\t   -a"))
        self.assertListEqual(["ls", "-l", "-a"], split_command_into_args("ls\t   -l\n\n   -a"))

    def test_quoted_args(self):
        self.assertListEqual(["ls", "-l", "'-a'"], split_command_into_args("ls -l   '-a'"))
        self.assertListEqual(["ls", "\"-l\"", "-a"], split_command_into_args("ls \"-l\" -a"))
        self.assertListEqual(["ls", "\"-l\"\"-a\""], split_command_into_args("ls \"-l\"\"-a\""))


class TestSubstitution(TestCase):
    def setUp(self):
        os.environ['a'] = '1'
        os.environ['b'] = '2'

    def test_no_variables(self):
        self.assertEqual("string", substitute_variables("string"))
        self.assertEqual("", substitute_variables(""))

    def test_dollar_sign_without_name(self):
        self.assertEqual("string$", substitute_variables("string$"))
        self.assertEqual("$", substitute_variables("$"))

    def test_existing_variables(self):
        self.assertEqual("12", substitute_variables("$a$b"))
        self.assertEqual("2", substitute_variables("$b"))
        self.assertEqual("1", substitute_variables("$a"))

    def test_two_dollars(self):
        self.assertEqual("$$", substitute_variables("$$"))

    def test_strong_quotes(self):
        self.assertEqual("'$a'", substitute_variables("'$a'"))
        self.assertEqual("'$abc'", substitute_variables("'$abc'"))

    def test_weak_quotes(self):
        self.assertEqual("\"2\"", substitute_variables("\"$b\""))
        self.assertEqual("\"1\"", substitute_variables("\"$a\""))

    def test_nonexistent_vars(self):
        self.assertEqual("", substitute_variables("$asd"))
        self.assertEqual("abc", substitute_variables("abc$abc"))
        self.assertEqual("a\"\"b\"\"c", substitute_variables("a\"$asd\"b\"$assd\"c"))


class TestSplitIntoCommands(TestCase):
    def test_single_command(self):
        self.assertListEqual(["echo 123"], split_into_commands("echo 123"))
        self.assertListEqual(["ls"], split_into_commands("ls"))

    def test_simple_pipeline(self):
        self.assertListEqual(["echo 123", "wc"], split_into_commands("echo 123 | wc"))
        self.assertListEqual(["echo 123", "wc"], split_into_commands("echo 123 |   wc"))
        self.assertListEqual(["echo 123", "wc"], split_into_commands("echo 123 |\t   wc"))

    def test_consecutive_pipes(self):
        self.assertListEqual(['', ''], split_into_commands("||"))

    def test_only_pipe(self):
        self.assertListEqual([''], split_into_commands("|"))

    def test_quoted_pipes(self):
        self.assertListEqual(['echo "123 |"', 'wc'], split_into_commands("echo \"123 |\" | wc"))
        self.assertListEqual(['echo \'123 |\'', 'wc'], split_into_commands("echo \'123 |\' | wc"))

    def test_broken_pipe(self):
        self.assertListEqual(['echo', '', 'echo'], split_into_commands("echo || echo"))
        self.assertListEqual(['echo', ''], split_into_commands("echo ||"))


class TestFindFirstUnquoted(TestCase):
    cipher = re.compile('[0-9]')
    alpha = re.compile('[a-zA-Z]')

    def test_first_position(self):
        self.assertEqual(0, find_first_unquoted("12345", self.cipher))
        self.assertEqual(0, find_first_unquoted("AcasdD", self.alpha))

    def test_not_present(self):
        self.assertEqual(len("abcdef"), find_first_unquoted("abcdef", self.cipher))
        self.assertEqual(len("12345"), find_first_unquoted("12345", self.alpha))

    def test_in_the_middle(self):
        self.assertEqual(3, find_first_unquoted("123c56", self.alpha))
        self.assertEqual(3, find_first_unquoted("123casd", self.alpha))


class TestFindUnquoted(TestCase):
    cipher = re.compile('[0-9]')
    alpha = re.compile('[a-zA-Z]')

    def test_single_sep(self):
        self.assertListEqual([7, 3], find_unquoted("123a234", self.alpha))
        self.assertListEqual([6, 1], find_unquoted("f8asdf", self.cipher))

    def test_several_seps(self):
        self.assertListEqual([9, 7, 4, 2], find_unquoted("12C3a23d4", self.alpha))
        self.assertListEqual([8, 6, 4, 1], find_unquoted("f8as3d5f", self.cipher))

    def test_sep_in_beginning(self):
        self.assertListEqual([9, 0], find_unquoted("1sdflkksd", self.cipher))
        self.assertListEqual([7, 0], find_unquoted("C192837", self.alpha))


class TestEvalState(TestCase):
    def test_unquoted_to_strong(self):
        self.assertEqual(State.STRONG_QUOTED, eval_state(State.UNQUOTED, '\''))

    def test_unquoted_to_weak(self):
        self.assertEqual(State.WEAK_QUOTED, eval_state(State.UNQUOTED, '\"'))

    def test_unquoted_to_unquouted(self):
        self.assertEqual(State.UNQUOTED, eval_state(State.UNQUOTED, 's'))

    def test_strong_to_unquoted(self):
        self.assertEqual(State.UNQUOTED, eval_state(State.STRONG_QUOTED, '\''))

    def test_strong_to_strong(self):
        self.assertEqual(State.STRONG_QUOTED, eval_state(State.STRONG_QUOTED, 's'))

    def test_weak_to_unquoted(self):
        self.assertEqual(State.UNQUOTED, eval_state(State.WEAK_QUOTED, '\"'))

    def test_weak_to_weak(self):
        self.assertEqual(State.WEAK_QUOTED, eval_state(State.WEAK_QUOTED, 's'))


if __name__ == '__main__':
    main()
