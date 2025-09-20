from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.exceptions import NotAuthenticated

User = get_user_model()

class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        cookie_name = getattr(settings, 'SIMPLE_JWT', {}).get('AUTH_COOKIE', None)
        if cookie_name is None:
            raise NotAuthenticated('No AUTH_COOKIE defined.')

        raw_token = request.COOKIES.get(cookie_name)
        if raw_token is None:
            return None

        try:
            validated_token = AccessToken(raw_token)
            user_id = validated_token['user_id']
            user = User.objects.get(id=user_id)
            return user, validated_token
        except Exception as e:
            raise NotAuthenticated(f'Invalid token: {e}')
