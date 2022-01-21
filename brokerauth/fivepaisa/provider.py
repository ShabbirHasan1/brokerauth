from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class FivePaisaAccount(ProviderAccount):

    def to_str(self):
        dflt = super(FivePaisaAccount, self).to_str()
        return '%s (%s)' % (
            self.account.extra_data.get('name', ''),
            dflt,
        )


class FivePaisaProvider(OAuth2Provider):
    id = 'fivepaisa'
    name = '5Paisa'
    account_class = FivePaisaAccount

    def extract_uid(self, data):
        return str(data['ClientCode'])

    def extract_common_fields(self, data):
        user = data.get('user', {})
        return {'name': data.get('ClientName'),
                'email': data.get('email_id', None)}

    def get_default_scope(self):
        return []


provider_classes = [FivePaisaProvider]