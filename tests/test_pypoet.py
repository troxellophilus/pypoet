import unittest

import os

import pypoet


class TestCodeBlock(unittest.TestCase):

    def test_entry(self):
        cb = pypoet.CodeBlock()
        try:
            cb._entry()
            self.fail('expected a NotImplementedError')
        except NotImplementedError:
            pass

    def test_add_docstring(self):
        doc = pypoet.DocString(name='docstring')
        cb = pypoet.CodeBlock()
        cb.docstring = doc
        self.assertEqual(cb.docstring, doc)
        try:
            cb.docstring = 'not a docstring'
            self.fail('expected a TypeError')
        except TypeError:
            pass

    def test_append(self):
        cbother = pypoet.CodeBlock()
        cb = pypoet.CodeBlock()
        try:
            cb.append(cbother)
            self.fail('expected NotImplementedError')
        except NotImplementedError:
            pass

    def test_to_lines(self):
        cb = pypoet.CodeBlock()
        try:
            cb._to_lines()
            self.fail('expected NotImplementedError')
        except NotImplementedError:
            pass


class TestDocString(unittest.TestCase):

    def test_to_lines(self):
        ds = pypoet.DocString(
            'docstring',
            'this is a docstring',
            'str',
            'arg1',
            'arg2'
        )
        exp_lines = [
            '"""docstring',
            '',
            'this is a docstring',
            '',
            'Args:',
            '    arg1 ():',
            '    arg2 ():',
            '',
            'Returns:',
            '    str:',
            '"""',
            ''
        ]
        self.assertEqual(list(ds), exp_lines)


class TestStatement(unittest.TestCase):

    def test_entry(self):
        stmnt = pypoet.Statement('print("CATS")')
        self.assertEqual(stmnt._entry(), 'print("CATS")')


class TestIf(unittest.TestCase):

    def test_entry(self):
        if_ = pypoet.If('x == 5')
        self.assertEqual(if_._entry(), 'if x == 5:')


class TestElIf(unittest.TestCase):

    def test_entry(self):
        elif_ = pypoet.ElIf('x == 6')
        self.assertEqual(elif_._entry(), 'elif x == 6:')


class TestElse(unittest.TestCase):

    def test_entry(self):
        else_ = pypoet.Else()
        self.assertEqual(else_._entry(), 'else:')


class TestForLoop(unittest.TestCase):

    def test_entry(self):
        forloop = pypoet.ForLoop('cat', 'cats')
        self.assertEqual(forloop._entry(), 'for cat in cats:')


class TestWhileLoop(unittest.TestCase):

    def test_entry(self):
        whileloop = pypoet.WhileLoop('len(cats) > 100')
        self.assertEqual(whileloop._entry(), 'while len(cats) > 100:')


class TestDefine(unittest.TestCase):

    def test_entry(self):
        define = pypoet.Define('add_cat', 'cat_name', 'cat_length', 'alive=True')
        self.assertEqual(define._entry(), 'def add_cat(cat_name, cat_length, alive=True):')

    def test_returns(self):
        define = pypoet.Define('cat_face').returns("':3'")
        self.assertEqual(define.return_stmnt, "return ':3'")


class TestClass(unittest.TestCase):

    def test_entry(self):
        class_ = pypoet.Class('Cat', 'DomesticMammal')
        self.assertEqual(class_._entry(), 'class Cat(DomesticMammal):')


class TestPythonFile(unittest.TestCase):

    def test_entry(self):
        pyfile = pypoet.Module('test')
        self.assertEqual(pyfile._entry(), '')

    def test_default_docstring(self):
        pyfile = pypoet.Module('test')
        self.assertEqual(pyfile.docstring, pypoet.DocString('test'))

    def test_write(self):
        pyfile = pypoet.Module('test')
        docstr = pypoet.DocString(name='doc', description='sample')
        pyfile.docstring = docstr
        stmnt = pypoet.Statement('bar = 5')
        pyfile.append(stmnt)
        define = pypoet.Define('foo').returns('bar')
        pyfile.append(define)
        pyfile.write()
        with open('test.py', 'r') as fp:
            lines = list(fp)
            self.assertEqual(''.join(lines[:5]), '"""doc\n\nsample\n"""\n\n')
            self.assertEqual(''.join(lines[5:8]), 'bar = 5\n\n\n')
            self.assertEqual(''.join(lines[8:]), 'def foo():\n    return bar\n')
        os.remove('test.py')


if __name__ == '__main__':
    unittest.main()
