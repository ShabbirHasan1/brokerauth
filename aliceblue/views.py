import requests

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import AliceblueProvider


class AliceblueOAuth2Adapter(OAuth2Adapter):
    provider_id = AliceblueProvider.id

    access_token_url = 'https://ant.aliceblueonline.com/oauth2/token'
    authorize_url = 'https://ant.aliceblueonline.com/oauth2/auth'
    identity_url = 'https://ant.aliceblueonline.com/api/v1/user/profile'
    basic_auth = True

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_data(token, app.client_id)
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)

    def get_data(self, token, client_id):
        # Verify the user first
        headers = {'Authorization': 'Bearer {0}'.format(token)}
        resp = requests.get(
            self.identity_url,
            params={'client_id': client_id},
            headers=headers
        )
        resp = resp.json()

        if resp['status'] != 'success':
            raise OAuth2Error()

        return resp['data']


oauth2_login = OAuth2LoginView.adapter_view(AliceblueOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(AliceblueOAuth2Adapter)
