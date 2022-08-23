class KeywordQuery(object):

  __slots__ = ['keyword_query', 'parsed_keyword_query', 'keywords', 'length']

  def __init__(self, parsed_keyword_query, keyword_query):
    self.parsed_keyword_query = parsed_keyword_query
    self.keyword_query = keyword_query

  
  def get_value(self):
    return self.keyword_query
  
  def get_parsed_value(self):
    return self.parsed_keyword_query
  
  # def get_compound_segments(self):


  def get_keywords(self):

    if hasattr(self, 'keywords'):
      return self.keywords

    keywords = []

    for element in self.parsed_keyword_query:
      if isinstance(element, list):
        for item in element:
          keywords.append(item.replace('\"', ''))
        continue
      
      keywords.append(element.replace('\"', ''))
    
    self.keywords = keywords
    self.length = len(keywords)

    return keywords
