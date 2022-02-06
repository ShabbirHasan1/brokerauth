from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class ZerodhaAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get('user').get('image_192', None)

    def to_str(self):
        dflt = super(ZerodhaAccount, self).to_str()
        return '%s (%s)' % (
            self.account.extra_data.get('name', ''),
            dflt,
        )


class ZerodhaProvider(OAuth2Provider):
    id = 'zerodha'
    name = 'Zerodha'
    account_class = ZerodhaAccount

    def extract_uid(self, data):
        return str(data['user_id'])

    def extract_common_fields(self, data):
        user = {'name': data.get('user_name'),
                'email': data.get('email', None)}
        return user

    def get_default_scope(self):
        return []


provider_classes = [ZerodhaProvider]
