from django.template import engines
from django.test import TestCase

def render_template(text, context=None):
    """Create a template ``text`` that first loads patternfly."""
    template = engines["django"].from_string(text)
    if not context:
        context = {}
    return template.render(context)

def render_template_with_patternfly(text, context=None):
    """Create a template ``text`` that first loads patternfly."""
    if not context:
        context = {}
    return render_template("{% load patternfly %}" + text, context)

class TemplateTest(TestCase):
    def test_patternfly_html_template_title(self):
        res = render_template(
            '{% extends "patternfly/patternfly.html" %}'
            + "{% block patternfly_title %}"
            + "test_patternfly_title"
            + "{% endblock %}"
        )
        self.assertIn("test_patternfly_title", res)

    def test_patternfly_html_template_content(self):
        res = render_template(
            '{% extends "patternfly/patternfly.html" %}'
            + "{% block patternfly_content %}"
            + "test_patternfly_content"
            + "{% endblock %}"
        )
        self.assertIn("test_patternfly_content", res)
