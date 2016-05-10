import os
import requests

from requests.auth import HTTPBasicAuth
from edxmako.shortcuts import render_to_response
from edxmako.paths import add_lookup
from opaque_keys.edx.keys import CourseKey

from courseware.courses import get_course_with_access
from student.models import CourseAccessRole


SHINDIG_HOST_SERVER = "http://54.83.13.6/"
PATH_EVENTS = "api/events/"
PATH_TOKEN = "o/token/"
PATH_HASH_KEY_USER = "api/lti_users/"
PATH_HASH_KEY_COURSE = "api/lti_course/"
PATH_WIDGET = 'embed_events_widget/'


def shindigwidget_dashboard(request, course_id):
    course_key = CourseKey.from_string(course_id)
    course = get_course_with_access(request.user, "load", course_key)
    add_lookup('main', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shindigwidget_tab/templates'))
    iframe_src = None
    shindig_settings = get_shindig_settings(course)

    if is_valid_settings(shindig_settings):
        hash_key_user, hash_key_course = get_hash_key_user_and_course(request.user, course, shindig_settings)

        if hash_key_user and hash_key_course:
            iframe_src = '{}{}{}/{}/'.format(SHINDIG_HOST_SERVER, PATH_WIDGET, hash_key_user, hash_key_course)

            if CourseAccessRole.objects.filter(course_id=course.id, user=request.user, role__in=['staff', 'instructor']).exists():
                iframe_src += '?email={}&password={}'.format(shindig_settings['EMAIL'], shindig_settings['PASSWORD'])

    context = {
        "course": course,
        "iframe_src": iframe_src,
    }
    return render_to_response("shindigwidget_tab/shindigwidget_tab.html", context)


def get_hash_key_user_and_course(user, course, shindig_settings):
    hash_key_user = None
    hash_key_course = None
    client_auth = HTTPBasicAuth(shindig_settings.get('CLIENT_ID'), shindig_settings.get('CLIENT_SECRET'))
    post_data = {"grant_type": "password",
                 'username': shindig_settings.get('SERVER_USERNAME'),
                 'password': shindig_settings.get('SERVER_PASSWORD')}
    response = requests.post(SHINDIG_HOST_SERVER + PATH_TOKEN,
                             auth=client_auth,
                             data=post_data)

    if response.status_code == 200:
        token_json = response.json()
        access_token = token_json["access_token"]

        url = SHINDIG_HOST_SERVER + PATH_HASH_KEY_USER
        headers = {"Authorization": "Bearer " + access_token}
        if CourseAccessRole.objects.filter(course_id=course.id, user=user, role__in=['staff', 'instructor']).exists():
            edx_role = 'staff'
        else:
            edx_role = 'student'
        data = {'email': user.email,
                'username': user.username,
                'edx_role': edx_role}
        req_user = requests.post(url, headers=headers, data=data)
        if req_user.status_code == 201:
            req_data = req_user.json()
            hash_key_user =  req_data.get('hash_key')

        url = SHINDIG_HOST_SERVER + PATH_HASH_KEY_COURSE
        data = {'org': course.org,
                'number': course.number,
                'run': course.id.run,
                'display_name': course.display_name}
        req_course = requests.post(url, headers=headers, data=data)
        if req_course.status_code == 201:
            req_data = req_course.json()
            hash_key_course =  req_data.get('hash_key')

    return hash_key_user, hash_key_course


def get_shindig_settings(course):
    shindig_settings = {}
    if course:
        lti_passports = course.lti_passports
        for lti_passport in lti_passports:
            try:
                name, key, secret = [i.strip() for i in lti_passport.split(':')]
            except ValueError:
                return shindig_settings
            if name == 'shindig_server_user':
                shindig_settings.update({'SERVER_USERNAME': key,
                                         'SERVER_PASSWORD': secret})
            elif name == 'shindig_auth':
                shindig_settings.update({'CLIENT_ID': key,
                                         'CLIENT_SECRET': secret})
            elif name == 'shindig_user':
                shindig_settings.update({'EMAIL': key,
                                         'PASSWORD': secret})
    return shindig_settings


def is_valid_settings(settings):
    return 'EMAIL' in settings and \
           'PASSWORD' in settings and \
           'CLIENT_ID' in settings and \
           'CLIENT_SECRET' in settings and \
           'SERVER_USERNAME' in settings and \
           'SERVER_PASSWORD' in settings
