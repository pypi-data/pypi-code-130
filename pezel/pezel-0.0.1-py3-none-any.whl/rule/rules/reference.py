from rule.rules.abstract import AbstractBasicRule


class ReferenceRule(AbstractBasicRule):
    def _str(self):
        return self.node_id

    @staticmethod
    def is_pointer():
        return True

    @staticmethod
    def get_yaml_tag():
        return u'!rule'
