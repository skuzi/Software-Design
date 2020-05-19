from unittest import TestCase, main
from src.executors import *


class TestCat(TestCase):
    resources = "resources/"

    def test_without_args(self):
        self.assertEqual("abc", CatExecutor.execute([], "abc"))
        self.assertEqual("", CatExecutor.execute([], ""))

    def test_one_line(self):
        self.assertEqual('asd asd asd', CatExecutor.execute([self.resources + 'one_liner']))

    def test_several_lines(self):
        self.assertEqual("abc\n"
                         "abc def\n"
                         "asd\n", CatExecutor.execute([self.resources + 'multiple_liner']))

    def test_empty(self):
        self.assertEqual('', CatExecutor.execute([self.resources + 'empty']))

    def test_several_files(self):
        self.assertEqual("asd asd asdabc\n"
                         "abc def\n"
                         "asd\n", CatExecutor.execute([self.resources + 'one_liner',
                                                       self.resources + 'multiple_liner']))


class TestEcho(TestCase):
    def test_without_args(self):
        self.assertEqual("", EchoExecutor.execute([]))

    def test_with_one_arg(self):
        self.assertEqual("123", EchoExecutor.execute(["123"]))

    def test_with_several_args(self):
        self.assertEqual("123 123 123  123", EchoExecutor.execute(["123", "123", "123  123"]))


class TestWc(TestCase):
    resources = "resources/"

    def test_without_args(self):
        self.assertEqual("1 1 3", WcExecutor.execute([], "abc"))
        with self.assertRaises(ExecutionException):
            WcExecutor.execute([], "")

    def test_one_line(self):
        self.assertEqual('1 3 11 resources/one_liner\ntotal 1 3 11',
                         WcExecutor.execute([self.resources + 'one_liner']))

    def test_several_lines(self):
        self.assertEqual("3 4 16 resources/multiple_liner\ntotal 3 4 16",
                         WcExecutor.execute([self.resources + 'multiple_liner']))

    def test_empty(self):
        self.assertEqual('0 0 0 resources/empty\ntotal 0 0 0',
                         WcExecutor.execute([self.resources + 'empty']))

    def test_several_files(self):
        self.assertEqual("1 3 11 resources/one_liner\n3 4 16 resources/multiple_liner\ntotal 4 7 27",
                         WcExecutor.execute([self.resources + 'one_liner', self.resources + 'multiple_liner']))


class TestExternal(TestCase):
    def test_python(self):
        self.assertEqual('1', ExternalExecutor.execute('python3 -c "print(1)"'))

    def test_bad_command(self):
        # I hope nobody has this in their PATH
        with self.assertRaises(ExecutionException):
            ExternalExecutor.execute("kajlshdlhdflskdfasaskfhsdlskf 123")
        with self.assertRaises(ExecutionException):
            ExternalExecutor.execute('python3 -c "print 1"')


if __name__ == '__main__':
    main()