"""
BEGIN_COPYRIGHT

IBM Confidential
OCO Source Materials

5727-I17
(C) Copyright IBM Corp. 2020 All Rights Reserved.
 
The source code for this program is not published or otherwise
divested of its trade secrets, irrespective of what has been
deposited with the U.S. Copyright Office.

END_COPYRIGHT
"""
import uuid


class GAAMAExample(object):
    __slots__ = ['example_id', 'question', 'passage']

    def __init__(self, question: str, passage: str):
        self.example_id = uuid.uuid4()
        self.question = question
        self.passage = passage

    def __str__(self):
        return "GAAMAExample(example_id={}, question={}, passage={})".format(
            self.example_id, self.question, self.passage
        )

    def __repr__(self):
        return "GAAMAExample(example_id={!r}, question={!r}, " \
               "passage={!r})".format(
            self.example_id, self.question, self.passage
        )
