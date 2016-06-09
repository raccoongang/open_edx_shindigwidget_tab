import os
import requests

from django.http import JsonResponse
from edxmako.shortcuts import render_to_response
from edxmako.paths import add_lookup
from opaque_keys.edx.keys import CourseKey

from courseware.courses import get_course_with_access
from student.models import CourseAccessRole


PATH_HASH_KEY_USER = "/api/lti_users/"
PATH_HASH_KEY_COURSE = "/api/lti_course/"
PATH_WIDGET = '/embed_events_widget/'


def shindigwidget_dashboard(request, course_id):
    course_key = CourseKey.from_string(course_id)
    course = get_course_with_access(request.user, "load", course_key)
    add_lookup('main', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shindigwidget_tab/templates'))
    iframe_src = None
    shindig_settings = get_shindig_settings(course)

    if is_valid_settings(shindig_settings):
        hash_key_user, hash_key_course = get_hash_key_user_and_course(request, course, shindig_settings)

        if hash_key_user and hash_key_course:
            iframe_src = 'https://{}{}{}/{}/'.format(shindig_settings['SHINDIG_HOST_SERVER'],
                                                    PATH_WIDGET,
                                                    hash_key_user,
                                                    hash_key_course)

    context = {
        "course": course,
        "iframe_src": iframe_src,
    }
    return render_to_response("shindigwidget_tab/shindigwidget_tab.html", context)


def new_events(request, course_id):
    path_img = ''
    course_key = CourseKey.from_string(course_id)
    course = get_course_with_access(request.user, "load", course_key)
    shindig_settings = get_shindig_settings(course)

    if is_valid_settings(shindig_settings):
        hash_key_user, hash_key_course = get_hash_key_user_and_course(request, course, shindig_settings)
        headers = {"Authorization": "Token " + shindig_settings['ACCESS_TOKEN']}
        url = 'https://{}{}{}/new_events/'.format(shindig_settings['SHINDIG_HOST_SERVER'], PATH_HASH_KEY_USER, hash_key_user)
        req_new_events = requests.post(url, headers=headers, data={'hash_key_course': hash_key_course})

        if req_new_events.status_code == 200:
            req_data = req_new_events.json()
            if req_data.get('is_new_events'):
                path_img = 'https://{}{}'.format(shindig_settings['SHINDIG_HOST_SERVER'], req_data.get('path_img'))

    return JsonResponse({'path_img': path_img})

def get_hash_key_user_and_course(request, course, shindig_settings):
    hash_key_user = None
    hash_key_course = None
    headers = {"Authorization": "Token " + shindig_settings['ACCESS_TOKEN']}

    url = 'https://{}{}'.format(shindig_settings['SHINDIG_HOST_SERVER'], PATH_HASH_KEY_COURSE)
    data = {'org': course.org,
            'number': course.number,
            'run': course.id.run,
            'display_name': course.display_name,
            'domain': request.get_host()}
    req_course = requests.post(url, headers=headers, data=data)
    if req_course.status_code == 201:
        req_data = req_course.json()
        hash_key_course = req_data.get('hash_key')

    url = 'https://{}{}'.format(shindig_settings['SHINDIG_HOST_SERVER'], PATH_HASH_KEY_USER)
    if CourseAccessRole.objects.filter(course_id=course.id, user=request.user, role__in=['staff', 'instructor']).exists():
        edx_role = 'staff'
    else:
        edx_role = 'student'
    data = {'email': request.user.email,
            'username': request.user.username,
            'role': edx_role,
            'hash_key_course': hash_key_course,
            'domain': request.get_host()}
    req_user = requests.post(url, headers=headers, data=data)

    if req_user.status_code == 201:
        req_data = req_user.json()
        hash_key_user = req_data.get('hash_key')

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

            if name == 'shindig_auth':
                shindig_settings.update({'SHINDIG_HOST_SERVER': key,
                                         'ACCESS_TOKEN': secret})
    return shindig_settings


def is_valid_settings(settings):
    return 'SHINDIG_HOST_SERVER' in settings and \
           'ACCESS_TOKEN' in settings
