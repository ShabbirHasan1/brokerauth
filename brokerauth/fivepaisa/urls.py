from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import FivePaisaProvider


urlpatterns = default_urlpatterns(FivePaisaProvider)
