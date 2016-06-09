from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import shindigwidget_dashboard, new_events

urlpatterns = patterns('',
    url(r"^$", login_required(shindigwidget_dashboard), name="shindigwidget_dashboard"),
    url(r"^new_events/$", login_required(new_events)),
)