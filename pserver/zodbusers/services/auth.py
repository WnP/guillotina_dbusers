from datetime import datetime
from datetime import timedelta
from plone.server import app_settings
from plone.server.api.service import Service
from plone.server.browser import UnauthorizedResponse
from plone.server.utils import get_authenticated_user
from plone.server.auth.validators import SaltedHashPasswordValidator

import jwt


class Login(Service):
    token_timeout = 60 * 60 * 1

    async def __call__(self):
        data = await self.request.json()
        creds = {
            'token': data['password'],
            'id': data['username']
        }
        validator = SaltedHashPasswordValidator(self.request)
        user = await validator.validate(creds)
        if user is None:
            return UnauthorizedResponse('login failed')

        jwt_token = jwt.encode({
            'exp': datetime.utcnow() + timedelta(seconds=self.token_timeout),
            'id': user.id
        }, app_settings['jwt']['secret']).decode('utf-8')

        return {
            'token': jwt_token
        }


class Refresh(Login):
    async def __call__(self):
        user = get_authenticated_user(self.request)
        if user is None:
            return UnauthorizedResponse('user not authorized')

        jwt_token = jwt.encode({
            'exp': datetime.utcnow() + timedelta(seconds=self.token_timeout),
            'id': user.id
        }, app_settings['jwt']['secret']).decode('utf-8')
        return {
            'token': jwt_token
        }
