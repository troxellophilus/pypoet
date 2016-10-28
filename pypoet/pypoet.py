r"""PyPoet: Python to write Python.

Provides classes to generate Python files. Output formatted with YAPF.

Examples:
    Hello World
    >>> import pypoet
    >>> s = pypoet.Statement('print("HELLO WORLD.")')
    >>> list(s)
    ['print("HELLO WORLD.")', '']
    >>> str(s)
    'print("HELLO WORLD.")\n'
    >>> s
    <pypoet.pypoet.Statement object at 0x0000000000715FD0>
    >>> 'HELLO' in s
    True

Drew Troxell
"""

import yapf


class FormattedBlock(object):
    """A block of Python formatted text.

    Provides magic methods and interface for CodeBlock and DocString.
    """

    def __str__(self):
        """String representation of a codeblock is the formatted code.

        Returns:
            str: The formatted code as a string.
        """
        code = '\n'.join(self._to_lines())
        return yapf.yapf_api.FormatCode(code)[0]

    def __iter__(self):
        """Convert this CodeBlock to an iterable of code lines.

        Returns:
            list(str): List of formatted lines of code.
        """
        return iter(str(self).split('\n'))

    def __len__(self):
        """# of lines in a CodeBlock.

        Returns:
            int: The number of lines in the CodeBlock after formatting.
        """
        return len(str(self).split('\n'))

    def __contains__(self, item):
        """Test membership of a string in a CodeBlock.

        Returns:
            bool: True if item is present in any line of the formatted CodeBlock.
        """
        return any(item in l for l in list(self))

    def __eq__(self, other):
        """Test equality of two CodeBlocks.

        Returns:
            bool: True if equal.
        """
        return str(self) == str(other)

    def _to_lines(self):
        raise NotImplementedError()


class CodeBlock(FormattedBlock):
    """A block of code.

    Don't use this class directly, use the sub-classes.
    """

    def __init__(self):
        """Initialize a CodeBlock."""
        self._docstring = None
        self.return_stmnt = None
        self.statements = []

    def _entry(self):
        """The entry line to this code block.

        Override this method in sub-classes.
        """
        raise NotImplementedError()

    @property
    def docstring(self):
        """Get this Module's DocString."""
        return self._docstring

    @docstring.setter
    def docstring(self, docstring):
        """Set the docstring for this module.

        Args:
            docstring (DocString): The DocString to add.

        Returns:
            PythonFile: This PythonFile.
        """
        if not isinstance(docstring, DocString):
            raise TypeError("'docstring' must be of type DocString")
        self._docstring = docstring

    def append(self, codeblock):
        """Append a Statement or CodeBlock to this CodeBlock.

        Args:
            codeblock (CodeBlock): The item to append to this CodeBlock.

        Returns:
            CodeBlock: This CodeBlock.
        """
        self.statements.extend(list(codeblock))
        return self

    def _to_lines(self):
        """Convert this CodeBlock to an array of code lines.

        Returns:
            list(str): The lines of code making up this CodeBlock.
        """
        lines = [self._entry(),]
        if self.docstring:
            lines.extend('    ' + l for l in list(self._docstring))
        for stmnt in self.statements:
            lines.append('    ' + stmnt)
        if self.return_stmnt:
            lines.append('    ' + self.return_stmnt)
        return lines


class DocString(FormattedBlock):
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
        super().__init__()
        self.name = name
        self.description = description
        self.returns = returns
        self.args = args

    def _to_lines(self):
        """Convert this DocString to a list of lines of code.

        Returns:
            list(str): The DocString as a list of code lines.
        """
        lines = ['"""%s' % self.name,]
        if self.description:
            lines.append('\n' + self.description)
        if self.args:
            lines.append('\nArgs:')
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


class Module(CodeBlock):
    """Object representing a Python module."""

    def __init__(self, name, docstring=None):
        """Initialize a PythonFile object.

        Args:
            name (str): Name of this module.
            docstring (DocString, optional): A docstring for this module.
                If None, a default docstring will be generated.
        """
        super().__init__()
        self.name = name
        if docstring:
            self.docstring = docstring
        else:
            self.docstring = DocString(name)

    def _entry(self):
        return ''

    def _to_lines(self):
        """Convert this CodeBlock to an array of code lines.

        Returns:
            list(str): The lines of code making up this CodeBlock.
        """
        lines = [self._entry(),]
        if self.docstring:
            lines.extend(l for l in list(self._docstring))
        for stmnt in self.statements:
            lines.append(stmnt)
        if self.return_stmnt:
            lines.append(self.return_stmnt)
        return lines

    def write(self):
        """Write this Module out to a file."""
        with open(self.name + '.py', 'w') as py_fp:
            py_fp.write(str(self))
        yapf.yapf_api.FormatFile(self.name + '.py', in_place=True)
