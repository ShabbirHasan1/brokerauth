import requests
from allauth.account import app_settings

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.utils import build_absolute_uri
from django.urls import reverse

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
        extra_data = self.get_data(token, app)
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)

    def get_data(self, token, app):
        # Verify the user first
        headers = {'Authorization': f'{app.id}:{token}'}
        resp = requests.get(
            self.identity_url,
            headers=headers
        )
        resp = resp.json()

        if resp['status'] != 'success':
            raise OAuth2Error()

        return resp['data']


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
    """
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
    """
    pass


oauth2_login = FivePaisaOAuth2LoginView.adapter_view(FivePaisaOAuth2Adapter)
oauth2_callback = FivePaisaOAuth2CallbackView.adapter_view(FivePaisaOAuth2Adapter)
