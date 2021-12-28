import requests
from collections import OrderedDict

from django.utils.http import urlencode

from allauth.socialaccount.providers.oauth2.client import (
    OAuth2Client,
    OAuth2Error,
)


class FivePaisaOAuth2Client(OAuth2Client):

    def get_redirect_url(self, authorization_url, extra_params):
        params = {
            'VendorKey': self.consumer_key,
            'ResponseURL': self.callback_url
        }
        if self.state:
            params['State'] = self.state
        params.update(extra_params)
        return '%s?%s' % (authorization_url, urlencode(params))

    def get_access_token(self, code):
        data = {
            'EncryKey': self.consumer_secret,
            'RequestToken': code,
            'UserId': '1h4UEVZ2qLi'
        }
        headers = {'Key':self.consumer_key}

        self._strip_empty_keys(data)
        url = self.access_token_url
        resp = requests.request(self.access_token_method,
                                url,
                                data=data,
                                headers=headers)
        access_token = None
        if resp.status_code == 200:
            access_token = resp.json()
        if not access_token or 'access_token' not in access_token:
            raise OAuth2Error('Error retrieving access token: %s'
                              % resp.content)
        return access_token
