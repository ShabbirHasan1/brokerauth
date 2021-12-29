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

    def get_access_token(self, code, key):
        data = {
            'head': {
                'Key': self.consumer_key
            },
            'body': {
                'EncryKey': self.consumer_secret,
                'RequestToken': code,
                'UserId': key
            }
        }

        self._strip_empty_keys(data)
        url = self.access_token_url
        resp = requests.request(self.access_token_method,
                                url,
                                json=data)

        access_token = None
        if resp.status_code == 200:
            access_token = resp.json()
            if 'body' not in access_token or 'AccessToken' not in access_token['body'] or access_token['body']['AccessToken'] is None:
                raise OAuth2Error('Error retrieving access token: %s'
                                  % resp.content)
            access_token = access_token['body']

        return access_token
