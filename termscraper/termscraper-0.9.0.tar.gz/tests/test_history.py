import os, sys

import termscraper
from termscraper import control as ctrl, modes as mo

sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))
from asserts import consistency_asserts

def chars(history_lines, columns):
    return ["".join(history_lines[y][x].data for x in range(columns))
            for y in range(len(history_lines))]


def test_index():
    screen = termscraper.HistoryScreen(5, 5, history=50)

    # Filling the screen with line numbers, so it's easier to
    # track history contents.
    for idx in range(screen.lines):
        screen.draw(str(idx))
        if idx != screen.lines - 1:
            screen.linefeed()

    assert not screen.history.top
    assert not screen.history.bottom

    # a) first index, expecting top history to be updated.
    line = screen.buffer[0]
    screen.index()
    assert screen.history.top
    assert screen.history.top[-1] == line

    # b) second index.
    line = screen.buffer[0]
    screen.index()
    assert len(screen.history.top) == 2
    assert screen.history.top[-1] == line

    # c) rotation.
    for _ in range(screen.history.size * 2):
        screen.index()

    assert len(screen.history.top) == 50


def test_reverse_index():
    screen = termscraper.HistoryScreen(5, 5, history=50)

    # Filling the screen with line numbers, so it's easier to
    # track history contents.
    for idx in range(screen.lines):
        screen.draw(str(idx))
        if idx != screen.lines - 1:
            screen.linefeed()

    assert not screen.history.top
    assert not screen.history.bottom

    screen.cursor_position()

    # a) first index, expecting top history to be updated.
    line = screen.buffer[screen.lines-1]
    screen.reverse_index()
    assert screen.history.bottom
    assert screen.history.bottom[0] == line

    # b) second index.
    line = screen.buffer[screen.lines-1]
    screen.reverse_index()
    assert len(screen.history.bottom) == 2
    assert screen.history.bottom[1] == line

    # c) rotation.
    for _ in range(screen.history.size * 2):
        screen.reverse_index()

    assert len(screen.history.bottom) == 50


def test_prev_page():
    screen = termscraper.HistoryScreen(4, 4, history=40)
    screen.set_mode(mo.LNM)

    assert screen.history.position == 40

    # Once again filling the screen with line numbers, but this time,
    # we need them to span on multiple lines.
    for idx in range(screen.lines * 10):
        screen.draw(str(idx))
        screen.linefeed()

    assert screen.history.top
    assert not screen.history.bottom
    assert screen.history.position == 40
    assert screen.display == [
        "37  ",
        "38  ",
        "39  ",
        "    "
    ]
    consistency_asserts(screen)

    assert chars(screen.history.top, screen.columns)[-4:] == [
        "33  ",
        "34  ",
        "35  ",
        "36  "
    ]

    # a) first page up.
    screen.prev_page()
    assert screen.history.position == 38
    assert len(screen.buffer) == screen.lines
    assert screen.display == [
        "35  ",
        "36  ",
        "37  ",
        "38  "
    ]
    consistency_asserts(screen)

    assert chars(screen.history.top, screen.columns)[-4:] == [
        "31  ",
        "32  ",
        "33  ",
        "34  "
    ]

    assert len(screen.history.bottom) == 2
    assert chars(screen.history.bottom, screen.columns) == [
        "39  ",
        "    ",
    ]

    # b) second page up.
    screen.prev_page()
    assert screen.history.position == 36
    assert len(screen.buffer) == screen.lines
    assert screen.display == [
        "33  ",
        "34  ",
        "35  ",
        "36  ",
    ]
    consistency_asserts(screen)

    assert len(screen.history.bottom) == 4
    assert chars(screen.history.bottom, screen.columns) == [
        "37  ",
        "38  ",
        "39  ",
        "    ",
    ]

    # c) same with odd number of lines.
    screen = termscraper.HistoryScreen(5, 5, history=50)
    screen.set_mode(mo.LNM)

    for idx in range(screen.lines * 10):
        screen.draw(str(idx))
        screen.linefeed()

    assert screen.history.top
    assert not screen.history.bottom
    assert screen.history.position == 50
    assert screen.display == [
        "46   ",
        "47   ",
        "48   ",
        "49   ",
        "     "
    ]
    consistency_asserts(screen)

    screen.prev_page()
    assert screen.history.position == 47
    assert screen.display == [
        "43   ",
        "44   ",
        "45   ",
        "46   ",
        "47   "
    ]
    consistency_asserts(screen)

    assert len(screen.history.bottom) == 3
    assert chars(screen.history.bottom, screen.columns) == [
        "48   ",
        "49   ",
        "     ",
    ]

    # d) with a ratio other than 0.5
    screen = termscraper.HistoryScreen(4, 4, history=40, ratio=0.75)
    screen.set_mode(mo.LNM)

    for idx in range(screen.lines * 10):
        screen.draw(str(idx))
        screen.linefeed()

    assert screen.history.top
    assert not screen.history.bottom
    assert screen.history.position == 40
    assert screen.display == [
        "37  ",
        "38  ",
        "39  ",
        "    "
    ]
    consistency_asserts(screen)

    screen.prev_page()
    assert screen.history.position == 37
    assert screen.display == [
        "34  ",
        "35  ",
        "36  ",
        "37  "
    ]
    consistency_asserts(screen)

    assert len(screen.history.bottom) == 3
    assert chars(screen.history.bottom, screen.columns) == [
        "38  ",
        "39  ",
        "    "
    ]

    # e) same with cursor in the middle of the screen.
    screen = termscraper.HistoryScreen(5, 5, history=50)
    screen.set_mode(mo.LNM)

    for idx in range(screen.lines * 10):
        screen.draw(str(idx))
        screen.linefeed()

    assert screen.history.top
    assert not screen.history.bottom
    assert screen.history.position == 50
    assert screen.display == [
        "46   ",
        "47   ",
        "48   ",
        "49   ",
        "     "
    ]
    consistency_asserts(screen)

    screen.cursor_to_line(screen.lines // 2)

    while screen.history.position > screen.lines:
        screen.prev_page()

    assert screen.history.position == screen.lines
    assert len(screen.buffer) == screen.lines
    assert screen.display == [
        "1    ",
        "2    ",
        "3    ",
        "4    ",
        "5    "
    ]
    consistency_asserts(screen)

    while screen.history.position < screen.history.size:
        screen.next_page()

    assert screen.history.position == screen.history.size
    assert screen.display == [
        "46   ",
        "47   ",
        "48   ",
        "49   ",
        "     "
    ]
    consistency_asserts(screen)

    # e) same with cursor near the middle of the screen.
    screen = termscraper.HistoryScreen(5, 5, history=50)
    screen.set_mode(mo.LNM)

    for idx in range(screen.lines * 10):
        screen.draw(str(idx))

        screen.linefeed()

    assert screen.history.top
    assert not screen.history.bottom
    assert screen.history.position == 50
    assert screen.display == [
        "46   ",
        "47   ",
        "48   ",
        "49   ",
        "     "
    ]
    consistency_asserts(screen)

    screen.cursor_to_line(screen.lines // 2 - 2)

    while screen.history.position > screen.lines:
        screen.prev_page()

    assert screen.history.position == screen.lines
    assert len(screen.buffer) == screen.lines
    assert screen.display == [
        "1    ",
        "2    ",
        "3    ",
        "4    ",
        "5    "
    ]
    consistency_asserts(screen)

    while screen.history.position < screen.history.size:
        screen.next_page()

    assert screen.history.position == screen.history.size
    assert len(screen.buffer) == screen.lines
    assert screen.display == [
        "46   ",
        "47   ",
        "48   ",
        "49   ",
        "     "
    ]
    consistency_asserts(screen)


def test_prev_page_large_sparse():
    # like test_prev_page, this test does the same checks
    # but uses a larger screen and it does not write on every
    # line.
    # Because screen.buffer is optimized to not have entries
    # for empty lines, this setup may uncover bugs that
    # test_prev_page cannot
    screen = termscraper.HistoryScreen(4, 8, history=16)
    screen.set_mode(mo.LNM)

    assert screen.history.position == 16

    # Filling the screen with line numbers but only
    # if they match the following sequence.
    # This is to leave some empty lines in between
    # to test the sparsity of the buffer.
    FB = [2, 5, 8, 13, 18]
    for idx in range(19):
        if idx in FB:
            screen.draw(str(idx))
        screen.linefeed()

    assert screen.history.top
    assert not screen.history.bottom
    assert screen.history.position == 16
    assert screen.display == [
        "    ",
        "13  ",
        "    ",
        "    ",
        "    ",
        "    ",
        "18  ",
        "    ",
    ]
    consistency_asserts(screen)

    assert chars(screen.history.top, screen.columns) == [
        "    ",
        "    ",
        "2   ",
        "    ",
        "    ",
        "5   ",
        "    ",
        "    ",
        "8   ",
        "    ",
        "    ",
        "    ",
    ]

    # a) first page up.
    screen.prev_page()
    assert screen.history.position == 12
    assert len(screen.buffer) == screen.lines
    assert screen.display == [
        "8   ",
        "    ",
        "    ",
        "    ",
        "    ",
        "13  ",
        "    ",
        "    ",
    ]
    consistency_asserts(screen)

    assert chars(screen.history.top, screen.columns) == [
        "    ",
        "    ",
        "2   ",
        "    ",
        "    ",
        "5   ",
        "    ",
        "    ",
    ]

    assert len(screen.history.bottom) == 4
    assert chars(screen.history.bottom, screen.columns) == [
        "    ",
        "    ",
        "18  ",
        "    ",
    ]

    # b) second page up.
    screen.prev_page()
    assert screen.history.position == 8
    assert len(screen.buffer) == screen.lines
    assert screen.display == [
        "    ",
        "5   ",
        "    ",
        "    ",
        "8   ",
        "    ",
        "    ",
        "    ",
    ]
    consistency_asserts(screen)

    assert len(screen.history.bottom) == 8
    assert chars(screen.history.bottom, screen.columns) == [
        "    ",
        "13  ",
        "    ",
        "    ",
        "    ",
        "    ",
        "18  ",
        "    ",
    ]

    # c) third page up?
    # TODO this seems to not work as the remaining lines in the history
    # are not moved into the buffer. This is because the condition
    #
    #    if self.history.position > self.lines and self.history.top:
    #       ....
    # This bug/issue is present on 0.8.1


def test_next_page():
    screen = termscraper.HistoryScreen(5, 5, history=50)
    screen.set_mode(mo.LNM)

    # Once again filling the screen with line numbers, but this time,
    # we need them to span on multiple lines.
    for idx in range(screen.lines * 5):
        screen.draw(str(idx))
        screen.linefeed()

    assert screen.history.top
    assert not screen.history.bottom
    assert screen.history.position == 50
    assert screen.display == [
        "21   ",
        "22   ",
        "23   ",
        "24   ",
        "     "
    ]
    consistency_asserts(screen)

    # a) page up -- page down.
    screen.prev_page()
    screen.next_page()
    assert screen.history.top
    assert not screen.history.bottom
    assert screen.history.position == 50
    assert screen.display == [
        "21   ",
        "22   ",
        "23   ",
        "24   ",
        "     "
    ]
    consistency_asserts(screen)

    # b) double page up -- page down.
    screen.prev_page()
    screen.prev_page()
    screen.next_page()
    assert screen.history.position == 47
    assert screen.history.top
    assert chars(screen.history.bottom, screen.columns) == [
        "23   ",
        "24   ",
        "     "
    ]

    assert screen.display == [
        "18   ",
        "19   ",
        "20   ",
        "21   ",
        "22   "
    ]
    consistency_asserts(screen)

    # c) double page up -- double page down
    screen.prev_page()
    screen.prev_page()
    screen.next_page()
    screen.next_page()
    assert screen.history.position == 47
    assert len(screen.buffer) == screen.lines
    assert screen.display == [
        "18   ",
        "19   ",
        "20   ",
        "21   ",
        "22   "
    ]
    consistency_asserts(screen)

def test_next_page_large_sparse():
    screen = termscraper.HistoryScreen(5, 8, history=16)
    screen.set_mode(mo.LNM)

    assert screen.history.position == 16

    # Filling the screen with line numbers but only
    # if they match the following sequence.
    # This is to leave some empty lines in between
    # to test the sparsity of the buffer.
    FB = [2, 5, 8, 13, 18]
    for idx in range(19):
        if idx in FB:
            screen.draw(str(idx))
        screen.linefeed()

    assert screen.history.top
    assert not screen.history.bottom
    assert screen.history.position == 16
    assert screen.display == [
        "     ",
        "13   ",
        "     ",
        "     ",
        "     ",
        "     ",
        "18   ",
        "     ",
    ]
    consistency_asserts(screen)

    # a) page up -- page down.
    screen.prev_page()
    screen.next_page()
    assert screen.history.top
    assert not screen.history.bottom
    assert screen.history.position == 16
    assert screen.display == [
        "     ",
        "13   ",
        "     ",
        "     ",
        "     ",
        "     ",
        "18   ",
        "     ",
    ]
    consistency_asserts(screen)

    # b) double page up -- page down.
    screen.prev_page()
    screen.prev_page()
    screen.next_page()
    assert screen.history.position == 12
    assert screen.history.top
    assert chars(screen.history.bottom, screen.columns) == [
        "     ",
        "     ",
        "18   ",
        "     ",
    ]
    assert chars(screen.history.top, screen.columns) == [
        "     ",
        "     ",
        "2    ",
        "     ",
        "     ",
        "5    ",
        "     ",
        "     ",
    ]

    assert screen.display == [
        "8    ",
        "     ",
        "     ",
        "     ",
        "     ",
        "13   ",
        "     ",
        "     ",
    ]
    consistency_asserts(screen)

    # c) page down -- double page up -- double page down
    screen.next_page()
    screen.prev_page()
    screen.prev_page()
    screen.next_page()
    screen.next_page()
    assert screen.history.position == 16
    assert len(screen.buffer) == screen.lines
    assert screen.display == [
        "     ",
        "13   ",
        "     ",
        "     ",
        "     ",
        "     ",
        "18   ",
        "     ",
    ]
    consistency_asserts(screen)


def test_ensure_width(monkeypatch):
    screen = termscraper.HistoryScreen(5, 5, history=50)
    screen.set_mode(mo.LNM)
    escape = dict(termscraper.Stream.escape)
    escape.update({"N": "next_page", "P": "prev_page"})
    monkeypatch.setattr(termscraper.Stream, "escape", escape)

    stream = termscraper.Stream(screen)

    for idx in range(screen.lines * 5):
        stream.feed("{0:04d}".format(idx) + os.linesep)

    assert screen.display == [
        "0021 ",
        "0022 ",
        "0023 ",
        "0024 ",
        "     "
    ]
    consistency_asserts(screen)

    # Shrinking the screen should truncate the displayed lines following lines.
    screen.resize(5, 3)
    stream.feed(ctrl.ESC + "P")

    # Inequality because we have an all-empty last line.
    assert all(len(l._line) <= 3 for l in screen.history.bottom)
    assert screen.display == [
        "001",  # 18
        "001",  # 19
        "002",  # 20
        "002",  # 21
        "002"   # 22
    ]
    consistency_asserts(screen)


def test_not_enough_lines():
    screen = termscraper.HistoryScreen(5, 5, history=6)
    screen.set_mode(mo.LNM)

    for idx in range(screen.lines):
        screen.draw(str(idx))
        screen.linefeed()

    assert screen.history.top
    assert not screen.history.bottom
    assert screen.history.position == 6
    assert screen.display == [
        "1    ",
        "2    ",
        "3    ",
        "4    ",
        "     "
    ]
    consistency_asserts(screen)

    screen.prev_page()
    assert not screen.history.top
    assert len(screen.history.bottom) is 1
    assert chars(screen.history.bottom, screen.columns) == ["     "]
    assert screen.display == [
        "0    ",
        "1    ",
        "2    ",
        "3    ",
        "4    ",
    ]
    consistency_asserts(screen)

    screen.next_page()
    assert screen.history.top
    assert not screen.history.bottom
    assert screen.display == [
        "1    ",
        "2    ",
        "3    ",
        "4    ",
        "     "
    ]
    consistency_asserts(screen)


def test_draw(monkeypatch):
    screen = termscraper.HistoryScreen(5, 5, history=50)
    screen.set_mode(mo.LNM)
    escape = dict(termscraper.Stream.escape)
    escape.update({"N": "next_page", "P": "prev_page"})
    monkeypatch.setattr(termscraper.Stream, "escape", escape)

    stream = termscraper.Stream(screen)
    for idx in range(screen.lines * 5):
        stream.feed(str(idx) + os.linesep)

    assert screen.display == [
        "21   ",
        "22   ",
        "23   ",
        "24   ",
        "     "
    ]
    consistency_asserts(screen)

    # a) doing a pageup and then a draw -- expecting the screen
    #    to scroll to the bottom before drawing anything.
    stream.feed(ctrl.ESC + "P")
    stream.feed(ctrl.ESC + "P")
    stream.feed(ctrl.ESC + "N")
    stream.feed("x")

    assert screen.display == [
        "21   ",
        "22   ",
        "23   ",
        "24   ",
        "x    "
    ]
    consistency_asserts(screen)


def test_cursor_is_hidden(monkeypatch):
    screen = termscraper.HistoryScreen(5, 5, history=50)
    escape = dict(termscraper.Stream.escape)
    escape.update({"N": "next_page", "P": "prev_page"})
    monkeypatch.setattr(termscraper.Stream, "escape", escape)

    stream = termscraper.Stream(screen)
    for idx in range(screen.lines * 5):
        stream.feed(str(idx) + os.linesep)

    assert not screen.cursor.hidden

    stream.feed(ctrl.ESC + "P")
    assert screen.cursor.hidden
    stream.feed(ctrl.ESC + "P")
    assert screen.cursor.hidden
    stream.feed(ctrl.ESC + "N")
    assert screen.cursor.hidden
    stream.feed(ctrl.ESC + "N")
    assert not screen.cursor.hidden


def test_erase_in_display():
    screen = termscraper.HistoryScreen(5, 5, history=6)
    screen.set_mode(mo.LNM)

    for idx in range(screen.lines):
        screen.draw(str(idx))
        screen.linefeed()

    screen.prev_page()

    # See #80 on GitHub for details.
    screen.erase_in_display(3)
    assert not screen.history.top
    assert not screen.history.bottom
