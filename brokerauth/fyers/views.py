import requests
from allauth.socialaccount.helpers import render_authentication_error, complete_social_login
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.providers.base import AuthError, ProviderException

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.utils import get_request_param
from django.core.exceptions import PermissionDenied
from requests import RequestException

from .client import FyersOAuth2Client
from .provider import FyersProvider



class FyersOAuth2Adapter(OAuth2Adapter):
    provider_id = FyersProvider.id

    access_token_url = 'https://api.fyers.in/api/v2/validate-authcode'
    authorize_url = 'https://api.fyers.in/api/v2/generate-authcode'
    identity_url = 'https://api.fyers.in/api/v2/profile'
    access_token_method = 'POST'
    basic_auth = True

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_data(token, app)
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)

    def get_data(self, token, app):
        # Verify the user first
        headers = {'Authorization': f'{app.client_id}:{token}'}
        print(headers)
        resp = requests.get(
            self.identity_url,
            headers=headers
        )
        resp = resp.json()

        if resp['code'] != 200:
            raise OAuth2Error()

        return resp['data']


class FyersOAuth2CallbackView(OAuth2CallbackView):

    def get_client(self, request, app):
        client = super(FyersOAuth2CallbackView, self).get_client(request,
                                                                 app)
        fyers_client = FyersOAuth2Client(
            client.request, client.consumer_key, client.consumer_secret,
            client.access_token_method, client.access_token_url,
            client.callback_url, client.scope)
        return fyers_client

    def dispatch(self, request, *args, **kwargs):

        # This function had to be defined here because Fyers retuns the code
        # in parameter 'auth_code' and not 'code' parameter
        if 'error' in request.GET or 'auth_code' not in request.GET:
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
            access_token = client.get_access_token(request.GET['auth_code'])
            print('came till here')
            print(access_token)
            token = self.adapter.parse_token(access_token)
            token.app = app
            login = self.adapter.complete_login(request,
                                                app,
                                                token,
                                                response=access_token)
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


oauth2_login = OAuth2LoginView.adapter_view(FyersOAuth2Adapter)
oauth2_callback = FyersOAuth2CallbackView.adapter_view(FyersOAuth2Adapter)
