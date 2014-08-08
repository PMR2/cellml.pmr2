import zope.component
import zope.interface
import zope.schema

from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import ITextAreaWidget
from z3c.form.browser.textarea import TextAreaFieldWidget

from plone.registry.interfaces import IRegistry
import z3c.form

from pmr2.z3cform import form

from cellml.pmr2.interfaces import IVHostRemap
from cellml.pmr2.interfaces import IPrefixMap


@zope.component.adapter(IPrefixMap, ITextAreaWidget)
class DictTextAreaConverter(BaseDataConverter):
    
    def toWidgetValue(self, value):
        if not value:
            return u''
        items = value.items()
        items.sort()
        return u'\n'.join(['%s %s' % i for i in items])

    def toFieldValue(self, value):
        return {k.strip(): v.strip()
            for k, v in (line.split(None, 1)
                for line in value.splitlines())
        }


class VHostRemapEditForm(form.EditForm):
    """
    VHost remap edit form.
    """

    fields = z3c.form.field.Fields(IVHostRemap)
    fields['prefix_maps'].widgetFactory = TextAreaFieldWidget

    def update(self):
        super(VHostRemapEditForm, self).update()
        self.request['disable_border'] = True

    def getContent(self):
        registry = zope.component.getUtility(IRegistry)
        return registry.forInterface(IVHostRemap, prefix='cellml.pmr2.vhost')
