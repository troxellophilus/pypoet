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
        cb.add_docstring(doc)
        self.assertEqual(cb.docstring, doc)
        try:
            cb.add_docstring('not a docstring')
            self.fail('expected a TypeError')
        except TypeError:
            pass

    def test_add_statement(self):
        stmnt = pypoet.Statement('print("cats")')
        cb = pypoet.CodeBlock()
        cb.add_statement(stmnt)
        self.assertEqual(len(cb.statements), 1)
        self.assertEqual(cb.statements[0], stmnt)
        try:
            cb.add_statement('not a statement')
            self.fail('expected a TypeError')
        except TypeError:
            pass

    def test_add_codeblock(self):
        cbother = pypoet.CodeBlock()
        cb = pypoet.CodeBlock()
        try:
            cb.add_codeblock(cbother)
            self.fail('expected NotImplementedError')
        except NotImplementedError:
            pass

    def test_to_lines(self):
        cb = pypoet.CodeBlock()
        try:
            cb.to_lines()
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
            '"""docstring\n',
            'this is a docstring\n',
            'Args:',
            '    arg1 ():',
            '    arg2 ():\n',
            'Returns:',
            '    str:',
            '"""'
        ]
        self.assertEqual(ds.to_lines(), exp_lines)


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

    def test_add_docstring(self):
        docstr = pypoet.DocString(name='doc', description='sample')
        pyfile = pypoet.PythonFile()
        pyfile.add_docstring(docstr)
        self.assertEqual(pyfile.docstring, docstr)
        try:
            pyfile.add_docstring('not a docstring')
            self.fail('expected a TypeError')
        except TypeError:
            pass

    def test_append(self):
        define = pypoet.Define('count_cats').returns('5')
        pyfile = pypoet.PythonFile()
        pyfile.append(define)
        self.assertEqual(pyfile.codeblocks[0], define)
        try:
            pyfile.append('not a codeblock')
            self.fail('expected a TypeError')
        except TypeError:
            pass

    def test_write(self):
        pyfile = pypoet.PythonFile()
        docstr = pypoet.DocString(name='doc', description='sample')
        pyfile.add_docstring(docstr)
        stmnt = pypoet.Statement('bar = 5')
        pyfile.append(stmnt)
        define = pypoet.Define('foo').returns('bar')
        pyfile.append(define)
        pyfile.write('tmp.py')
        with open('tmp.py', 'r') as fp:
            lines = list(fp)
            self.assertEqual(''.join(lines[:4]), '"""doc\nsample\n"""\n\n')
            self.assertEqual(''.join(lines[4:7]), 'bar = 5\n\n\n')
            self.assertEqual(''.join(lines[7:]), 'def foo():\n    return bar\n')
        os.remove('tmp.py')


if __name__ == '__main__':
    unittest.main()
