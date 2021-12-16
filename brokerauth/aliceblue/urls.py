from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import AliceBlueProvider


urlpatterns = default_urlpatterns(AliceBlueProvider)
