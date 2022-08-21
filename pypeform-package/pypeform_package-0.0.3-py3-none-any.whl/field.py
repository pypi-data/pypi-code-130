import typing


class Choice:
    id: str
    label: str

    def __init__(self, id: str, label: str):
        self.id = id
        self.label = label

    def __repr__(self):
        return f'Choice(label: {self.id}, label: {self.label})'

    def __str__(self):
        return self.__repr__()


class Field:
    id: str
    title: str
    type: str
    ref: str
    allow_multiple_selections: bool
    allow_other_choice: bool
    choices: typing.List[Choice]

    def __init__(self, id: str, title: str, type: str, ref: str, allow_multiple_selections: bool = None,
                 allow_other_choice: bool = None, choices: typing.List[Choice] = None):

        supported_field_types = ["multiple_choice", "short_text", "long_text", "number", "date", "email",
                                 "phone_number", "yes_no", "website", "file_upload", "nps", "opinion_scale",
                                 "ranking", "rating", "dropdown", "legal"]
        if type not in supported_field_types:
            raise NotImplementedError(f"{type} is not an accepted type of field. ")

        self.id = id
        self.title = title
        self.type = type
        self.ref = ref
        self.allow_multiple_selections = allow_multiple_selections
        self.allow_other_choice = allow_other_choice
        self.choices = choices

    def __repr__(self):
        return f'Field(id: {self.id}, title: {self.title}, type: {self.type}, ref: {self.ref}, ' \
               f'allow_multiple_selections: {self.allow_multiple_selections}, allow_other_choice: {self.allow_other_choice}, ' \
               f'choices: {self.choices})'

    @classmethod
    def from_definition_json(cls, field_dict: typing.Dict[str, typing.Any]):
        choice_objs = list()
        if 'choices' in field_dict:
            for choice in field_dict['choices']:
                choice_objs.append(Choice(id=choice['id'], label=choice['label']))

        return cls(id=field_dict['id'],
                   title=field_dict.get('title', None),
                   type=field_dict['type'],
                   ref=field_dict.get('ref', None),
                   allow_multiple_selections=field_dict.get('allow_multiple_selections', None),
                   allow_other_choice=field_dict.get('allow_other_choice', None),
                   choices=choice_objs if len(choice_objs) >= 1 else None
                   )
