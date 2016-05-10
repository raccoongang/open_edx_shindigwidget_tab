from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import shindigwidget_dashboard

urlpatterns = patterns('',
    url(r"^$", login_required(shindigwidget_dashboard), name="shindigwidget_dashboard"),
)