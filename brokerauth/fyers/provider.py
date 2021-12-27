from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class FyersAccount(ProviderAccount):

    def to_str(self):
        dflt = super(FyersAccount, self).to_str()
        return '%s (%s)' % (
            self.account.extra_data.get('name', ''),
            dflt,
        )


class FyersProvider(OAuth2Provider):
    id = 'fyers'
    name = 'Fyers'
    account_class = FyersAccount

    def extract_uid(self, data):
        return str(data['fy_id'])

    def extract_common_fields(self, data):
        user = data.get('user', {})
        return {'name': data.get('name'),
                'email': data.get('email_id', None)}

    def get_default_scope(self):
        return []


provider_classes = [FyersProvider]
