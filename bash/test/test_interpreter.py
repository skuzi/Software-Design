from unittest import TestCase, main
from src.interpreter import *


class TestExit(TestCase):
    def test_is_exit(self):
        self.assertTrue(is_exit(["exit"]))

    def test_is_not_exit(self):
        self.assertFalse(is_exit(["asdlj"]))

    def test_exit_longer_than_one(self):
        self.assertFalse(is_exit(["exit", "exit"]))


class TestAssignment(TestCase):
    def test_is_assignment(self):
        self.assertTrue(is_assignment(["a=5"]))

    def test_is_not_assignment(self):
        self.assertFalse(is_assignment(["asd"]))

    def test_variable_not_correct(self):
        self.assertFalse(is_assignment(["5=3"]))

    def test_variable_has_underscore(self):
        self.assertTrue(is_assignment(["_5=3"]))

    def test_variable_underscore(self):
        self.assertTrue(is_assignment(["_=3"]))


class TestExecutePipeline(TestCase):
    def test_simple_command(self):
        self.assertEqual("123", execute_pipeline("echo 123"))

    def test_simple_pipe(self):
        self.assertEqual("1 1 3", execute_pipeline("echo 123 | wc"))

    def test_simple_pipe_more(self):
        self.assertEqual("1 1 3", execute_pipeline("echo 123 | cat | wc"))

    def test_exit(self):
        self.assertEqual(None, execute_pipeline("exit"))

    def test_bad_pipeline(self):
        self.assertEqual("error while parsing", execute_pipeline("echo 123 |||"))


if __name__ == '__main__':
    main()