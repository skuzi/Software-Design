from unittest import TestCase, main
from src.executors import *
from pathlib import Path


class TestCat(TestCase):
    resources = Path(__file__).parent.absolute() / "resources"

    def test_without_args(self):
        self.assertEqual("abc", CatExecutor.execute([], "abc"))
        self.assertEqual("", CatExecutor.execute([], ""))

    def test_one_line(self):
        self.assertEqual('asd asd asd', CatExecutor.execute([self.resources / 'one_liner']))

    def test_several_lines(self):
        self.assertEqual("abc\n"
                         "abc def\n"
                         "asd\n", CatExecutor.execute([self.resources / 'multiple_liner']))

    def test_empty(self):
        self.assertEqual('', CatExecutor.execute([self.resources / 'empty']))

    def test_several_files(self):
        self.assertEqual("asd asd asdabc\n"
                         "abc def\n"
                         "asd\n", CatExecutor.execute([self.resources / 'one_liner',
                                                       self.resources / 'multiple_liner']))


class TestEcho(TestCase):
    def test_without_args(self):
        self.assertEqual("", EchoExecutor.execute([]))

    def test_with_one_arg(self):
        self.assertEqual("123", EchoExecutor.execute(["123"]))

    def test_with_several_args(self):
        self.assertEqual("123 123 123  123", EchoExecutor.execute(["123", "123", "123  123"]))


class TestWc(TestCase):
    resources = Path(__file__).parent.absolute() / "resources"

    def test_without_args(self):
        self.assertEqual("1 1 3", WcExecutor.execute([], "abc"))
        with self.assertRaises(ExecutionException):
            WcExecutor.execute([], "")

    def test_one_line(self):
        self.assertEqual('1 3 11\ntotal 1 3 11',
                         WcExecutor.execute([self.resources / 'one_liner']))

    def test_several_lines(self):
        self.assertEqual("3 4 16\ntotal 3 4 16",
                         WcExecutor.execute([self.resources / 'multiple_liner']))

    def test_empty(self):
        self.assertEqual('0 0 0\ntotal 0 0 0',
                         WcExecutor.execute([self.resources / 'empty']))

    def test_several_files(self):
        self.assertEqual("1 3 11\n3 4 16\ntotal 4 7 27",
                         WcExecutor.execute([self.resources / 'one_liner', self.resources / 'multiple_liner']))


class TestGrep(TestCase):
    resources = Path(__file__).parent.absolute() / "resources"

    def test_without_file(self):
        self.assertEqual("abc", GrepExecutor.execute(['abc'], 'abc'))
        self.assertEqual("abc\nabc", GrepExecutor.execute(['abc'], 'abc\nabc'))
        with self.assertRaises(ExecutionException):
            WcExecutor.execute(['abc'], "")

    def test_simple_file(self):
        self.assertEqual("asd asd asd", GrepExecutor.execute(['as', str(self.resources / 'one_liner')]))
        self.assertEqual("", GrepExecutor.execute(['Asd', str(self.resources / 'one_liner')]))
        self.assertEqual("", GrepExecutor.execute(['asdf', str(self.resources / 'one_liner')]))

    def test_case_sens(self):
        self.assertEqual("asd asd asd", GrepExecutor.execute(['-i', 'ASd', str(self.resources / 'one_liner')]))
        self.assertEqual("asd asd asd", GrepExecutor.execute(['-i', 'aSd', str(self.resources / 'one_liner')]))

    def test_full_word_match(self):
        self.assertEqual("asd asd asd", GrepExecutor.execute(['-w', 'asd', str(self.resources / 'one_liner')]))
        self.assertEqual("", GrepExecutor.execute(['-w', 'as', str(self.resources / 'one_liner')]))
        self.assertEqual("asd asd asd", GrepExecutor.execute(['-w', 'asd asd', str(self.resources / 'one_liner')]))

    def test_lines_after(self):
        self.assertEqual("asd asd asd", GrepExecutor.execute(['-A', '1', 'asd', str(self.resources / 'one_liner')]))
        self.assertEqual("", GrepExecutor.execute(['-A', '3', 'asds', str(self.resources / 'multiple_liner')]))
        self.assertEqual("abc\nabc def",
                         GrepExecutor.execute(['-A', '1', 'abc$', str(self.resources / 'multiple_liner')]))
        self.assertEqual("abc\n"
                         "abc def\n"
                         "asd",
                         GrepExecutor.execute(['-A', '1', 'abc', str(self.resources / 'multiple_liner')]))

    def test_multiple_flags(self):
        self.assertEqual("asd asd asd", GrepExecutor.execute(['-wi', 'aSd', str(self.resources / 'one_liner')]))
        self.assertEqual("asd asd asd", GrepExecutor.execute(['-w', '-i',  'aSd', str(self.resources / 'one_liner')]))
        self.assertEqual("asd asd asd", GrepExecutor.execute(['-wi', 'aSd asD', str(self.resources / 'one_liner')]))
        self.assertEqual("abc def\nasd",
                         GrepExecutor.execute(['-i', '-A', '1', 'aBc DeF', str(self.resources / 'multiple_liner')]))

    def test_regex(self):
        self.assertEqual("asd asd asd",
                         GrepExecutor.execute([r'([a-z]{3} ){2}[a-z]{3}', str(self.resources / 'one_liner')]))


class TestExternal(TestCase):
    def test_python(self):
        self.assertEqual('1', ExternalExecutor.execute(['python3', '-c', 'print(1)']))

    def test_bad_command(self):
        with self.assertRaises(ExecutionException):
            # I hope nobody has this in their PATH
            ExternalExecutor.execute(["kajlshdlhdflskdfasaskfhsdlskf", "123"])
        with self.assertRaises(ExecutionException):
            ExternalExecutor.execute(['python3', '-c', 'print 1'])


if __name__ == '__main__':
    main()
