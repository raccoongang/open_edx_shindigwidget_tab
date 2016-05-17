# open_edx_shindigwidget_tab

add in `lms/urls.py` before static_tab

<pre>
url(
    r'^courses/{}/shindigwidget/'.format(
        settings.COURSE_ID_PATTERN,
    ),
    include('shindigwidget_tab.urls'),
),
</pre>

add in `ADDL_INSTALLED_APPS` `'shindigwidget_tab'`
