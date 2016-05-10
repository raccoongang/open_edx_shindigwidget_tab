from django.utils.translation import ugettext_noop
from courseware.tabs import CourseTab


class ShindigwidgetTab(CourseTab):

    name = "shindigwidget_tab"
    title = ugettext_noop("Shindig Office Hours")
    view_name = "shindigwidget_dashboard"
    tab_id = "shindigwidget_tab"
    type = 'shindigwidget_tab'
    is_default = True
    is_dynamic = False

    @classmethod
    def is_enabled(cls, course, user=None):
        return True
