def regexize_keywords(
    keyword_str, keyword_delimiter=" ", line_delimiter="\n", case_insensitive=True
):
    r"""Convert a string of keywords into a regular expression that can be used as input
    for the sentenCy sentex component. You can separate keywords individually or into
    groups using keyword and line delimiters.

    Example usage:
    >>> from sentency.regex import regexize_keywords
    >>> keyword_str = "abdominal aortic aneurysm\naneurysm abdominal aorta"
    >>> regexize_keywords(keyword_str)
    (?i)((abdominal.*aortic.*aneurysm)|(aneurysm.*abdominal.*aorta))

    keyword_str: `str`, The keyword string to be converted into a regular expression.
    keyword_delimiter: `str`, The delimiter separating individual keywords in
    `keyword_str`. Default is `' '`
    line_delimiter: `str`, The string separating lines into a regular expression.
    Default is `'\n'`
    case_insensitive: `bool`, Should the regular expression be case-insensitive?
    RETURNS: `str`, The regular expression
    """
    keyword_str = keyword_str.strip()
    keyword_phrases = keyword_str.split(line_delimiter)
    keyword_regexes = [
        f'({keyword.replace(keyword_delimiter, ".*")})' for keyword in keyword_phrases
    ]
    ci_flag = "(?i)" if case_insensitive else ""
    regex = f"{ci_flag}({'|'.join(keyword_regexes)})"
    return regex
