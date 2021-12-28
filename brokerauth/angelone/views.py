import requests
from allauth.socialaccount.helpers import complete_social_login, render_authentication_error
from allauth.socialaccount.providers.base import ProviderException

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.account import app_settings

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.utils import build_absolute_uri
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from requests import RequestException

from .client import AngelOneOAuth2Client
from .provider import AngelOneProvider
from smartapi import SmartConnect


class AngelOneOAuth2Adapter(OAuth2Adapter):
    provider_id = AngelOneProvider.id

    access_token_url = ''  # Not required as its not a OAUTH2
    authorize_url = 'https://smartapi.angelbroking.com/publisher-login'
    identity_url = ''  # Using the python client provided by vendor instead of rest call

    basic_auth = True

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_data(token, app)
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)

    def get_data(self, token, app):
        # Verify the user first

        obj = SmartConnect(api_key=app.client_id,
                           access_token=token.token,
                           refresh_token=token.token_secret)
        resp = obj.getProfile(token.token_secret)

        if not resp['status']:
            raise OAuth2Error()

        return resp['data']


class AngelOneOAuth2ClientMixin(object):

    def get_client(self, request, app):
        callback_url = reverse(self.adapter.provider_id + "_callback")
        protocol = (
                self.adapter.redirect_uri_protocol or
                app_settings.DEFAULT_HTTP_PROTOCOL)
        callback_url = build_absolute_uri(
            request, callback_url,
            protocol=protocol)
        provider = self.adapter.get_provider()
        scope = provider.get_scope(request)
        client = AngelOneOAuth2Client(
            request, app.client_id, app.secret,
            self.adapter.access_token_method,
            self.adapter.access_token_url,
            callback_url,
            scope)
        return client


class AngelOneOAuth2LoginView(AngelOneOAuth2ClientMixin, OAuth2LoginView):
    pass


class AngelOneOAuth2CallbackView(AngelOneOAuth2ClientMixin, OAuth2CallbackView):
    def dispatch(self, request, *args, **kwargs):
        app = self.adapter.get_provider().get_app(self.request)
        client = self.get_client(request, app)
        try:
            access_token = {'access_token': request.GET['auth_token'], 'refresh_token': request.GET['refresh_token']}
            token = self.adapter.parse_token(access_token)
            token.app = app
            login = self.adapter.complete_login(request,
                                                app,
                                                token,
                                                response=access_token)
            login.token = token
            return complete_social_login(request, login)
        except (PermissionDenied,
                OAuth2Error,
                RequestException,
                ProviderException) as e:
            return render_authentication_error(
                request,
                self.adapter.provider_id,
                exception=e)


oauth2_login = AngelOneOAuth2LoginView.adapter_view(AngelOneOAuth2Adapter)
oauth2_callback = AngelOneOAuth2CallbackView.adapter_view(AngelOneOAuth2Adapter)
