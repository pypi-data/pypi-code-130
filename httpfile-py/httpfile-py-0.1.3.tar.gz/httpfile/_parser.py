import re
import uuid
import time
import random
import json
from string import Template
from typing import Optional


class SafeDict(dict):
    def __missing__(self, key):
        return ''

    def __getitem__(self, key):
        if key == "uuid":
            return str(uuid.uuid4())
        elif key == "timestamp":
            return str(time.time_ns() / 1000)
        elif key == "randomInt":
            return str(random.randint(0, 1000))
        else:
            return super().__getitem__(key)


class HttpHeader:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value
        if "${" in self.value:
            self.value_template = Template(self.value)
        else:
            self.value_template = None

    def __repr__(self):
        return "(" + self.name + ":" + self.value + ")"


class HttpTarget:

    def __init__(self, index):
        self.index: int = index
        self.name: Optional[str] = None
        self.comment: Optional[str] = None
        self.tags: list[str] = []
        self.method: str = ""
        self.url: str = ""
        self.url_template: Optional[Template] = None
        self.schema: Optional[str] = None
        self.headers: list[HttpHeader] = []
        self.body: Optional[str] = None
        self.body_template: Optional[Template] = None
        self.body_lines: Optional[list[str]] = None
        self.script: Optional[str] = None
        self.variables: list[str] = []
        self.mock_result: Optional[str] = None
        self.graphql_query_text: Optional[str] = None
        self.graphql_query_template: Optional[Template] = None
        self.graphql_variables_text: Optional[str] = None
        self.graphql_variables_template: Optional[Template] = None

    def is_empty(self):
        return self.method == "" and self.url == ""

    def is_mocked(self):
        return self.mock_result is not None

    def clean(self):
        if self.url != "":
            self.url = self.replace_variables(self.url)
            if "${" in self.url:
                self.url_template = Template(self.url)
        if self.body is not None:
            self.body = self.replace_variables(self.body)
            if "${" in self.body:
                self.body_template = Template(self.body)
        if self.name is None:
            self.name = "http" + str(self.index)
        else:
            self.name = self.name.replace("-", "_")
        if self.method == "GRAPHQL":
            self.extract_graphql_document()
        mocked_lines = []
        for tag in self.tags:
            if tag.startswith("mock "):
                mocked_lines.append(tag[5:])
        if len(mocked_lines) > 0:
            self.mock_result = "\n".join(mocked_lines)

    def add_tag(self, tag):
        self.tags.append(tag)

    def add_header(self, name, value):
        if not (self.method == "GRAPHQL" and name.lower() == "content-type"):
            new_value = self.replace_variables(value)
            self.headers.append(HttpHeader(name, new_value))

    def add_script_line(self, script_line):
        pass

    def add_body_line(self, body_line):
        if self.body is None:
            self.body = body_line
            self.body_lines = [body_line]
        else:
            self.body = self.body + "\n" + body_line
            self.body_lines.append(body_line)

    def replace_variables(self, text: str):
        new_text = text
        while "{{" in new_text:
            start = new_text.index("{{")
            end = new_text.index("}}")
            if end < start:
                return new_text
            name = new_text[start + 2:end]
            if name.startswith("$"):
                name = name[1:]
            if not (name in self.variables):
                self.variables.append(name)
            value = '${' + name + "}"
            new_text = new_text[0:start] + value + new_text[end + 2:]
        return new_text

    def extract_graphql_document(self):
        variables_offset = -1
        variables_offset_end = -1
        for idx, l in enumerate(self.body_lines):
            line = l.strip()
            if line == "{":
                variables_offset = idx
            elif line == "}":
                variables_offset_end = idx
        if 0 < variables_offset < variables_offset_end:
            query = "\n".join(self.body_lines[0:variables_offset])
            self.graphql_query_text = self.replace_variables(query)
            self.graphql_variables_text = self.replace_variables("\n".join(self.body_lines[variables_offset:]))
            if "${" in self.graphql_variables_text:
                self.graphql_variables_template = Template(self.graphql_variables_text)
        else:
            self.graphql_query_text = self.replace_variables(self.body)
        if "${" in self.graphql_query_text:
            self.graphql_query_template = Template(self.graphql_query_text)
        # add application/json
        self.add_header("Content-Type", "application/json")

    def get_url(self, **params):
        if self.url_template is not None:
            return self.url_template.substitute(SafeDict(params))
        else:
            return self.url

    def get_http_headers(self, **params):
        http_headers = []
        for header in self.headers:
            if header.value_template is not None:
                http_headers.append((header.name, header.value_template.substitute(SafeDict(params))))
            else:
                http_headers.append((header.name, header.value))
        return http_headers

    def get_http_body(self, **params):
        if self.body_template is not None:
            return self.body_template.substitute(SafeDict(params))
        else:
            return self.body

    def get_graphql_document(self, **params):
        doc = {}
        if self.graphql_query_template is not None:
            doc['query'] = self.graphql_query_template.substitute(SafeDict(params))
        else:
            doc['query'] = self.graphql_query_text
        if self.graphql_variables_text is not None:
            if self.graphql_variables_template is not None:
                doc['variables'] = json.loads(self.graphql_variables_template.substitute(SafeDict(params)))
            else:
                doc['variables'] = json.loads(self.graphql_variables_text)
        return doc


def parse_httpfile(httpfile_text: str) -> list[HttpTarget]:
    targets: list[HttpTarget] = []
    lines = httpfile_text.splitlines()
    index = 1
    http_target = HttpTarget(index)
    for raw_line in lines:
        line = raw_line.rstrip()
        if (line == "" or line.startswith("#!/usr/bin/env")) and http_target.is_empty():
            continue
        if line.startswith("###"):  # request seperator
            comment = line[3:].strip()
            if http_target.is_empty():
                http_target.comment = comment
            else:
                http_target.clean()
                targets.append(http_target)
                index = index + 1
                http_target = HttpTarget(index)
                http_target.comment = comment
        elif line.startswith("//") or line.startswith("#"):  # comment
            if "@" in line:
                tag = line[line.index('@') + 1:]
                parts = re.split("[=\\s]", tag, 2)
                if parts[0] == "name":
                    http_target.name = parts[1]
                http_target.add_tag(tag)
            elif http_target.comment == "":
                http_target.comment = line[2].strip()
        elif (line.startswith("GET ") or line.startswith("POST ")
              or line.startswith("DELETE") or line.startswith("PUT ")
              or line.startswith("GRAPHQL ")) and http_target.method == "":  # http method and URL
            parts = line.split(' ', 3)  # format as `POST URL HTTP/1.1`
            http_target.method = parts[0]
            http_target.url = parts[1].strip()
            if len(parts) > 2:
                http_target.schema = parts[2]
        elif line.startswith("  ") \
                and ('  /' in line or '  ?' in line or '  &' in line) \
                and len(http_target.headers) == 0:  # long request url into several lines
            http_target.url = http_target.url + line.strip()
        elif (":" in line) and (http_target.body is None) and (http_target.script is None):  # http header
            offset = line.index(':')
            name = line[0:offset].strip()
            if ' ' in name:
                http_target.add_body_line(raw_line)
            else:
                http_target.add_header(name, line[offset + 1:].strip())
        elif line.startswith("<> "):  # response-ref
            continue
        else:  # http body
            if not (line == "" and http_target.body is None):
                if line.startswith("> {%"):  # indicate script
                    code = line[4:].strip()
                    if code.endswith("5}"):
                        code = code[0:-2]
                    http_target.script = code
                elif line.startswith("%}"):  # end of script
                    continue
                elif line.startswith("> "):  # insert the script file
                    http_target.script = line
                else:
                    if http_target.script is not None:
                        http_target.add_script_line(raw_line)
                    else:
                        http_target.add_body_line(raw_line)

    if not http_target.is_empty():
        http_target.clean()
        targets.append(http_target)
    return targets
