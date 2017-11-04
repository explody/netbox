from __future__ import unicode_literals
import sys

from django.conf import settings
from django.db import ProgrammingError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

BASE_PATH = getattr(settings, 'BASE_PATH', False)
LOGIN_REQUIRED = getattr(settings, 'LOGIN_REQUIRED', False)
SAML_ENABLED = getattr(settings, 'SAML_ENABLED', False)


class LoginRequiredMiddleware(object):
    """
    If LOGIN_REQUIRED is True, redirect all non-authenticated users to the login page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if LOGIN_REQUIRED and not request.user.is_authenticated():
            # Redirect unauthenticated requests to the login page. API requests are exempt from
            # redirection as the API performs its own authentication.
            api_path = reverse('api-root')

            if not request.path_info.startswith(api_path):

                # If not the login path, SAML is enabled and the request is *not* for a saml path,
                # OR not the login path, SAML is *not* enabled
                # Then redirect to the login URL
                if (request.path_info != settings.LOGIN_URL and
                        (SAML_ENABLED and not request.path_info.startswith("/saml2"))) or \
                   (request.path_info != settings.LOGIN_URL and not SAML_ENABLED):

                    return HttpResponseRedirect('{}?next={}'.format(settings.LOGIN_URL,
                                                                    request.path_info))
        return self.get_response(request)


class APIVersionMiddleware(object):
    """
    If the request is for an API endpoint, include the API version as a response header.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        api_path = reverse('api-root')
        response = self.get_response(request)
        if request.path_info.startswith(api_path):
            response['API-Version'] = settings.REST_FRAMEWORK_VERSION
        return response


class ExceptionHandlingMiddleware(object):
    """
    Intercept certain exceptions which are likely indicative of installation issues and provide helpful instructions
    to the user.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):

        # Raise exceptions if in debug mode
        if settings.DEBUG:
            raise exception

        # Determine the type of exception
        if isinstance(exception, ProgrammingError):
            template_name = 'exceptions/programming_error.html'
        elif isinstance(exception, ImportError):
            template_name = 'exceptions/import_error.html'
        elif isinstance(exception, PermissionError):
            template_name = 'exceptions/permission_error.html'
        else:
            template_name = '500.html'

        # Return an error message
        type_, error, traceback = sys.exc_info()
        return render(request, template_name, {
            'exception': str(type_),
            'error': error,
        }, status=500)
