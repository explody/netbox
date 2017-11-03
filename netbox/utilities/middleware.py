from __future__ import unicode_literals

from django.http import HttpResponseRedirect
from django.conf import settings
from django.urls import reverse
import logging

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
        logger = logging.getLogger('django')
        if LOGIN_REQUIRED and not request.user.is_authenticated():
            # Redirect unauthenticated requests to the login page. API requests are exempt from
            # redirection as the API performs its own authentication.
            api_path = reverse('api-root')

            if not request.path_info.startswith(api_path):
                # If SAML is enabled and the request is *not* for a saml path,
                # OR if SAML is not enabled, and the request is *not* for the login path
                # Then redirect to the login URL
                if (SAML_ENABLED and not request.path_info.startswith("/saml2")) or \
                   (not SAML_ENABLED and request.path_info != settings.LOGIN_URL):
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
