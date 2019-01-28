"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""
from tornado.web import RequestHandler
from ..abcs import AuthorizationAccountStore
from anthill.framework.utils.translation import translate as _
from anthill.framework.auth.token.jwt.settings import token_settings
from anthill.framework.auth.token.jwt import authentication
from anthill.framework.auth.token import exceptions
import functools
import json
import jwt


jwt_decode_handler = token_settings.JWT_DECODE_HANDLER


def request_context(fn):
    @functools.wraps(fn)
    def wrap(*args, **kwargs):
        handler = args[0].handler  # obtain from self
        if 'handler' not in kwargs or kwargs['handler'] is None:
            kwargs['handler'] = handler
        return fn(*args, **kwargs)
    return wrap


class JWTStore(AuthorizationAccountStore):
    allow_caching = False

    def __init__(self, handler: RequestHandler = None):
        self._auth = authentication.JSONWebTokenAuthentication()
        self.handler = handler

    def _get_jwt_value(self, handler):
        return self._auth.get_jwt_value(handler.request)

    # noinspection PyMethodMayBeStatic
    def _get_jwt_payload(self, jwt_value):
        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()
        return payload

    @request_context
    def get_authz_permissions(self, identifier, handler: RequestHandler = None):
        jwt_value = self._get_jwt_value(handler)
        payload = self._get_jwt_payload(jwt_value)
        permissions = payload['permissions']
        # TODO: permissions is a dict: {'domain': json blob of lists of dicts}
        return permissions

    @request_context
    def get_authz_roles(self, identifier, handler: RequestHandler = None):
        jwt_value = self._get_jwt_value(handler)
        payload = self._get_jwt_payload(jwt_value)
        roles = payload['roles']
        try:
            roles = json.loads(roles)
        except json.JSONDecodeError:
            # roles = list(map(lambda x: x.strip(), roles.split(',')))
            roles = [r.strip() for r in roles.split(',')]
        return roles
