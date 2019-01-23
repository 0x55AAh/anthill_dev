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

from abc import ABCMeta, abstractmethod
from anthill.framework.auth.backends.authorizer import DefaultPermissionVerifier, Permission
from uuid import uuid4
import logging


AUTH_PERMISSIONS_DATA_SESSION_KEY = '_auth_perms_user_data'
AUTH_ROLES_DATA_SESSION_KEY = '_auth_roles_user_data'


def _get_cached_permissions(handler):
    return handler.session[AUTH_PERMISSIONS_DATA_SESSION_KEY]


def _get_cached_roles(handler):
    return handler.session[AUTH_ROLES_DATA_SESSION_KEY]


logger = logging.getLogger('anthill.application')


class BaseRealm(metaclass=ABCMeta):
    """
    A ``Realm`` access application-specific security entities such as accounts,
    roles, and permissions to perform authentication and authorization operations.
    ``Realm``s usually have a 1-to-1 correlation with an ``AccountStore``,
    such as a NoSQL or relational database, file system, or other similar resource.
    However, since most Realm implementations are nearly identical, except for
    the account query logic, a default realm implementation, ``AccountStoreRealm``,
    is provided, allowing you to configure it with the data API-specific
    ``AccountStore`` instance.
    Because most account stores usually contain Subject information such as
    usernames and passwords, a Realm can act as a pluggable authentication module
    in a <a href="http://en.wikipedia.org/wiki/Pluggable_Authentication_Modules">PAM</a>
    configuration.  This allows a Realm to perform *both* authentication and
    authorization duties for a single account store, catering to most
    application needs.  If for some reason you don't want your Realm implementation
    to participate in authentication, override the ``supports(authc_token)`` method
    to always return False.
    Because every application is different, security data such as users and roles
    can be represented in any number of ways.  Yosai tries to maintain a
    non-intrusive development philosophy whenever possible -- it does not require
    you to implement or extend any *User*, *Group* or *Role* interfaces or classes.
    Instead, Yosai allows applications to implement this interface to access
    environment-specific account stores and data model objects.  The
    implementation can then be plugged in to the application's Yosai configuration.
    This modular technique abstracts away any environment/modeling details and
    allows Yosai to be deployed in practically any application environment.
    Most users will not implement this ``Realm`` interface directly, but will
    instead use an ``AccountStoreRealm`` instance configured with an underlying
    ``AccountStore``. This setup implies that there is an ``AccountStoreRealm``
    instance per ``AccountStore`` that the application needs to access.
    Yosai introduces two additional Realm interfaces in order to separate authentication
    and authorization responsibilities.
    """

    @abstractmethod
    def do_clear_cache(self, identifiers):
        """
        :type identifiers:  SimpleRealmCollection
        """
        pass


class BaseAuthorizingRealm(Realm):
    """
    required attributes:
        permission_verifier
        role_verifier
    """

    @abstractmethod
    def get_authzd_permissions(self, identitier, domain):
        pass

    @abstractmethod
    def get_authzd_roles(self, identitier):
        pass

    @abstractmethod
    def is_permitted(self, identifiers, permission_s):
        """
        :type identifiers:  SimpleRealmCollection
        """
        pass

    @abstractmethod
    def has_role(self, identifiers, role_s):
        """
        :type identifiers:  SimpleRealmCollection
        """
        pass

    @abstractmethod
    def clear_cached_authorization_info(self, identifiers):
        pass


class DatastoreRealm(BaseAuthorizingRealm):
    """
    A Realm interprets information from a datastore.
    """

    def __init__(self, name='DatastoreRealm_' + str(uuid4()),
                 storage=None, permission_verifier=None):
        self.name = name
        self.storage = storage
        self.permission_verifier = permission_verifier or DefaultPermissionVerifier()

    def clear_cached_authorization_info(self, identifiers):
        pass

    def get_authzd_permissions(self, handler, perm_domain):
        """
        :type handler: tornado.web.RequestHandler
        :type perm_domain: str
        :returns: a list of relevant json blobs, each a list of permission dicts
        """
        related_perms = []
        identifier = handler.current_user.username

        def query_permissions(self):
            msg = ("Could not obtain cached permissions for [{0}]. "
                   "Will try to acquire permissions from account store."
                   .format(identifier))
            logger.debug(msg)

            # permissions is a dict:  {'domain': json blob of lists of dicts}
            permissions = self.storage.get_authz_permissions(identifier)
            if not permissions:
                raise ValueError(
                    "Could not get permissions from storage for {0}".format(identifier))
            return permissions

        try:
            logger.debug("Attempting to get cached permissions for [{0}]".format(identifier))
            queried_permissions = _get_cached_permissions(handler)
        except ValueError:
            logger.warning(
                "No permissions found for identifiers [{0}]. Returning None.".format(identifier))
            return []
        except AttributeError:
            # this means the sessions isn't configured
            queried_permissions = query_permissions(self)

        related_perms = [
            queried_permissions.get('*'),
            queried_permissions.get(perm_domain)
        ]

        return related_perms

    def get_authzd_roles(self, handler):
        roles = []
        identifier = handler.current_user.username

        def query_roles(self):
            msg = ("Could not obtain cached roles for [{0}]. "
                   "Will try to acquire roles from account store."
                   .format(identifier))
            logger.debug(msg)

            roles_ = self.storage.get_authz_roles(identifier)
            if not roles_:
                raise ValueError(
                    "Could not get roles from storage for {0}".format(identifier))
            return roles_
        try:
            logger.debug("Attempting to get cached roles for [{0}]".format(identifier))
            roles = _get_cached_roles(handler)
        except AttributeError:
            # this means the sessions isn't configured
            roles = query_roles(self)
        except ValueError:
            logger.warning(
                "No roles found for identifiers [{0}]. Returning None.".format(identifier))

        return set(roles)

    def is_permitted(self, handler, permission_s):
        """
        If the authorization info cannot be obtained from the accountstore,
        permission check tuple yields False.
        :type handler: tornado.web.RequestHandler
        :param permission_s: a collection of one or more permissions, represented
                             as string-based permissions or Permission objects
                             and NEVER comingled types
        :type permission_s: list of string(s)
        :yields: tuple(Permission, Boolean)
        """
        for required in permission_s:
            domain = Permission.get_domain(required)

            # assigned is a list of json blobs:
            assigned = self.get_authzd_permissions(handler, domain)

            is_permitted = False
            for perms_blob in assigned:
                is_permitted = self.permission_verifier.\
                    is_permitted_from_json(required, perms_blob)

            yield (required, is_permitted)

    def has_role(self, handler, required_role_s):
        """
        Confirms whether a subject is a member of one or more roles.
        If the authorization info cannot be obtained from the accountstore,
        role check tuple yields False.
        :type handler: tornado.web.RequestHandler
        :param required_role_s: a collection of 1..N Role identifiers
        :type required_role_s: Set of String(s)
        :yields: tuple(role, Boolean)
        """
        identifier = handler.current_user.username

        # assigned_role_s is a set
        assigned_role_s = self.get_authzd_roles(handler)

        if not assigned_role_s:
            logger.warning(
                'has_role:  no roles obtained from storage for [{0}]'.format(identifier))
            for role in required_role_s:
                yield (role, False)
        else:
            for role in required_role_s:
                hasrole = ({role} <= assigned_role_s)
                yield (role, hasrole)
