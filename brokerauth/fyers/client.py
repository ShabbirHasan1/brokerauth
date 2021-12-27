from urllib.parse import parse_qsl

import requests
import json
from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.oauth2.client import (
    OAuth2Client,
    OAuth2Error,
)

from .provider import FyersProvider


class FyersOAuth2Client(OAuth2Client):
    """
    Custom client because Fyers uses different params to be passed than usual:
    """

    def get_access_token(self, code):

        payload = json.dumps({
            "grant_type": "authorization_code",
            "appIdHash": self.consumer_secret,
            "code": code
        })

        headers = {
            'Content-Type': 'application/json'
        }

        url = self.access_token_url

        resp = requests.request(
            self.access_token_method,
            url,
            data=payload,
            headers=headers)

        access_token = None
        if resp.status_code in [200, 201]:
            # Weibo sends json via 'text/plain;charset=UTF-8'
            if (resp.headers['content-type'].split(
                    ';')[0] == 'application/json' or resp.text[:2] == '{"'):
                access_token = resp.json()
            else:
                access_token = dict(parse_qsl(resp.text))

            print(access_token)
        if not access_token or 'access_token' not in access_token:
            raise OAuth2Error('Error retrieving access token: %s'
                              % resp.content)

        return access_token
