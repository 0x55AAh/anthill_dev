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
from anthill.framework.auth.backends.exceptions import UnauthorizedException
import itertools
import logging
import json
import collections


logger = logging.getLogger('anthill.application')


class BaseAuthorizer(metaclass=ABCMeta):
    """
    An ``Authorizer`` performs authorization (access control) operations
    for any given Subject (aka 'application user').

    Each method requires a subject identifiers to perform the action for the
    corresponding Subject/user.

    This identifiers argument is usually an object representing a user database
    primary key or a String username or something similar that uniquely
    identifies an application user. The runtime value of the this identifiers
    is application-specific and provided by the application's configured
    Realms.

    Note that the ``Permission`` methods in this interface accept either String
    arguments or Permission instances. This provides convenience in allowing
    the caller to use a String representation of a Permission if one is so
    desired.  Most implementations of this interface will simply convert these
    String values to Permission instances and then just call the corresponding
    method.
    """

    @abstractmethod
    def is_permitted(self, identifiers, permission_s):
        """
        Determines whether any Permission(s) associated with the subject
        implies the requested Permission(s) provided.

        :param identifiers: the application-specific subject/user identifiers(s)
        :type identifiers: subject_abcs.IdentifierCollection
        :param permission_s: a collection of 1..N permissions, all of the same type
        :type permission_s: List of authz_abcs.Permission object(s) or String(s)
        :returns: a List of tuple(s), containing the Permission and a Boolean
                  indicating whether the permission is granted, True if the
                  corresponding Subject/user is permitted, False otherwise
        """

    @abstractmethod
    def is_permitted_collective(self, identifiers, permission_s, logical_operator):
        """
        This method determines whether the requested Permission(s) are
        collectively granted authorization. The Permission(s) associated with
        the subject are evaluated to determine whether authorization is implied
        for each Permission requested. Results are collectively evaluated using
        the logical operation provided: either ANY or ALL.

        If operator=ANY: returns True if any requested permission is implied permission
        If operator=ALL: returns True if all requested permissions are implied permission
        Else returns False

        :param identifiers: the application-specific subject/user identifiers(s)
        :type identifiers: subject_abcs.IdentifierCollection
        :param permission_s: a collection of 1..N permissions, all of the same type
        :type permission_s: List of authz_abcs.Permission object(s) or String(s)
        :param logical_operator: any or all
        :type logical_operator: function (stdlib)
        :rtype: bool
        """

    @abstractmethod
    def check_permission(self, identifiers, permission_s, logical_operator):
        """
        This method determines whether the requested Permission(s) are
        collectively granted authorization.  The Permission(s) associated with
        the subject are evaluated to determine whether authorization is implied
        for each Permission requested.  Results are collectively evaluated using
        the logical operation provided: either ANY or ALL.

        This method is similar to is_permitted_collective except that it raises
        an AuthorizationException if collectively False else does not return any
        value.

        :param identifiers: the application-specific subject/user identifiers(s)
        :type identifiers: subject_abcs.IdentifierCollection
        :param permission_s: a collection of 1..N permissions, all of the same type
        :type permission_s: List of authz_abcs.Permission object(s) or String(s)
        :param logical_operator: any or all
        :type logical_operator: function (stdlib)
        :raises AuthorizationException: if the user does not have sufficient permission
        """

    @abstractmethod
    def has_role(self, identifiers, role_s):
        """
        Determines whether a ``Subject`` is a member of the Role(s) requested

        :param identifiers: the application-specific subject/user identifiers(s)
        :type identifiers: subject_abcs.IdentifierCollection
        :param role_s: 1..N role identifiers (strings)
        :type role_s: Set of Strings
        :returns: a set of tuple(s), each containing the Role identifier
                  requested and a Boolean indicating whether the subject is
                  a member of that Role
                  - the tuple format is: (role, Boolean)
        """

    @abstractmethod
    def has_role_collective(self, identifiers, role_s, logical_operator):
        """
        This method determines whether the Subject's role membership
        collectively grants authorization for the roles requested.  The
        Role(s) associated with the subject are evaluated to determine
        whether the roles requested are sufficiently addressed by those that
        the Subject is a member of. Results are collectively evaluated using
        the logical operation provided: either ANY or ALL.

        If operator=ANY, returns True if any requested role membership is
                         satisfied
        If operator=ALL: returns True if all of the requested permissions are
                         implied permission
        Else returns False

        :param identifiers: the application-specific subject/user identifiers(s)
        :type identifiers: subject_abcs.IdentifierCollection
        :param role_s: 1..N role identifiers (strings)
        :type role_s: Set of Strings
        :param logical_operator: any or all
        :type logical_operator: function (stdlib)
        :rtype: bool
        """

    @abstractmethod
    def check_role(self, identifiers, role_s, logical_operator):
        """
        This method determines whether the Subject's role membership
        collectively grants authorization for the roles requested.  The
        Role(s) associated with the subject are evaluated to determine
        whether the roles requested are sufficiently addressed by those that
        the Subject is a member of. Results are collectively evaluated using
        the logical operation provided: either ANY or ALL.

        This method is similar to has_role_collective except that it raises
        an AuthorizationException if collectively False else does not return any

        :param identifiers: the application-specific subject/user identifiers(s)
        :type identifiers: subject_abcs.IdentifierCollection
        :param role_s: 1..N role identifiers (strings)
        :type role_s: Set of Strings
        :param logical_operator: any or all
        :type logical_operator: function (stdlib)
        :raises AuthorizationException: if the user does not have sufficient
                                        role membership
        """


class BasePermission(metaclass=ABCMeta):
    """
    A ``Permission`` represents the ability to perform an action or access a
    resource.  A ``Permission`` is the most granular, or atomic, unit in a system's
    security policy and is the cornerstone upon which fine-grained security
    models are built.

    It is important to understand a ``Permission`` instance only represents
    functionality or access - it does not grant it. Granting access to an
    application functionality or a particular resource is done by the
    application's security configuration, typically by assigning Permissions to
    users, roles and/or groups.

    Most typical systems are role-based in nature, where a role represents
    common behavior for certain user types. For example, a system might have an
    Aministrator role, a User or Guest roles, etc. However, if you have a dynamic
    security model, where roles can be created and deleted at runtime, you
    can't hard-code role names in your code. In this environment, roles
    themselves aren't aren't very useful. What matters is what permissions are
    assigned to these roles.

    Under this paradigm, permissions are immutable and reflect an application's
    raw functionality (opening files, accessing a web URL, creating users, etc).
    This is what allows a system's security policy to be dynamic: because
    Permissions represent raw functionality and only change when the
    application's source code changes, they are immutable at runtime - they
    represent 'what' the system can do. Roles, users, and groups are the 'who'
    of the application. Determining 'who' can do 'what' then becomes a simple
    exercise of associating Permissions to roles, users, and groups in some
    way.

    Most applications do this by associating a named role with permissions
    (i.e. a role 'has a' collection of Permissions) and then associate users
    with roles (i.e. a user 'has a' collection of roles) so that by transitive
    association, the user 'has' the permissions in their roles. There are
    numerous variations on this theme (permissions assigned directly to users,
    or assigned to groups, and users added to groups and these groups in turn
    have roles, etc, etc). When employing a permission-based security model
    instead of a role-based one, users, roles, and groups can all be created,
    configured and/or deleted at runtime. This enables an extremely powerful
    security model.

    A benefit to Yosai is that, although it assumes most systems are based on
    these types of static role or dynamic role w/ permission schemes, it does
    not require a system to model their security data this way - all Permission
    checks are relegated to Realm implementations, and only those
    implementations really determine how a user 'has' a permission or not. The
    Realm could use the semantics described here, or it could utilize some
    other mechanism entirely - it is always up to the application developer.
    Yosai provides a very powerful default implementation of this interface in
    the form of the WildcardPermission. We highly recommend that you
    investigate this class before trying to implement your own Permissions.
    """

    @abstractmethod
    def implies(self, permission):
        """
        Returns True if this current instance implies all of the functionality
        and/or resource access described by the specified Permission argument,
        returning False otherwise.

        That is, this current instance must be exactly equal to or a
        superset of the functionalty and/or resource access described by the
        given Permission argument.  Yet another way of saying this is:
           - If permission1 implies permission2, then any Subject granted
             permission1 would have ability greater than or equal to that
             defined by permission2.

        :returns: bool
        """


class BasePermissionVerifier(metaclass=ABCMeta):
    @abstractmethod
    def is_permitted_from_json(self, required_perm, serialized_perms):
        pass

    @abstractmethod
    def is_permitted_from_str(self, required_perm, assigned_perms):
        pass


class Permission(BasePermission):
    """
    In this example, the first token is the *domain* that is being operated on
    and the second token is the *action* that is performed. Each level can contain
    multiple values.  Given support for multiple values, you could simply grant
    a user the permission 'blogpost:view,edit,create', granting the user
    access to perform ``view``, ``edit``, and ``create`` actions in the ``blogpost``
    *domain*. Then you could check whether the user has the ``'blogpost:create'``
    permission by calling:::
        subject.is_permitted(['blogpost:create'])
    (which would return true)

    In addition to granting multiple permissions using a single string, you can
    grant all permission for a particular level:
        * If you want to grant a user permission to perform all actions in the
        ``blogpost`` domain, you could simply grant the user ``'blogpost:*'``.
        With this permission granted, any permission check for ``'blogpost:XXX'```
        will return ``True``.
        * It is also possible to use the wildcard token at the domain
        level (or both levels), granting a user the ``'view'`` action across all
        domains: ``'*:view'``.

    Instance-level Access Control
    -----------------------------
    Another usage of ``Permission`` is to model instance-level
    Access Control Lists (ACLs). In this scenario, you use three tokens:
        * the first token is the *domain*
        * the second token is the *action*
        * the third token is the *instance* that is acted upon (target)
    For example, suppose you grant a user ``'blogpost:edit:12,13,18'``.
    In this example, assume that the third token contains system identifiers of
    blogposts. That would allow the user to edit blogpost with id ``12``, ``13``, and ``18``.
    Representing permissions in this manner is an extremely powerful way to
    express permissions as you can state permissions like:
        *``'blogpost:*:13'``, granting a user permission to perform all actions for blogpost ``13``,
        *``'blogpost:view,create,edit:*'``, granting a user permission to ``view``,
                                            ``create``, or ``edit`` *any* blogpost
        *``'blogpost:*:*'``, granting a user permission to perform *any* action on *any* blogpost
    To perform checks against these instance-level permissions, the application
    should include the instance ID in the permission check like so:::
        subject.is_permitted(['blogpost:edit:13'])
    """

    WILDCARD_TOKEN = '*'
    PART_DIVIDER_TOKEN = ':'
    SUBPART_DIVIDER_TOKEN = ','

    def __init__(self, wildcard_perm=None, parts=None):
        if wildcard_perm:
            parts = iter(self.partify(wildcard_perm))
            try:
                self.domain = next(parts)
                self.actions = next(parts)
                self.targets = next(parts)
            except StopIteration:
                raise ValueError("Permission cannot identify required parts from string")
        else:
            self.domain = {parts.get('domain', self.WILDCARD_TOKEN)}
            self.actions = set(parts.get('actions', self.WILDCARD_TOKEN))
            self.targets = set(parts.get('targets', self.WILDCARD_TOKEN))

    def partify(self, wildcard_perm):
        return [set(a.strip() for a in y.split(self.SUBPART_DIVIDER_TOKEN))
                for y in [x[0] if x[0] else x[1]
                          for x in itertools.zip_longest(
                    wildcard_perm.split(self.PART_DIVIDER_TOKEN),
                    [self.WILDCARD_TOKEN] * 3)]
                ]

    def implies(self, permission):
        if self.domain != {self.WILDCARD_TOKEN}:
            if self.domain != permission.domain:
                return False

        if self.actions != {self.WILDCARD_TOKEN}:
            if not self.actions >= permission.actions:
                return False

        if self.targets != {self.WILDCARD_TOKEN}:
            if not self.actions >= permission.actions:
                return False

        return True

    @staticmethod
    def get_domain(wildcard_perm):
        domain = wildcard_perm.split(Permission.PART_DIVIDER_TOKEN)[0].strip()
        if not domain:
            return Permission.WILDCARD_TOKEN
        return domain


class DefaultPermissionVerifier(BasePermissionVerifier):
    def is_permitted_from_str(self, required, assigned):
        required_perm = Permission(wildcard_perm=required)
        for perm_str in assigned:
            assigned_perm = Permission(wildcard_perm=perm_str)
            if assigned_perm.implies(required_perm):
                return True
        return False

    def is_permitted_from_json(self, required, assigned):
        required = Permission(wildcard_perm=required)
        the_parts = json.loads(assigned.decode('utf-8'))
        for parts in the_parts:
            assigned_perm = Permission(parts=parts)
            if assigned_perm.implies(required):
                return True
        return False


class DefaultAuthorizer(BaseAuthorizer):
    def __init__(self):
        self.realms = None

    def __repr__(self):
        return "DefaultAuthorizer(realms={0})".format(self.realms)

    def init_realms(self, realms):
        """
        :type realms: tuple
        """
        from .realm import BaseAuthorizingRealm
        self.realms = tuple(realm for realm in realms
                            if isinstance(realm, BaseAuthorizingRealm))

    def assert_realms_configured(self):
        if not self.realms:
            msg = ("Configuration error: No realms have been configured! "
                   "One or more realms must be present to execute an "
                   "authorization operation.")
            raise ValueError(msg)

    def _has_role(self, identifier, role_s):
        """
        :type identifier: str
        :type role_s: Set of String(s)
        """
        for realm in self.realms:
            # the realm's has_role returns a generator
            yield from realm.has_role(identifier, role_s)

    def _is_permitted(self, identifier, permission_s):
        """
        :type identifier: str
        :param permission_s: a collection of 1..N permissions
        :type permission_s: List of permission string(s)
        """
        for realm in self.realms:
            # the realm's is_permitted returns a generator
            yield from realm.is_permitted(identifier, permission_s)

    def is_permitted(self, identifier, permission_s, log_results=True):
        """
        :type identifier: str
        :param permission_s: a collection of 1..N permissions
        :type permission_s: List of permission string(s)
        :param log_results:  states whether to log results (True) or allow the
                             calling method to do so instead (False)
        :type log_results:  bool
        :returns: a set of tuple(s), containing the Permission and a Boolean
                  indicating whether the permission is granted
        """
        self.assert_realms_configured()

        results = collections.defaultdict(bool)  # defaults to False

        is_permitted_results = self._is_permitted(identifier, permission_s)

        for permission, is_permitted in is_permitted_results:
            # permit expected format is: (Permission, Boolean)
            # As long as one realm returns True for a Permission, that Permission
            # is granted.  Given that (True or False == True), assign accordingly:
            results[permission] = results[permission] or is_permitted

        results = set(results.items())
        return results

    def is_permitted_collective(self, identifier, permission_s, logical_operator):
        """
        :type identifier: str
        :param permission_s: a collection of 1..N permissions
        :type permission_s: List of Permission object(s) or String(s)
        :param logical_operator:  indicates whether all or at least one
                                  permission check is true (any)
        :type: any OR all (from python standard library)
        :returns: a Boolean
        """
        self.assert_realms_configured()

        # interim_results is a set of tuples:
        interim_results = self.is_permitted(identifier, permission_s,
                                            log_results=False)

        results = logical_operator(is_permitted for perm, is_permitted
                                   in interim_results)

        return results

    def check_permission(self, identifier, permission_s, logical_operator):
        """
        :type identifier: str
        :param permission_s: a collection of 1..N permissions
        :type permission_s: List of Permission objects or Strings
        :param logical_operator:  indicates whether all or at least one
                                  permission check is true (any)
        :type: any OR all (from python standard library)
        :raises UnauthorizedException: if any permission is unauthorized
        """
        self.assert_realms_configured()
        permitted = self.is_permitted_collective(identifier,
                                                 permission_s, logical_operator)
        if not permitted:
            msg = "Subject lacks permission(s) to satisfy logical operation"
            raise UnauthorizedException(msg)

    def has_role(self, identifier, role_s, log_results=True):
        """
        :type identifier: str
        :param role_s: a collection of 1..N Role identifiers
        :type role_s: Set of String(s)
        :param log_results:  states whether to log results (True) or allow the
                             calling method to do so instead (False)
        :type log_results:  bool
        :returns: a set of tuple(s), containing the role and a Boolean
                  indicating whether the user is a member of the Role
        """
        self.assert_realms_configured()

        results = collections.defaultdict(bool)  # defaults to False

        for role, has_role in self._has_role(identifier, role_s):
            # checkrole expected format is: (role, Boolean)
            # As long as one realm returns True for a role, a subject is
            # considered a member of that Role.
            # Given that (True or False == True), assign accordingly:
            results[role] = results[role] or has_role

        results = set(results.items())
        return results

    def has_role_collective(self, identifier, role_s, logical_operator):
        """
        :type identifier: str
        :param role_s: a collection of 1..N Role identifiers
        :type role_s: Set of String(s)
        :param logical_operator:  indicates whether all or at least one
                                  permission check is true (any)
        :type: any OR all (from python standard library)
        :returns: a Boolean
        """
        self.assert_realms_configured()

        # interim_results is a set of tuples:
        interim_results = self.has_role(identifier, role_s, log_results=False)

        results = logical_operator(has_role for role, has_role in interim_results)

        return results

    def check_role(self, identifier, role_s, logical_operator):
        """
        :type identifier: str
        :param role_s: 1..N role identifiers
        :type role_s:  a String or Set of Strings
        :param logical_operator:  indicates whether all or at least one
                                  permission check is true (any)
        :type: any OR all (from python standard library)
        :raises UnauthorizedException: if Subject not assigned to all roles
        """
        self.assert_realms_configured()
        has_role_s = self.has_role_collective(identifier, role_s, logical_operator)
        if not has_role_s:
            msg = "Subject does not have role(s) assigned."
            raise UnauthorizedException(msg)
