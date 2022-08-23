# TODO: Functionalities needed for the index generation
# 1 - Traversal to obtain all the attributes from the document (in any level of nesting)
# 2 - Traversal to obtain all the values to index
from copy import deepcopy
import datetime

from bson.int64 import Int64

class DocumentTraverser:

    def __init__(self):
        self.traversed_attributes = {}
        self.document_attributes = {}
        self.indexable_content = []

    def _traverse(self, attribute_path, document_path, value, value_type):
        if value_type == list:
            self.document_attributes[document_path] = value_type
            for number, element in enumerate(value):
                updated_path = ''.join([
                    attribute_path,
                    '[',
                    str(number + 1),
                    ']',
                ])
                self._add_to_document_attributes(document_path, type(element))
                self._traverse(updated_path, document_path, element, type(element))
        elif value_type == dict:
            if document_path not in self.document_attributes:
                self.document_attributes[document_path] = value_type
            for attribute, attribute_value in value.items():
                updated_path = self._increment_document_path(attribute_path, attribute)
                updated_document_path = self._increment_document_path(document_path, attribute)
                self._add_to_document_attributes(updated_document_path, type(attribute_value))
                self._traverse(updated_path, updated_document_path, attribute_value, type(attribute_value))
        elif value_type in [str, int, float, Int64]:
            self._add_to_document_attributes(document_path, value_type)
            self.traversed_attributes[attribute_path] = value
            self.indexable_content.append(
                (document_path, value),
            )
        elif value_type == datetime.datetime:
            self._add_to_document_attributes(document_path, value_type)
            self.traversed_attributes[attribute_path] = value.strftime('%d/%m/%Y %H:%M:%S')

    def _add_to_document_attributes(self, document_path, value_type):
        if document_path not in self.document_attributes:
            self.document_attributes[document_path] = value_type

    def _increment_document_path(self, current_path, new_attribute):
        return '.'.join([current_path, new_attribute])
    
    def cleanup(self):
        self.traversed_attributes = {}
        # TODO: evaluate if we can mantain this dict while iterating through all documents
        # self.document_attributes = {}
        self.indexable_content = []

    def traverse(self, document):
        for attribute, value in document.items():
            # print(attribute, type(value))
            self._traverse(attribute, attribute, value, type(value))
    
    def get_traversed_attributes(self):
        return self.traversed_attributes

    def get_document_attributes(self):
        return self.document_attributes

    def get_document_attributes_without_top_level_attributes(self):
      filtered_document_attributes = deepcopy(self.document_attributes)
      attributes_for_removal = []
      for attribute in filtered_document_attributes:
          if '.' not in attribute and \
                  filtered_document_attributes[attribute] in [type(list()), type(dict())]:
              # print('Removing attribute from collection structure')
              attributes_for_removal.append(attribute)
          else:
              if filtered_document_attributes[attribute] in [type(list()), type(dict())]:
                  attributes_for_removal.append(attribute)
      for attribute in attributes_for_removal:
          del filtered_document_attributes[attribute]
      
      return filtered_document_attributes

    def get_indexable_content(self):
        return self.indexable_content


if __name__ == "__main__":
    document = {
  "_id": {
    "$oid": "52f587f0b42a75c4264022c4"
  },
  "teams": [
    {
      "name": "Washington Wizards",
      "abbreviation": "WAS",
      "score": 78,
      "home": True,
      "won": 0,
      "results": {
        "ast": 13,
        "blk": 2,
        "drb": 30,
        "fg": 27,
        "fg3": 4,
        "fg3_pct": ".211",
        "fg3a": 19,
        "fg_pct": ".375",
        "fga": 72,
        "ft": 20,
        "ft_pct": ".714",
        "fta": 28,
        "mp": 240,
        "orb": 9,
        "pf": 18,
        "plus_minus": "",
        "pts": 78,
        "stl": 8,
        "tov": 14,
        "trb": 39
      },
      "players": [
        {
          "ast": 1,
          "blk": 0,
          "drb": 6,
          "fg": 4,
          "fg3": 0,
          "fg3_pct": "",
          "fg3a": 0,
          "fg_pct": ".500",
          "fga": 8,
          "ft": 5,
          "ft_pct": ".833",
          "fta": 6,
          "mp": "35:00",
          "orb": 5,
          "pf": 4,
          "player": "Jared Jeffries",
          "plus_minus": -9,
          "pts": 13,
          "stl": 0,
          "tov": 2,
          "trb": 11
        },
        {
          "ast": 0,
          "blk": 0,
          "drb": 2,
          "fg": 5,
          "fg3": 1,
          "fg3_pct": ".250",
          "fg3a": 4,
          "fg_pct": ".500",
          "fga": 10,
          "ft": 4,
          "ft_pct": ".667",
          "fta": 6,
          "mp": "33:00",
          "orb": 1,
          "pf": 1,
          "player": "Jarvis Hayes",
          "plus_minus": "+2",
          "pts": 15,
          "stl": 1,
          "tov": 0,
          "trb": 3
        },
        {
          "ast": 3,
          "blk": 1,
          "drb": 2,
          "fg": 1,
          "fg3": 1,
          "fg3_pct": ".200",
          "fg3a": 5,
          "fg_pct": ".111",
          "fga": 9,
          "ft": 0,
          "ft_pct": "",
          "fta": 0,
          "mp": "30:00",
          "orb": 0,
          "pf": 0,
          "player": "Steve Blake",
          "plus_minus": "+4",
          "pts": 3,
          "stl": 1,
          "tov": 3,
          "trb": 2
        },
        {
          "ast": 2,
          "blk": 1,
          "drb": 5,
          "fg": 3,
          "fg3": 0,
          "fg3_pct": ".000",
          "fg3a": 1,
          "fg_pct": ".300",
          "fga": 10,
          "ft": 2,
          "ft_pct": "1.000",
          "fta": 2,
          "mp": "26:00",
          "orb": 0,
          "pf": 2,
          "player": "Larry Hughes",
          "plus_minus": "+7",
          "pts": 8,
          "stl": 0,
          "tov": 0,
          "trb": 5
        },
        {
          "ast": 2,
          "blk": 0,
          "drb": 4,
          "fg": 4,
          "fg3": 0,
          "fg3_pct": "",
          "fg3a": 0,
          "fg_pct": ".800",
          "fga": 5,
          "ft": 0,
          "ft_pct": "",
          "fta": 0,
          "mp": "18:00",
          "orb": 1,
          "pf": 2,
          "player": "Brendan Haywood",
          "plus_minus": "+2",
          "pts": 8,
          "stl": 0,
          "tov": 0,
          "trb": 5
        },
        {
          "ast": 0,
          "blk": 0,
          "drb": 5,
          "fg": 6,
          "fg3": 0,
          "fg3_pct": "",
          "fg3a": 0,
          "fg_pct": ".667",
          "fga": 9,
          "ft": 4,
          "ft_pct": ".667",
          "fta": 6,
          "mp": "30:00",
          "orb": 1,
          "pf": 3,
          "player": "Etan Thomas",
          "plus_minus": -18,
          "pts": 16,
          "stl": 3,
          "tov": 2,
          "trb": 6
        },
        {
          "ast": 1,
          "blk": 0,
          "drb": 1,
          "fg": 3,
          "fg3": 1,
          "fg3_pct": ".200",
          "fg3a": 5,
          "fg_pct": ".273",
          "fga": 11,
          "ft": 1,
          "ft_pct": ".500",
          "fta": 2,
          "mp": "21:00",
          "orb": 1,
          "pf": 2,
          "player": "Juan Dixon",
          "plus_minus": -18,
          "pts": 8,
          "stl": 1,
          "tov": 1,
          "trb": 2
        },
        {
          "ast": 2,
          "blk": 0,
          "drb": 2,
          "fg": 0,
          "fg3": 0,
          "fg3_pct": ".000",
          "fg3a": 3,
          "fg_pct": ".000",
          "fga": 5,
          "ft": 2,
          "ft_pct": ".500",
          "fta": 4,
          "mp": "20:00",
          "orb": 0,
          "pf": 2,
          "player": "Gilbert Arenas",
          "plus_minus": -25,
          "pts": 2,
          "stl": 1,
          "tov": 4,
          "trb": 2
        },
        {
          "ast": 0,
          "blk": 0,
          "drb": 2,
          "fg": 1,
          "fg3": 1,
          "fg3_pct": "1.000",
          "fg3a": 1,
          "fg_pct": ".250",
          "fga": 4,
          "ft": 0,
          "ft_pct": "",
          "fta": 0,
          "mp": "15:00",
          "orb": 0,
          "pf": 0,
          "player": "Mitchell Butler",
          "plus_minus": -18,
          "pts": 3,
          "stl": 1,
          "tov": 1,
          "trb": 2
        },
        {
          "ast": 2,
          "blk": 0,
          "drb": 1,
          "fg": 0,
          "fg3": 0,
          "fg3_pct": "",
          "fg3a": 0,
          "fg_pct": ".000",
          "fga": 1,
          "ft": 2,
          "ft_pct": "1.000",
          "fta": 2,
          "mp": "12:00",
          "orb": 0,
          "pf": 2,
          "player": "Lonny Baxter",
          "plus_minus": -7,
          "pts": 2,
          "stl": 0,
          "tov": 1,
          "trb": 1
        }
      ],
      "city": "Washington"
    }
  ],
  "date": {
    "$date": "2004-04-14T04:00:00.000+0000"
  }
}
    from pprint import pprint as pp
    from time import time
    start = time()
    d = DocumentTraverser() 
    d.traverse(document)
    # pp(d.get_indexable_content())
    pp(d.get_document_attributes())
    # pp(d.get_traversed_attributes())
    print('Total time: {}'.format(time() - start))
