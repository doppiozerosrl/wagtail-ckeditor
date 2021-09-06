

from __future__ import absolute_import, unicode_literals

import json

from django.forms import widgets
from django.utils.safestring import mark_safe
from wagtail.utils.widgets import WidgetWithScript

from wagtail import __version__ as WAGTAIL_VERSION

if WAGTAIL_VERSION >= '2.0':
    from wagtail.admin.edit_handlers import RichTextFieldPanel
    from wagtail.admin.rich_text.converters.editor_html import EditorHTMLConverter
    from wagtail.core.rich_text import features
else:
    from wagtail.wagtailadmin.edit_handlers import RichTextFieldPanel
    from wagtail.wagtailcore.rich_text import DbWhitelister
    from wagtail.wagtailcore.rich_text import expand_db_html

from wagtail_ckeditor import settings


class CKEditor(WidgetWithScript, widgets.Textarea):

    def __init__(self, attrs=None, **kwargs):
        super(CKEditor, self).__init__(attrs)
        self.kwargs = {}
        self.features = kwargs.pop('features', None)
        if kwargs is not None:
            self.kwargs.update(kwargs)

        if self.features is None:
            self.features = features.get_default_features()
            self.converter = EditorHTMLConverter()
        else:
            self.converter = EditorHTMLConverter(self.features)

    def get_panel(self):
        return RichTextFieldPanel

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            translated_value = None
        else:
            if WAGTAIL_VERSION >= '2.0':
                translated_value = self.converter.from_database_format(value)
            else:
                translated_value = expand_db_html(value, for_editor=True)
        return super().render(name, translated_value, attrs)

    def render_js_init(self, editor_id, name, value):

        return "CKEDITOR.replace( '%s', %s);" % (editor_id, mark_safe(json.dumps(settings.WAGTAIL_CKEDITOR_CONFIG)))

    def value_from_datadict(self, data, files, name):
        original_value = super().value_from_datadict(data, files, name)
        if original_value is None:
            return None
        if WAGTAIL_VERSION >= '2.0':
            return self.converter.to_database_format(original_value)
        else:
            return DbWhitelister.clean(original_value)

