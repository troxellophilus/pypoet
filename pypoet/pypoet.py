"""PyPoet: Python to write Python.

Provides classes to generate Python files. Output formatted with YAPF.

Examples:
    Hello World
    >>> print_hello = pypoet.Statement("print('Hello world!')")
    >>> hellopy = pypoet.Pythonfile()
    >>> hellopy.append(print_hello)
    >>> hellopy.write('hello.py')

Drew Troxell
"""

import os

import yapf


class CodeBlock(object):
    """A block of code.

    Don't use this class directly, use the sub-classes.
    """

    def __init__(self):
        """Initialize a CodeBlock."""
        self.docstring = None
        self.return_stmnt = None
        self.statements = []

    def _entry(self):
        """The entry line to this code block.

        Override this method in sub-classes.
        """
        raise NotImplementedError()

    def add_docstring(self, docstring):
        """Add a docstring to the code block.

        Args:
            docstring (DocString): The DocString to add to the block.

        Returns:
            CodeBlock: This codeblock.
        """
        if not isinstance(docstring, DocString):
            raise TypeError("'docstring' must be of type DocString")
        self.docstring = docstring
        return self

    def add_statement(self, stmnt):
        """Add a statement to the code block.

        Args:
            stmnt (Statement): The Statement to add to the block.

        Returns:
            CodeBlock: This codeblock.
        """
        if not isinstance(stmnt, Statement):
            raise TypeError("'stmnt' must be of type Statement")
        self.statements.append(stmnt)
        return self

    def add_codeblock(self, codeblock):
        """Add a codeblock to the code block.

        Args:
            codeblock (CodeBlock): The CodeBlock to add to the block.

        Returns:
            CodeBlock: This codeblock.
        """
        if not isinstance(codeblock, CodeBlock):
            raise TypeError("'codeblock' must be of type CodeBlock")
        self.statements.extend(codeblock.to_lines())
        return self

    def to_lines(self):
        """Convert this CodeBlock to an array of code lines.

        Returns:
            list(str): The lines of code making up this CodeBlock.
        """
        lines = [self._entry(),]
        if self.docstring:
            lines.extend('    ' + l for l in self.docstring.to_lines())
        for stmnt in self.statements:
            lines.append('    ' + stmnt)
        if self.return_stmnt:
            lines.append('    ' + self.return_stmnt)
        return lines


class DocString(object):
    r"""Documentation string.

    Example:
        >>> ds = pypoet.DocString('docstring', 'description', 'return_value', 'arg1')
        >>> print('\n'.join(ds.to_lines()))
    """

    def __init__(self, name, description=None, returns=None, *args):
        """Initialize a DocString.

        Args:
            name (str): The opening line of the docstring.
            description (str, optional): The description line of the docstring.
            returns (str, optional): The return doc.
            *args (list(str), optional): Any arguments documented in the docstring.
        """
        self.name = name
        self.description = description
        self.returns = returns
        self.args = args

    def to_lines(self):
        """Convert this DocString to a list of lines of code.

        Returns:
            list(str): The DocString as a list of code lines.
        """
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
    """A Python statement."""

    def __init__(self, stmnt):
        """Initialize a Statement.

        Args:
            stmnt (str): The Python statement as a string.
        """
        super().__init__()
        self.statement = stmnt

    def _entry(self):
        """The entry line to a statement is the statement itself.

        Returns:
            str: The statement.
        """
        return self.statement


class If(CodeBlock):
    """CodeBlock representing an if conditional."""

    def __init__(self, expression):
        """Initialize an If block.

        Args:
            expression (str): The expression to evaluate for this If.
        """
        super().__init__()
        self.expression = expression

    def _entry(self):
        """Enter an If conditional.

        Returns:
            str: Of form, 'if <expression>:'
        """
        return "if %s:" % self.expression


class ElIf(CodeBlock):
    """CodeBlock representing an elif conditional."""

    def __init__(self, expression):
        """Initialize an ElIf block.

        Args:
            expression (str): The expression to evaluate for this ElIf.
        """
        super().__init__()
        self.expression = expression

    def _entry(self):
        """Enter an ElIf conditional.

        Returns:
            str: Of form, 'elif <expression>:'
        """
        return "elif %s:" % self.expression


class Else(CodeBlock):
    """CodeBlock representing an else conditional."""

    def __init__(self):
        """Initialize an Else block."""
        super().__init__()

    def _entry(self):
        """Enter an Else conditional.

        Returns:
            str: Of form, 'else:'
        """
        return "else:"


class ForLoop(CodeBlock):
    """CodeBlock representing a for loop."""

    def __init__(self, index, iterable):
        """Initialize a ForLoop block.

        Args:
            index (str): The name of the index variable(s).
            iterable (str): The name of the iterable variable.
        """
        super().__init__()
        self.index = index
        self.iterable = iterable

    def _entry(self):
        """Enter a for loop.

        Returns:
            str: Of form, 'for <index> in <iterable>:'
        """
        return "for %s in %s:" % (self.index, self.iterable)


class WhileLoop(CodeBlock):
    """CodeBlock representing a while loop."""

    def __init__(self, expression):
        """Initialize a WhileLoop block.

        Args:
            expression (str): The expression to evaluate in the while loop.
        """
        super().__init__()
        self.expression = expression

    def _entry(self):
        """Enter a while loop.

        Returns:
            str: Of form, 'while <expression>:'
        """
        return "while %s:" % self.expression


class Define(CodeBlock):
    """CodeBlock representing a define block."""

    def __init__(self, name, *params):
        """Initialize a Define block.

        Args:
            name (str): Name of the function/method being defined.
            params (list(str)): Any parameters to the defined func/method.
        """
        super().__init__()
        self.name = name
        self.params = params

    def _entry(self):
        """Enter a define block.

        Returns:
            str: Of form, 'def <name>(<param1>, <param2>, ...):'
        """
        return "def %s(%s):" % (self.name, ', '.join(self.params))

    def returns(self, what):
        """Set a return value for the defined func/method.

        Args:
            what (str): What the def returns.

        Returns:
            CodeBlock: this codeblock.
        """
        self.return_stmnt = "return %s" % what
        return self


class Class(CodeBlock):
    """CodeBlock representing a class."""

    def __init__(self, name, *extends):
        """Initialize a Class block.

        Args:
            name (str): Name of the class.
            extends (list(str)): Any classes this class inherits from.
        """
        super().__init__()
        self.name = name
        self.extends = extends if extends else ["object",]

    def _entry(self):
        """Enter a class block.

        Returns:
            str: Of form, 'class <name>(<extend1>, <extend2>, ...):'
        """
        return "class %s(%s):" % (self.name, ', '.join(self.extends))


class PythonFile(object):
    """Object representing a Python module."""

    def __init__(self):
        """Initialize a PythonFile object."""
        self.docstring = None
        self.codeblocks = []

    def add_docstring(self, docstring):
        """Add a docstring to this module.

        Args:
            docstring (DocString): The DocString to add.

        Returns:
            PythonFile: This PythonFile.
        """
        if not isinstance(docstring, DocString):
            raise TypeError("'docstring' must be of type DocString")
        self.docstring = docstring
        return self

    def append(self, codeblock):
        """Append a CodeBlock to this module.

        Args:
            codeblock (CodeBlock): The CodeBlock to append.

        Returns:
            PythonFile: This PythonFile.
        """
        if not isinstance(codeblock, CodeBlock):
            raise TypeError("'codeblock' must be of type CodeBlock")
        self.codeblocks.append(codeblock)
        return self

    def write(self, filename):
        """Write this PythonFile out to a file.

        Args:
            filename (str): Path of the file to write.
        """
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
