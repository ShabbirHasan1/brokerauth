import requests
import hashlib
from collections import OrderedDict

from django.utils.http import urlencode

from allauth.socialaccount.providers.oauth2.client import (
    OAuth2Client,
    OAuth2Error,
)


class ZerodhaOAuth2Client(OAuth2Client):

    def get_redirect_url(self, authorization_url, extra_params):
        params = {
            'api_key': self.consumer_key,
            'v': 3
        }

        params.update(extra_params)
        sorted_params = OrderedDict()
        for param in sorted(params):
            sorted_params[param] = params[param]
        return '%s?%s' % (authorization_url, urlencode(sorted_params))

    def get_access_token(self, code):
        h = hashlib.sha256(self.consumer_key.encode("utf-8") + code.encode("utf-8") + self.consumer_secret.encode("utf-8"))
        checksum = h.hexdigest()
        data = {
            "api_key": self.consumer_key,
            "request_token": code,
            "checksum": checksum
        }

        params = None
        self._strip_empty_keys(data)
        url = self.access_token_url
        if self.access_token_method == 'GET':
            params = data
            data = None

        resp = requests.request(self.access_token_method,
                                url,
                                params=params,
                                data=data)

        access_token = None
        if resp.status_code in [200, 201]:
            access_token = resp.json()['data']
        if not access_token or 'access_token' not in access_token:
            raise OAuth2Error('Error retrieving access token: %s'
                              % resp.content)
        return access_token
