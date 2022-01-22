import requests
from allauth.account import app_settings
from allauth.socialaccount.helpers import render_authentication_error, complete_social_login
from allauth.socialaccount.providers.base import AuthError, ProviderException
from allauth.socialaccount.models import SocialLogin

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.utils import build_absolute_uri
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from requests import RequestException
from allauth.utils import get_request_param

from .client import FivePaisaOAuth2Client
from .provider import FivePaisaProvider


class FivePaisaOAuth2Adapter(OAuth2Adapter):
    provider_id = FivePaisaProvider.id

    access_token_url = 'https://openapi.5paisa.com/VendorsAPI/Service1.svc/GetAccessToken'
    authorize_url = 'https://dev-openapi.5paisa.com/WebVendorLogin/VLogin/Index'
    identity_url = 'https://api.fivepaisa.in/api/v2/profile'
    access_token_method = 'POST'

    basic_auth = True

    def complete_login(self, request, app, token, **kwargs):
        extra_data = kwargs['response']
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


class FivePaisaOAuth2ClientMixin(object):

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
        client = FivePaisaOAuth2Client(
            request, app.client_id, app.secret,
            self.adapter.access_token_method,
            self.adapter.access_token_url,
            callback_url,
            scope)
        return client


class FivePaisaOAuth2LoginView(FivePaisaOAuth2ClientMixin, OAuth2LoginView):
    pass


class FivePaisaOAuth2CallbackView(FivePaisaOAuth2ClientMixin, OAuth2CallbackView):

    def dispatch(self, request, *args, **kwargs):
        """ custom dispatch as it doesn't follows typic OAuth2 flow """
        if 'error' in request.GET or 'RequestToken' not in request.GET:
            # Distinguish cancel from error
            auth_error = request.GET.get('error', None)
            if auth_error == self.adapter.login_cancelled_error:
                error = AuthError.CANCELLED
            else:
                error = AuthError.UNKNOWN
            return render_authentication_error(
                request,
                self.adapter.provider_id,
                error=error)
        app = self.adapter.get_provider().get_app(self.request)
        client = self.get_client(request, app)
        try:
            # 5paisa doesn't have a seprate api for pull user profile
            # and provides the profile details along with access token
            # hence get_access_token function returns the entire body instead of just returning access token
            login_data = client.get_access_token(request.GET['RequestToken'], key=app.key)
            access_token = {'access_token':login_data['AccessToken']}
            token = self.adapter.parse_token(access_token)
            token.app = app
            login = self.adapter.complete_login(request,
                                                app,
                                                token,
                                                response=login_data)
            login.token = token
            if self.adapter.supports_state:
                login.state = SocialLogin \
                    .verify_and_unstash_state(
                    request,
                    get_request_param(request, 'state'))
            else:
                login.state = SocialLogin.unstash_state(request)
            return complete_social_login(request, login)
        except (PermissionDenied,
                OAuth2Error,
                RequestException,
                ProviderException) as e:
            return render_authentication_error(
                request,
                self.adapter.provider_id,
                exception=e)


oauth2_login = FivePaisaOAuth2LoginView.adapter_view(FivePaisaOAuth2Adapter)
oauth2_callback = FivePaisaOAuth2CallbackView.adapter_view(FivePaisaOAuth2Adapter)
