from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import AngelOneProvider


urlpatterns = default_urlpatterns(AngelOneProvider)
