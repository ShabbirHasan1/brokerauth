from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AliceBlueAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get('user').get('image_192', None)

    def to_str(self):
        dflt = super(AliceBlueAccount, self).to_str()
        return '%s (%s)' % (
            self.account.extra_data.get('name', ''),
            dflt,
        )


class AliceBlueProvider(OAuth2Provider):
    id = 'aliceblue'
    name = 'AliceBlue'
    account_class = AliceBlueAccount

    def extract_uid(self, data):
        return str(data['client_id'])

    def extract_common_fields(self, data):
        user = data.get('user', {})
        return {'name': data.get('name'),
                'email': data.get('email_id', None)}

    def get_default_scope(self):
        return ['orders', 'holdings']


provider_classes = [AliceBlueProvider]
