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

from ..authz.authz import DefaultPermissionVerifier, Permission
import logging
from uuid import uuid4
from . import abcs


logger = logging.getLogger('anthill.application')


class AccountStoreRealm(abcs.AuthorizingRealm):
    """
    A Realm interprets information from a datastore.
    """

    def __init__(self, name='AccountStoreRealm_' + str(uuid4()),
                 account_store=None, permission_verifier=DefaultPermissionVerifier()):
        self.name = name
        self.account_store = account_store
        self.permission_verifier = permission_verifier
        self.cache_handler = None

    def get_authzd_permissions(self, identifier, perm_domain):
        """
        :type identifier:  str
        :type perm_domain:  str
        :returns: a list of relevant json blobs, each a list of permission dicts
        """
        related_perms = []
        keys = ['*', perm_domain]

        def query_permissions(self):
            msg = ("Could not obtain cached permissions for [{0}]. "
                   "Will try to acquire permissions from account store."
                   .format(identifier))
            logger.debug(msg)

            # permissions is a dict:  {'domain': json blob of lists of dicts}
            permissions = self.account_store.get_authz_permissions(identifier)
            if not permissions:
                raise ValueError(
                    "Could not get permissions from account_store for {0}".format(identifier))
            return permissions

        try:
            logger.debug("Attempting to get cached authz_info for [{0}]".format(identifier))

            domain = 'authorization:permissions:' + self.name

            # related_perms is a list of json blobs whose contents are ordered
            # such that the order matches that in the keys parameter:
            related_perms = self.cache_handler.\
                hmget_or_create(domain=domain,
                                identifier=identifier,
                                keys=keys,
                                creator_func=query_permissions,
                                creator=self)
        except ValueError:
            logger.warning(
                "No permissions found for identifiers [{0}]. Returning None.".format(identifier))

        except AttributeError:
            # this means the cache_handler isn't configured
            queried_permissions = query_permissions(self)

            related_perms = [
                queried_permissions.get('*'),
                queried_permissions.get(perm_domain)
            ]

        return related_perms

    def get_authzd_roles(self, identifier):
        roles = []

        def query_roles(self):
            msg = ("Could not obtain cached roles for [{0}]. "
                   "Will try to acquire roles from account store."
                   .format(identifier))
            logger.debug(msg)

            roles = self.account_store.get_authz_roles(identifier)
            if not roles:
                raise ValueError(
                    "Could not get roles from account_store for {0}".format(identifier))
            return roles
        try:
            logger.debug("Attempting to get cached roles for [{0}]".format(identifier))

            roles = self.cache_handler.get_or_create(
                domain='authorization:roles:' + self.name,
                identifier=identifier,
                creator_func=query_roles,
                creator=self)
        except AttributeError:
            # this means the cache_handler isn't configured
            roles = query_roles(self)
        except ValueError:
            logger.warning(
                "No roles found for identifiers [{0}]. Returning None.".format(identifier))

        return set(roles)

    def is_permitted(self, identifiers, permission_s):
        """
        If the authorization info cannot be obtained from the accountstore,
        permission check tuple yields False.
        :type identifiers:  subject_abcs.IdentifierCollection
        :param permission_s: a collection of one or more permissions, represented
                             as string-based permissions or Permission objects
                             and NEVER comingled types
        :type permission_s: list of string(s)
        :yields: tuple(Permission, Boolean)
        """
        identifier = identifiers.primary_identifier

        for required in permission_s:
            domain = Permission.get_domain(required)

            # assigned is a list of json blobs:
            assigned = self.get_authzd_permissions(identifier, domain)

            is_permitted = False
            for perms_blob in assigned:
                is_permitted = self.permission_verifier.\
                    is_permitted_from_json(required, perms_blob)

            yield (required, is_permitted)

    def has_role(self, identifiers, required_role_s):
        """
        Confirms whether a subject is a member of one or more roles.
        If the authorization info cannot be obtained from the accountstore,
        role check tuple yields False.
        :type identifiers:  subject_abcs.IdentifierCollection
        :param required_role_s: a collection of 1..N Role identifiers
        :type required_role_s: Set of String(s)
        :yields: tuple(role, Boolean)
        """
        identifier = identifiers.primary_identifier

        # assigned_role_s is a set
        assigned_role_s = self.get_authzd_roles(identifier)

        if not assigned_role_s:
            logger.warning(
                'has_role:  no roles obtained from account_store for [{0}]'.format(identifier))
            for role in required_role_s:
                yield (role, False)
        else:
            for role in required_role_s:
                hasrole = ({role} <= assigned_role_s)
                yield (role, hasrole)
