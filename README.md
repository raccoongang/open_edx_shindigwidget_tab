# open_edx_shindigwidget_tab
1. Install pade to the open edx from next repo: `git@github.com:raccoongang/open_edx_shindigwidget_tab.git`
    * add in `ADDL_INSTALLED_APPS` `'shindigwidget_tab'`
    * add in `lms/envs/common.py` -> `MAKO_TEMPLATES['main']` `'/edx/app/edxapp/venvs/edxapp/src/shindigwidget-tab/shindigwidget_tab/templates'`
    * add in `lms/urls.py` before static_tab
        <pre>
        url(
            r'^courses/{}/shindigwidget/'.format(
                settings.COURSE_ID_PATTERN,
            ),
            include('shindigwidget_tab.urls'),
        ),
        </pre>
    

2. Contact Shindig representative in order to obtain the following data:
    * `"shindig_auth:<server_url>:<token>",`

3. Change Course Advanced Settings in Open edX.
    * Open a course you are authoring and select `"Settings" ⇒ "Advanced Settings”`.
    * Navigate to the section titled `"LTI Passports"`. Add `"shindig_auth:<server_url>:<token>"` to module list.
    ![Alt text](/doc/images/img_1.png?raw=true "image")
