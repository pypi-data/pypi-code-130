# -----------------------------------------------------------------------------
#                      xrst: Extract Sphinx RST Files
#          Copyright (C) 2020-22 Bradley M. Bell (bradbell@seanet.com)
#              This program is distributed under the terms of the
#              GNU General Public License version 3.0 or later see
#                    https://www.gnu.org/licenses/gpl-3.0.txt
# ----------------------------------------------------------------------------
"""
{xrst_begin spell_cmd user}
{xrst_spell
    abcd
}

Spell Command
#############

Syntax
******
``{xrst_spell`` *word_1* ...  *word_n* :code:`}`

Here *word_1*, ..., *word_n* is the special word list for this section.
In the syntax above the list of words is all in one line.
They could be on different lines which helps when displaying
the difference between  versions of the corresponding file.
Each word is a sequence of letters.
Upper case letters start a new word (even when preceded by a letter).
You need not include latex commands in special word list because
words with a backslash directly before them are not include in spell checking.

Purpose
*******
You can specify a special list of words
(not normally considered correct spelling)
for the current section using the command above.
The line starting the command
can only have spaces and tabs before the command.

spelling
********
The list of words in
:ref:`spelling<run_xrst@sphinx_dir@spelling>`
are considered correct spellings for all sections.
The latex commands corresponding to the letters in the greek alphabet
are automatically added to this list.

Capital Letters
***************
The case of the first letter does not matter when checking spelling;
e.g., if ``abcd`` is *word_1* then ``Abcd`` will be considered a valid word.
Each capital letter starts a new word; e.g., `CamelCase` is considered to
be the two words 'camel' and 'case'.
Single letter words are always correct and not included in the
special word list; e.g., the word list entry ``CppAD`` is the same as ``Cpp``.

Double Words
************
It is considered an error to have only white space between two occurrences
of the same word. You can make an exception for this by entering
the same word twice (next to each other) in the special word list.

Example
*******
:ref:`spell_example`

{xrst_end spell_cmd}
"""
# ---------------------------------------------------------------------------
import sys
import re
import xrst
#
# Process the spell command for a section
#
# data_in:
# is the data for this section before the spell command is removed.
#
# file_name:
# is the name of the file that this data comes from. This is only used
# for error reporting.
#
# section_name:
# is the name of the section that this data is in. This is only used
# for error reporting.
#
# spell_checker:
# Is the pyspellchecker object used for error checking.
#
# data_out:
# is the data for this section after the spell command (if it exists)
# is removed.
#
# Spelling Warnings:
# A spelling warning is reported for each word (and double word) that is not
# in the spell_checker dictionary or the speical word list. A word is two or
# more letter characters. If a word is directly precceded by a backslash,
# it is ignored (so that latex commands do not generate warnings).
#
# data_out =
def spell_command(
    data_in, file_name, section_name, spell_checker
) :
    #
    # pattern
    pattern = dict()
    pattern['spell']     = re.compile(
        r'\n[ \t]*\{xrst_spell([^}]*)\}' +
        r'([ \t]*\{xrst_line [0-9]+@)?'
    )
    pattern['word_list'] = re.compile( r'[A-Za-z \t\n]*' )
    #
    # pattern
    # global pattern values used by spell command
    pattern['child']  = xrst.pattern['child']
    pattern['code']   = xrst.pattern['code']
    pattern['file_2'] = xrst.pattern['file_2']
    pattern['file_3'] = xrst.pattern['file_3']
    pattern['line']   = xrst.pattern['line']
    #
    # pattern
    # local pattern values only used by spell command
    pattern['directive']   = re.compile( r'\n[ ]*[.][.][ ]+[a-z-]+::' )
    pattern['http']  = re.compile( r'(https|http)://[A-Za-z0-9_/.]*' )
    pattern['ref_1'] = re.compile( r':ref:`[^\n<`]+`' )
    pattern['ref_2'] = re.compile( r':ref:`([^\n<`]+)<[^\n>`]+>`' )
    pattern['url_1'] = re.compile( r'`<[^\n>`]+>`_' )
    pattern['url_2'] = re.compile( r'`([^\n<`]+)<[^\n>`]+>`_' )
    #
    # The first choice is for line numbers which are not in original file.
    # The second is characters that are not letters, white space, or backslash.
    # These character separate double words so they are not an error.
    # The third is for the actual words (plus a possible backlash at start).
    pattern['word']  = re.compile(
        r'({xrst_line [0-9]+@|[^A-Za-z\s\\]+|\\?[A-Za-z][a-z]+)' )
    #
    #
    # m_spell
    m_spell       = pattern['spell'].search(data_in)
    #
    # special_used, double_used
    special_used  = dict()
    double_used   = dict()
    #
    # data_out
    data_out = data_in
    #
    # special_used, double_used
    if m_spell != None :
        #
        # check for multiple spell commands in one section
        m_tmp  = pattern['spell'].search(data_in, m_spell.end() )
        if m_tmp :
            msg  = 'There are two spell xrst commands in this section'
            xrst.system_exit(
                msg,
                file_name=file_name,
                section_name=section_name,
                m_obj=m_tmp,
                data=data_in
            )
        #
        # word_list
        word_list = m_spell.group(1)
        word_list = pattern['line'].sub('', word_list)
        m_tmp     = pattern['word_list'].search(word_list)
        if m_tmp.group(0) != word_list :
            msg  = 'The word list in spell command contains '
            msg += 'charactes that are not letters or white space.'
            xrst.system_exit(
                msg,
                file_name=file_name,
                section_name=section_name,
                m_obj=m_spell,
                data=data_in
            )
        #
        # special_used, double_used
        previous_lower = ''
        for m_obj in pattern['word'].finditer( word_list ) :
            word_lower = m_obj.group(0).lower()
            if not word_lower.startswith('{xrst_line') :
                special_used[ word_lower ] = False
                if word_lower == previous_lower :
                    double_used[ word_lower ] = False
                previous_lower = word_lower
        #
        # remove spell command
        start    = m_spell.start()
        end      = m_spell.end()
        data_out = data_in[: start] + data_in[end :]
    #
    # data_tmp
    # version of data_in with certain commands removed
    data_tmp = data_out
    #
    # commands with file names as arugments
    data_tmp = pattern['file_2'].sub('', data_tmp)
    data_tmp = pattern['file_3'].sub('', data_tmp)
    data_tmp = pattern['child'].sub('', data_tmp)
    data_tmp = pattern['http'].sub('', data_tmp)
    data_tmp = pattern['directive'].sub('', data_tmp)
    #
    # command with section names and headings as arguments
    data_tmp = pattern['ref_1'].sub('', data_tmp)
    data_tmp = pattern['ref_2'].sub(r'\1', data_tmp)
    data_tmp = pattern['code'].sub('', data_tmp)
    #
    # commands with external urls as arguments
    data_tmp = pattern['url_1'].sub('', data_tmp)
    data_tmp = pattern['url_2'].sub(r'\1', data_tmp)
    #
    # first_spell_error
    first_spell_error = True
    #
    # previous_word
    previous_word = ''
    #
    # m_obj
    for m_obj in pattern['word'].finditer( data_tmp ) :
        #
        # word, word_lower
        word       = m_obj.group(0)
        word_lower = word.lower()
        #
        if not word.startswith('{xrst_line') and word[0].isalpha()  :
            #
            unknown = len( spell_checker.unknown( [word] ) ) > 0
            if unknown :
                # word is not in the dictionary
                #
                if not word_lower in special_used :
                    # word is not in the list of special words
                    #
                    # first_spell_error
                    if first_spell_error :
                        msg  = '\nwarning: file = ' + file_name
                        msg += ', section = ' + section_name + '\n'
                        sys.stderr.write(msg)
                        first_spell_error = False
                    #
                    # line_number
                    m_tmp  = pattern['line'].search(data_tmp, m_obj.end() )
                    assert m_tmp
                    line_number = m_tmp.group(1)
                    #
                    # msg
                    msg  = 'spelling = ' + word
                    suggest = spell_checker.correction(word)
                    if suggest != word :
                        msg += ', suggest = ' + suggest
                    msg += ', line ' + line_number + '\n'
                    #
                    sys.stderr.write(msg)
                #
                # special_used
                special_used[word_lower] = True
            #
            double_word = word_lower == previous_word.lower()
            if double_word :
                # This is the second use of word with only white space between
                #
                if not word_lower in double_used :
                    # word is not in list of special double words
                    #
                    # first_spell_error
                    if first_spell_error :
                        msg  = 'warning: file = ' + file_name
                        msg += ', section = ' + section_name + '\n'
                        sys.stderr.write(msg)
                        first_spell_error = False
                    #
                    # line_number
                    m_tmp = pattern['line'].search(data_tmp, m_obj.end() )
                    assert m_tmp
                    line_number = m_tmp.group(1)
                    msg  = f'double word error: "{previous_word} {word}"'
                    msg += ', line ' + line_number + '\n'
                    sys.stderr.write(msg)
                #
                # double_used
                double_used[word_lower]  = True
        if not word.startswith('{xrst_line') :
            # previous_word
            # This captures when there are non space characters between words
            previous_word = word
    #
    # check for words that were not used
    for word_lower in special_used :
        if not (special_used[word_lower] or word_lower in double_used) :
            if first_spell_error :
                msg  = '\nwarning: file = ' + file_name
                msg += ', section = ' + section_name + '\n'
                sys.stderr.write(msg)
                first_spell_error = False
            msg = 'spelling word "' + word_lower + '" not needed\n'
            sys.stderr.write(msg)
    for word_lower in double_used :
        if not double_used[word_lower] :
            if first_spell_error :
                msg  = '\nwarning: file = ' + file_name
                msg += ', section = ' + section_name + '\n'
                sys.stderr.write(msg)
                first_spell_error = False
            msg  = 'double word "' + word_lower + ' ' + word_lower
            msg += '" not needed\n'
            sys.stderr.write(msg)
    #
    return data_out
