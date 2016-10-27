# PyPoet
**Write Python in Python**

## Install

```bash
$ python setup.py install
```

## Usage

Import

```python
>>> import pypoet
```

Hello World

```python
>>> (pypoet.PythonFile()
     .append(pypoet.Statement("print('Hello World!')"))
     .write("hello_world.py"))
```

Conditionals

```python
>>> cond_if = (pypoet.If("len(sys.argv) > 1")
               .add_statement("print('Hello, sys.argv[1]')"))
>>> cond_else = (pypoet.Else()
                 .add_statement("print('Goodbye.')"))
>>> (pypoet.PythonFile()
    .append(pypoet.Statement("import sys"))
    .append(cond_if)
    .append(cond_else)
    .write("conditionals.py"))
```
