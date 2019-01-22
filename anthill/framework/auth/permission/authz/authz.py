from . import abcs
import itertools
import logging
import json


class Permission:
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
        *``'blogpost:view,create,edit:*'``, granting a user permission to ``view``, ``create``, or ``edit`` *any* blogpost
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
            self.domain = set([parts.get('domain', self.WILDCARD_TOKEN)])
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


class DefaultPermissionVerifier:
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


class ModularRealmAuthorizer(abcs.Authorizer):
    def is_permitted(self, identifiers, permission_s):
        pass

    def is_permitted_collective(self, identifiers, permission_s, logical_operator):
        pass

    def check_permission(self, identifiers, permission_s, logical_operator):
        pass

    def has_role(self, identifiers, role_s):
        pass

    def has_role_collective(self, identifiers, role_s, logical_operator):
        pass

    def check_role(self, identifiers, role_s, logical_operator):
        pass
