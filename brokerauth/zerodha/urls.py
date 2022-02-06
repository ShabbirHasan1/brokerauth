from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import ZerodhaProvider


urlpatterns = default_urlpatterns(ZerodhaProvider)
