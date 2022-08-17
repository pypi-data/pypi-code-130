import os
from coder import Coder


#
# CoderUtilities
#
class CoderUtilities:

    #
    # Imports a python file into coder, that can be inserted into main code
    #
    # Args:
    #   file_path - linux or windows path
    #   file_name - file name with extension
    #   eol - default escape n, but can be overridden
    #   auto_indent - default False, True forces indent according to current coder setup
    #   i - default 0, ident for output code
    #
    # Returns:
    #   Coder object with python code
    #
    @staticmethod
    def python_to_coder(file_path, file_name, eol='\n', auto_indent=False, i=0):
        c = Coder()
        _file = os.path.join(file_path, file_name)
        file = open(_file, "r")
        data = file.read()
        lines = data.split(eol)
        indent = 0
        last_indent_count = 0

        for line in lines:
            nl = line.strip()
            if nl == '':
                c.add(i, 'c.new_line()')
            else:
                indent_count = len(line) - len(line.lstrip())
                if auto_indent:
                    if indent_count > last_indent_count:
                        indent += 1
                    elif indent_count < last_indent_count:
                        indent -= 1

                    last_indent_count = indent_count
                    if indent < 0:
                        indent = 0

                    if nl.find('# ') == 0:
                        nl = nl.replace('# ', '')
                        c.new_line()
                        c.add(i, '# ' + nl)
                        c.add(i, 'c.comment(' + str(indent) + ', "' + nl + '")')
                    else:
                        c.add(i, 'c.add(' + str(indent) + ', "' + nl + '")')

                else:
                    indent_count = int(indent_count / c.indent_space)
                    if nl.find('# ') == 0:
                        nl = nl.replace('# ', '')
                        c.new_line()
                        c.add(i, '# ' + nl)
                        c.add(i, 'c.comment(' + str(indent_count) + ', "' + nl + '")')
                    else:
                        c.add(i, 'c.add(' + str(indent_count) + ', "' + nl + '")')

        return c

    #
    # Imports a html file into coder, that can be inserted into main code
    #
    # Args:
    #   file_path - linux or windows path
    #   file_name - file name with extension
    #   eol - default escape n, but can be overridden
    #   auto_indent - default False, True forces indent according to current coder setup
    #   i - default 0, ident for output code
    #
    # Returns:
    #   Coder object with python code
    #
    @staticmethod
    def html_to_coder(file_path, file_name, eol='\n', auto_indent=False, i=0):
        c = Coder(code_type="html")
        _file = os.path.join(file_path, file_name)
        file = open(_file, "r")
        data = file.read()
        lines = data.split(eol)
        indent = 0
        last_indent_count = 0

        for line in lines:
            nl = line.strip()
            if nl == '':
                c.add(i, 'c.new_line()')
            else:
                indent_count = len(line) - len(line.lstrip())
                if auto_indent:
                    if indent_count > last_indent_count:
                        indent += 1
                    elif indent_count < last_indent_count:
                        indent -= 1

                    last_indent_count = indent_count
                    if indent < 0:
                        indent = 0

                    if (nl.find('<!-- ') == 0) or (nl.find(' -->') == 0):
                        nl = nl.replace('<!-- ', '')
                        nl = nl.replace(' -->', '')
                        c.new_line()
                        c.add(i, '# ' + nl)
                        c.add(i, 'c.comment(' + str(indent) + ', "' + nl + '")')
                    else:
                        c.add(i, 'c.add(' + str(indent) + ', "' + nl + '")')

                else:
                    indent_count = int(indent_count / c.indent_space)
                    if (nl.find('<!-- ') == 0) or (nl.find(' -->') == 0):
                        nl = nl.replace('<!-- ', '')
                        nl = nl.replace(' -->', '')
                        c.new_line()
                        c.add(i, '# ' + nl)
                        c.add(i, 'c.comment(' + str(indent_count) + ', "' + nl + '")')
                    else:
                        c.add(i, 'c.add(' + str(indent_count) + ', "' + nl + '")')

        return c

    #
    # Imports a java file into coder, that can be inserted into main code
    #
    # Args:
    #   file_path - linux or windows path
    #   file_name - file name with extension
    #   eol - default escape n, but can be overridden
    #   auto_indent - default False, True forces indent according to current coder setup
    #   i - default 0, ident for output code
    #
    # Returns:
    #   Coder object with python code
    #
    @staticmethod
    def java_to_coder(file_path, file_name, eol='\n', auto_indent=False, i=0):
        c = Coder(code_type="java")
        _file = os.path.join(file_path, file_name)
        file = open(_file, "r")
        data = file.read()
        lines = data.split(eol)
        indent = 0
        last_indent_count = 0

        for line in lines:
            nl = line.strip()
            if nl == '':
                c.add(i, 'c.new_line()')
            else:
                indent_count = len(line) - len(line.lstrip())
                if auto_indent:
                    if indent_count > last_indent_count:
                        indent += 1
                    elif indent_count < last_indent_count:
                        indent -= 1

                    last_indent_count = indent_count
                    if indent < 0:
                        indent = 0

                    if nl.find('// ') == 0:
                        nl = nl.replace('// ', '')
                        c.new_line()
                        c.add(i, '# ' + nl)
                        c.add(i, 'c.comment(' + str(indent) + ', "' + nl + '")')
                    else:
                        c.add(i, 'c.add(' + str(indent) + ', "' + nl + '")')

                else:
                    indent_count = int(indent_count / c.indent_space)
                    if nl.find('# ') == 0:
                        nl = nl.replace('// ', '')
                        c.new_line()
                        c.add(i, '# ' + nl)
                        c.add(i, 'c.comment(' + str(indent_count) + ', "' + nl + '")')
                    else:
                        c.add(i, 'c.add(' + str(indent_count) + ', "' + nl + '")')

        return c

    #
    # Imports a dart file into coder, that can be inserted into main code
    #
    # Args:
    #   file_path - linux or windows path
    #   file_name - file name with extension
    #   eol - default escape n, but can be overridden
    #   auto_indent - default False, True forces indent according to current coder setup
    #   i - default 0, ident for output code
    #
    # Returns:
    #   Coder object with python code
    #
    @staticmethod
    def dart_to_coder(file_path, file_name, eol='\n', auto_indent=False, i=0):
        c = Coder(code_type="dart")
        _file = os.path.join(file_path, file_name)
        file = open(_file, "r")
        data = file.read()
        lines = data.split(eol)
        indent = 0
        last_indent_count = 0

        for line in lines:
            nl = line.strip()
            if nl == '':
                c.add(i, 'c.new_line()')
            else:
                indent_count = len(line) - len(line.lstrip())
                if auto_indent:
                    if indent_count > last_indent_count:
                        indent += 1
                    elif indent_count < last_indent_count:
                        indent -= 1

                    last_indent_count = indent_count
                    if indent < 0:
                        indent = 0

                    if nl.find('// ') == 0:
                        nl = nl.replace('// ', '')
                        c.new_line()
                        c.add(i, '# ' + nl)
                        c.add(i, 'c.comment(' + str(indent) + ', "' + nl + '")')
                    else:
                        c.add(i, 'c.add(' + str(indent) + ', "' + nl + '")')

                else:
                    indent_count = int(indent_count / c.indent_space)
                    if nl.find('# ') == 0:
                        nl = nl.replace('// ', '')
                        c.new_line()
                        c.add(i, '# ' + nl)
                        c.add(i, 'c.comment(' + str(indent_count) + ', "' + nl + '")')
                    else:
                        c.add(i, 'c.add(' + str(indent_count) + ', "' + nl + '")')

        return c

    # Shorthand for python_to_coder
    def ptc(self, file_path, file_name, eol='\n', auto_indent=False, i=0):
        self.python_to_coder(file_path, file_name, eol, auto_indent, i)

    # Shorthand for html_to_coder
    def htc(self, file_path, file_name, eol='\n', auto_indent=False, i=0):
        self.html_to_coder(file_path, file_name, eol, auto_indent, i)

    # Shorthand for java_to_coder
    def jtc(self, file_path, file_name, eol='\n', auto_indent=False, i=0):
        self.java_to_coder(file_path, file_name, eol, auto_indent, i)

    # Shorthand for dart_to_coder
    def dtc(self, file_path, file_name, eol='\n', auto_indent=False, i=0):
        self.dart_to_coder(file_path, file_name, eol, auto_indent, i)


