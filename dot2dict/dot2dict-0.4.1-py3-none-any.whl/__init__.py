__version__ = '0.2.1'

"""
Dot Notation to Dictionary and Hash Notation for Python 🐍 and Ruby ♦️.
    Provide JSON dot notation as input and get dictionary / hash notation as output.
    
    dot2dict on pypi : Visit https://pypi.org
    
Example Use : 

(bash) $ dot2dict --dict=imdb -p json.1.2 -s val.soon --lang=ruby -v props.pageProps.mainColumnData.quotes.edges[0].node.lines[0].characters[0].name.__typename

{
  "dotnotation": "props.pageProps.mainColumnData.quotes.edges[0].node.lines[0].characters[0].name.__typename",
  "python": true,
  "ruby": false,
  "language": "ruby",
  "output_lang": "ruby",
  "prefix": "json.1.2",
  "suffix": "val.soon",
  "dict_name": "imdb",
  "max_json_array_size": 1000,
  "use_double_quotes": false,
  "filter_list": [
    null,
    "''"
  ],
  "verbose": true,
  "version": null,
  "about": null,
  "appearance": {
    "panel_color": "red",
    "panel_heading": " Ruby \u2666 Hash ",
    "panel_subtitle": " Copy from Below Snippet "
  }
}
The Options are Valid


╭───────────────────────────────────────────────────────────────  Ruby ♦ Hash  ────────────────────────────────────────────────────────────────╮
│                                                                                                                                              │
│     imdb.dig('json', '1', '2', 'props', 'pageProps', 'mainColumnData', 'quotes', 'edges', 0, 'node', 'lines', 0, 'characters', 0,            │
│     'name', '__typename', 'val', 'soon')                                                                                                     │
│                                                                                                                                              │
╰─────────────────────────────────────────────────────────  Copy from Below Snippet  ──────────────────────────────────────────────────────────╯

	imdb.dig('json', '1', '2', 'props', 'pageProps', 'mainColumnData', 'quotes', 'edges', 0, 'node', 'lines', 0, 'characters', 0, 'name', '__typename', 'val', 'soon')



"""

