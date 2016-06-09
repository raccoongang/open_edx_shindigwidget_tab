from django.utils.translation import ugettext_noop
from .views import get_shindig_settings, is_valid_settings
from courseware.tabs import EnrolledTab


class ShindigwidgetTab(EnrolledTab):

    name = "shindigwidget_tab"
    title = ugettext_noop("Shindig Office Hours")
    view_name = "shindigwidget_dashboard"
    tab_id = "shindigwidget_tab"
    type = 'shindigwidget_tab'
    is_default = True
    is_dynamic = False

    @classmethod
    def is_enabled(cls, course, user=None):
        if not super(ShindigwidgetTab, cls).is_enabled(course, user=user):
            return False

        shindig_settings = get_shindig_settings(course)
        if is_valid_settings(shindig_settings):
            return True

        return False
