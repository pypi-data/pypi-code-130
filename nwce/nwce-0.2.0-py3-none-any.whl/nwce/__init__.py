import re
import os

DEFAULT_CONFIG = {"indent": "  ", "comments": "!", "config_type": "nxos", "negation": "no "}


def naturalize(value, max_length, integer_places=8):
    """
    Take an alphanumeric string and prepend all integers to `integer_places` places to ensure the strings
    are ordered naturally. For example:
        site9router21
        site10router4
        site10router19
    becomes:
        site00000009router00000021
        site00000010router00000004
        site00000010router00000019
    :param value: The value to be naturalized
    :param max_length: The maximum length of the returned string. Characters beyond this length will be stripped.
    :param integer_places: The number of places to which each integer will be expanded. (Default: 8)
    """
    if not value:
        return value
    output = []
    for segment in re.split(r"(\d+)", value):
        if segment.isdigit():
            output.append(segment.rjust(integer_places, "0"))
        elif segment:
            output.append(segment)
    ret = "".join(output)

    return ret[:max_length]


class CfgBlock(object):
    def __add__(self, other):
        """Make a merge of 2 CfgBlock objects."""
        return self.copy(align=True).merge(other.copy(align=True))

    def __init__(self, lines=None, config=None):
        if not config:
            self.config = DEFAULT_CONFIG.copy()
        else:
            self.config = {**DEFAULT_CONFIG.copy(), **config}

        self.line = None
        self.negate = None
        self.children = list()

        if lines:
            self._parse(lines)
            # removed because of bad performance
            # self._merge_duplicate_siblings()

    def __repr__(self):
        r = str(self)
        if self.children and r != "":
            r += "/"
        r += "".join(["(" + str(c) + ")" for c in self.children])
        return f"{self.__class__.__name__}: {r} ({len(self.children)} children)"

    def __str__(self):
        command = self.line if self.line is not None else ""
        negation = self.config["negation"] if (command and self.negate) else ""
        return negation + command

    def __sub__(self, other):
        """Make a diff of 2 CfgBlock objects."""
        return CfgBlock.diff(self.copy(align=True), other.copy(align=True))

    def _align(self):
        """Some objects have 2 representations (configs with only 1 top line)."""
        if self.line is None:
            return self

        c = CfgBlock()
        c.children.append(self)
        return c

    @staticmethod
    def _clean_blank_lines(lines):
        """Removes all blank lines."""
        p = re.compile(r"^\s*$")
        return [line for line in lines if not p.search(line)]

    @staticmethod
    def _clean_comments(lines, comments="!"):
        """Removes all comment lines."""
        p = re.compile(r"^\s*[" + re.escape(comments) + "]")
        return [line for line in lines if not p.search(line)]

    @staticmethod
    def _guess_indent(line):
        m = re.compile(r"^\s+").search(line)
        indent = m.group() if m else ""
        return indent

    def _merge_duplicate_siblings(self):
        """Returns the CfgBlock object with merged duplicate siblings."""
        res = CfgBlock()
        for c in self.children:
            res += c
        self.children = res.children
        return self

    def _parse(self, lines):
        """Parse string lines into a comprehensive CfgBlock object structure."""
        lines = self._clean_comments(lines, comments=self.config["comments"])
        lines = self._clean_blank_lines(lines)
        blocks = self._parse_blocks(lines)
        if len(blocks) == 0:
            return
        if len(blocks) == 1:
            self.line, self.negate, lines = self._parse_block(blocks[0])
            blocks = self._parse_blocks(lines)
        self.children = [CfgBlock(b, config=self.config) for b in blocks]

    def _parse_block(self, lines):
        """Parse string block to return top line and children lines."""
        lines = CfgBlock.indent(lines, num=-1, indent=CfgBlock._guess_indent(lines[0]))
        negate = lines[0].startswith(self.config["negation"])
        lines[0] = lines[0] if not negate else lines[0][len(self.config["negation"]) :]
        lines[0] = lines[0].strip()
        if len(lines) == 1:
            return lines[0], negate, []
        return lines[0], negate, CfgBlock.indent(lines[1:], num=-1, indent=CfgBlock._guess_indent(lines[1]))

    @staticmethod
    def _parse_blocks(lines):
        """Parse string lines to return string blocks."""
        res = []
        if len(lines) == 0:
            return res
        lines = CfgBlock.indent(lines, num=-1, indent=CfgBlock._guess_indent(lines[0]))
        i = 0
        while i < len(lines):
            j = i + 1
            if j < len(lines):
                indent = CfgBlock._guess_indent(lines[j])
                while j < len(lines) and 0 < len(indent) <= len(lines[j]) and lines[j][: len(indent)] == indent:
                    j += 1
            res.append(lines[i:j])
            i = j
        return res

    @staticmethod
    def _blocks_sort(block, regex_match):
        c1, c2, c3, clast = "", "", "", naturalize(block.line, 1000)
        if "id1" in regex_match.groupdict():
            c1 = naturalize(regex_match.group("id1"), 1000)
        if "id2" in regex_match.groupdict():
            c2 = naturalize(regex_match.group("id2"), 1000)
        if "id3" in regex_match.groupdict():
            c3 = naturalize(regex_match.group("id3"), 1000)
        return c1, c2, c3, clast

    @staticmethod
    def _params_sort(line, regex_match):
        if "params" in regex_match.groupdict():
            params = re.split(r"\s+", regex_match.group("params"))
            params.sort(key=lambda b: naturalize(b, 1000))
            res = line.line[: regex_match.start("params")]
            res += " ".join(params)
            res += line.line[regex_match.end("params") :]
            line.line = res
        return line

    def copy(self, align=False):
        """Returns a deep-copy of a CfgBlock object."""
        res = CfgBlock()
        res.config = self.config
        res.line = self.line
        res.negate = self.negate
        res.children = [c.copy() for c in self.children]
        if align:
            return res._align()
        return res

    def merge(self, other):
        """Returns the CfgBlock object merged with another CfgBlock."""
        for c in other.children:
            matching_blocks = [b for b in self.children if b.line == c.line]
            if len(matching_blocks) > 0:
                if matching_blocks[0].negate != c.negate:
                    matching_blocks[0].negate = c.negate
                    matching_blocks[0].children = c.children
                else:
                    matching_blocks[0].merge(c)
            else:
                d = c.copy()
                self.children.append(d)
        return self

    @staticmethod
    def diff(op1, op2):
        """Returns a new CfgBlock object from the diff of 2 CfgBlocks."""
        res = CfgBlock([])
        for b2 in op2.children:
            if not any([str(b2) == str(b1) for b1 in op1.children]):
                c = CfgBlock([])
                c.line = b2.line
                c.negate = not b2.negate
                res.children.insert(0, c)
        for b1 in op1.children:
            matching_blocks = [b2 for b2 in op2.children if b2.line == b1.line]
            if len(matching_blocks) > 0:
                if matching_blocks[0].negate != b1.negate:
                    res.children.append(b1)
                else:
                    c = CfgBlock.diff(b1, matching_blocks[0])
                    if c.children:
                        c.line = b1.line
                        c.negate = b1.negate
                        res.children.append(c)
            else:
                c = b1.copy()
                res.children.append(c)
        return res._merge_duplicate_siblings()

    def filter(self, regex):
        """Returns a new CfgBlock from the current CfgBlock filtered according to the regex."""

        if self.line and re.search(regex, self.line):
            return self.copy()

        # self.line doesn't match or can't match
        # if no children then return an empty CfgBlock
        if not self.children:
            return CfgBlock()

        # if self has children, filter them recursively...
        children = [c.filter(regex) for c in self.children]
        # but remove those empty CfgBlocks
        children = [c for c in children if c.children or c.line]

        # then return the results
        if children:
            res = self.copy()
            res.children = children
            return res
        else:
            return CfgBlock()

    def lines(self, comment_line=None, _recursion_count=0):
        """Returns a list of strings from the current CfgBlock."""

        comment_char = ""
        if comment_line is True and len(self.config["comments"]) > 0:
            comment_char = self.config["comments"][0]
        if self.line is not None:
            res = [str(self)]
            for c in self.children:
                res += self.indent(c.lines(_recursion_count=_recursion_count + 1), indent=self.config["indent"])
        else:
            res = list()
            previous_command = None
            previous_comment = False
            for c in self.children:
                command = c.line.split(" ")[0]
                if comment_line and _recursion_count < 1:
                    if previous_command and previous_command != command or previous_comment:
                        res += [comment_char]
                        previous_comment = False
                res += c.lines(_recursion_count=_recursion_count + 1)
                if comment_line and _recursion_count < 1:
                    if len(c.children) > 0:
                        previous_comment = True
                previous_command = command
            if comment_line:
                res += [comment_char]
        return res

    def text(self, comment_line=None):
        return "\n".join(self.lines(comment_line=comment_line))

    @staticmethod
    def indent(lines, indent="  ", num=1):
        """Returns an indented copy of the list of strings passed as argument. Indent may be positive or negative"""

        # copy lines to res
        res = lines[:]

        # no-op
        if len(res) == 0 or num == 0:
            return res

        # prepend indent to each line
        if num > 0:
            for n in range(0, num):
                res = [indent + line for line in res]
            return res

        # remove indent from each line
        if num < 0:
            for n in range(0, num, -1):
                i = 0
                while i < len(res):
                    if i > 0 and res[i][: len(indent)] != indent:
                        raise Exception(f"Line #{i}: Configuration is not correctly indented!")
                    res[i] = res[i][len(indent) :]
                    i += 1
            return res

    def sort(self, rules=None, merge_duplicate_siblings=False):
        """Returns the current CfgBlock object sorted according to the rule list passed as argument."""

        # find rules if not provided as argument
        if not rules:
            default_rules_dir = os.path.dirname(os.path.realpath(__file__))
            filename = os.path.join(default_rules_dir, self.config["config_type"] + ".re.txt")
            try:
                with open(filename) as f:
                    rules = CfgBlock(f.read().splitlines())
            except FileNotFoundError:
                print("Could not find rules!")

        # apply rules
        result = list()
        lines = self.children.copy()
        for rule in rules.children:
            # calculate matches
            p = re.compile(rule.line, flags=re.IGNORECASE)
            search_results = [{"block": b, "search_result": p.search(b.line)} for b in lines]

            # remove matched blocks from lines
            matched = [s for s in search_results if s["search_result"]]
            lines = [s["block"] for s in search_results if not s["search_result"]]

            # sort params, if any
            for s in matched:
                s["block"] = self._params_sort(s["block"], s["search_result"])

            # sort all matched blocks
            matched.sort(key=lambda s: self._blocks_sort(s["block"], s["search_result"]))

            # now sort matched blocks children using matching rule children
            result += [block["block"].sort(rules=rule) for block in matched]

        # default rule for all remaining lines
        lines.sort(key=lambda b: naturalize(b.line, 1000))
        result += [block.sort(rules=CfgBlock([])) for block in lines]

        self.children = result
        if merge_duplicate_siblings:
            self._merge_duplicate_siblings()
        return self

    def negative_first(self):
        """Returns the current CfgBlock object with negative lines first."""
        result = list()

        while self.children:
            b = self.children.pop(0)
            if b.negate:
                result.insert(0, b.negative_first())
            else:
                result.append(b.negative_first())

        self.children = result
        return self
