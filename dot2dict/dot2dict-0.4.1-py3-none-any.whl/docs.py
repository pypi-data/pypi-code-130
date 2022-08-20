def get_expanded_example() -> str:
    """

    :return:
    """

    markdown_string = """

Dot Notation to Dictionary and Hash Notation for Python 🐍 and Ruby ♦️.
    Provide JSON dot notation as input and get dictionary / hash notation as output.

dot2dict on pypi : Visit https://pypi.org

Example Use : 

```
(bash) $ dot2dict --dict=imdb -p json.1.2 -s val.soon --lang=ruby -v props.pageProps.mainColumnData.quotes.edges[0].node.lines[0].characters[0].name.__typename
```

```json
{
  "dotnotation": "props.pageProps.mainColumnData.quotes.edges[0].node.lines[0].characters[0].name.__typename",
  "python": true,
  "ruby": false,
  "language": "python",
  "output_lang": "python",
  "prefix": "json_data.nested.dict",
  "suffix": "title",
  "dict_name": "data_dictionary",
  "max_json_array_size": 1000,
  "use_double_quotes": false,
  "filter_list": [
    null,
    "''"
  ],
  "verbose": true,
  "version": null,
  "about": null,
  "example": null,
  "appearance": {
    "panel_color": "yellow",
    "panel_heading": " Python 🐍 Dictionary ",
    "panel_subtitle": " Copy from Below Snippet "
  }
}
```
The Options are Valid

```

╭──────────────────  Python 🐍 Dictionary  ──────────────────╮
│                                                            │
│     data_dictionary['json_data']['nested']['dict']['pr     │
│     ops']['pageProps']['mainColumnData']['quotes']['ed     │
│     ges'][0]['node']['lines'][0]['characters'][0]['nam     │
│     e']['__typename']['title']                             │
│                                                            │
╰────────────────  Copy from Below Snippet  ─────────────────╯

```

```
data_dictionary['json_data']['nested']['dict']['props']['pageProps']['mainColumnData']['quotes']['edges'][0]['node']['lines'][0]['characters'][0]['name']['__typename']['title']
```
 """

    return markdown_string
