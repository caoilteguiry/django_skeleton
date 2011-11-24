from django.contrib.admin.filterspecs import FilterSpec
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _

class ContainsFilterSpec(FilterSpec):
    """
    Filter records which contain a specified piece of text. Enable this by
    subclassing ContainsFilterSpec and setting the lookup_choices tuple and
    registering the FilterSpec, e.g.
    {{{
    class BrowserFilterSpec(ContainsFilterSpec):
        def __init__(self, f, request, params, model, model_admin, 
                    field_path=None):
            super(BrowserFilterSpec, self).__init__(f, request, params, model,
                                                    model_admin, field_path)
            self.lookup_choices = ("Chrome", "Firefox",)

    # Register the filter
    FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'browser_filter',
                                       False),
                                   BrowserFilterSpec))
    }}}

    Additionally you will need to enable the filter in your model, e.g.
    {{{
    from filterspecs import BrowserFilterSpec 
    class Log(models.Model):
        user_agent = models.CharField(max_length=300)
        user_agent.browser_filter = True 
    }}}

    Finally, ensure this field is included in your ModelAdmin's list_filter
    tuple:
    {{{
    from models import *
    from django.contrib import admin

    class LogAdmin(admin.ModelAdmin):
        list_filter = ( "user_agent", )

    admin.site.register(Log, LogAdmin)
    }}}
    """
    def __init__(self, f, request, params, model, model_admin, field_path=None):
        super(ContainsFilterSpec, self).__init__(f, request, params, model,
                                                   model_admin, field_path)
        self.lookup_kwarg = '%s__contains' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        values_list = model.objects.values_list(f.name, flat=True)
        self.lookup_choices = ()

    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
               'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
               'display': _('All')}
        for val in self.lookup_choices:
            yield {'selected': smart_unicode(val) == self.lookup_val,
                   'query_string': cl.get_query_string(
                                   {self.lookup_kwarg: val}),
                   'display': val.upper()}
