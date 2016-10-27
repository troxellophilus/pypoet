import os

import yapf


class CodeBlock(object):

    def __init__(self):
        self.docstring = None
        self.return_stmnt = None
        self.statements = []

    def _entry(self):
        """Override"""
        raise NotImplementedError()

    def add_docstring(self, docstring):
        if not isinstance(docstring, DocString):
            raise TypeError("'docstring' must be of type DocString")
        self.docstring = docstring
        return self

    def add_statement(self, stmnt):
        if not isinstance(stmnt, Statement):
            raise TypeError("'stmnt' must be of type Statement")
        self.statements.append(stmnt)
        return self

    def add_codeblock(self, codeblock):
        if not isinstance(codeblock, CodeBlock):
            raise TypeError("'codeblock' must be of type CodeBlock")
        self.statements.extend(codeblock.to_lines())
        return self

    def to_lines(self):
        lines = [self._entry(),]
        if self.docstring:
            lines.extend('    ' + l for l in self.docstring.to_lines())
        for stmnt in self.statements:
            lines.append('    ' + stmnt)
        if self.return_stmnt:
            lines.append('    ' + self.return_stmnt)
        return lines


class DocString(object):

    def __init__(self, name, description=None, returns=None, *args):
        self.name = name
        self.description = description
        self.returns = returns
        self.args = args

    def to_lines(self):
        lines = ['"""%s\n' % self.name,]
        if self.description:
            lines.append(self.description + '\n')
        if self.args:
            lines.append('Args:')
            for arg in self.args:
                lines.append('    %s ():' % arg)
            lines.append(lines.pop() + '\n')
        if self.returns:
            lines.append('Returns:')
            lines.append('    %s:' % self.returns)
        lines.append('"""')
        return lines


class Statement(CodeBlock):

    def __init__(self, stmnt):
        super().__init__()
        self.statement = stmnt

    def _entry(self):
        return self.statement


class If(CodeBlock):

    def __init__(self, expression):
        super().__init__()
        self.expression = expression

    def _entry(self):
        return "if %s:" % self.expression


class ElIf(CodeBlock):

    def __init__(self, expression):
        super().__init__()
        self.expression = expression

    def _entry(self):
        return "elif %s:" % self.expression


class Else(CodeBlock):

    def __init__(self):
        super().__init__()

    def _entry(self):
        return "else:"


class ForLoop(CodeBlock):

    def __init__(self, index, iterable):
        super().__init__()
        self.index = index
        self.iterable = iterable

    def _entry(self):
        return "for %s in %s:" % (self.index, self.iterable)


class WhileLoop(CodeBlock):

    def __init__(self, expression):
        super().__init__()
        self.expression = expression

    def _entry(self):
        return "while %s:" % self.expression


class Define(CodeBlock):

    def __init__(self, name, *params):
        super().__init__()
        self.name = name
        self.params = params

    def _entry(self):
        return "def %s(%s):" % (self.name, ', '.join(self.params))

    def returns(self, what):
        self.return_stmnt = "return %s" % what
        return self


class Class(CodeBlock):

    def __init__(self, name, *extends):
        super().__init__()
        self.name = name
        self.extends = extends if extends else ["object",]

    def _entry(self):
        return "class %s(%s):" % (self.name, ', '.join(self.extends))


class PythonFile(object):

    def __init__(self):
        self.docstring = None
        self.codeblocks = []

    def add_docstring(self, docstring):
        if not isinstance(docstring, DocString):
            raise TypeError("'docstring' must be of type DocString")
        self.docstring = docstring
        return self

    def append(self, codeblock):
        if not isinstance(codeblock, CodeBlock):
            raise TypeError("'codeblock' must be of type CodeBlock")
        self.codeblocks.append(codeblock)
        return self

    def write(self, filename):
        with open(filename, 'w') as py_fp:
            if self.docstring:
                for line in self.docstring.to_lines():
                    py_fp.write(line)
            else:
                py_fp.write('"""%s."""' % filename)
            for codeblock in self.codeblocks:
                py_fp.write('\n\n' + '\n'.join(codeblock.to_lines()))
            py_fp.write('\n')
        yapf.yapf_api.FormatFile(filename, in_place=True)


def pypi(project_name):
    os.mkdir(project_name)
    os.mkdir(os.path.join(project_name, project_name))
    setuppy = PythonFile()
    setuppy.append(Statement('from setuptools import setup'))
    setuppy.append(Statement('setup(name=%s)' % project_name))
    setuppy.write(os.path.join(project_name, 'setup.py'))
    with open(os.path.join(project_name, 'README.md'), 'w') as readme:
        readme.write('# %s\n' % project_name)
        readme.write('### Short description.\n\n'
                     '## Install\n\n'
                     '```bash\n$ python setup.py install\n```\n\n'
                     '## Usage\n\n'
                     '```python\n>>> \n```\n\n'
                     '## More Info\n\n'
                     '<a href="">Link to more info.</a>')
    with open(os.path.join(project_name, 'MANIFEST.in'), 'w') as manifest:
        manifest.write('include README.md')
    with open(
            os.path.join(project_name, project_name,
                         '__init__.py'), 'w') as initpy:
        initpy.write('__all__ = []\n')
    with open(
            os.path.join(project_name, project_name,
                         project_name + '.py'), 'w') as mainpy:
        mainpy.write(
            '"""%s."""\n\ndef main():\n    return\n\nif __name__ == "__main__":\n    main()\n'
            % project_name)
