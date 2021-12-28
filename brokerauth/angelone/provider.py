from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AngelOneAccount(ProviderAccount):

    def to_str(self):
        dflt = super(AngelOneAccount, self).to_str()
        return '%s (%s)' % (
            self.account.extra_data.get('name', ''),
            dflt,
        )


class AngelOneProvider(OAuth2Provider):
    id = 'angelone'
    name = 'AngelOne'
    account_class = AngelOneAccount

    def extract_uid(self, data):
        return str(data['clientcode'])

    def extract_common_fields(self, data):
        return {'name': data.get('name'),
                'email': data.get('email', None)}


provider_classes = [AngelOneProvider]
