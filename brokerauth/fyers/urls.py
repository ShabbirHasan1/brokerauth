from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import FyersProvider


urlpatterns = default_urlpatterns(FyersProvider)
