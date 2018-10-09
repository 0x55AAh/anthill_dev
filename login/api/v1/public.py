import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from login import models


PAGINATED_BY = 50


class User(SQLAlchemyObjectType):
    """User model entity."""
    class Meta:
        model = models.User


class RootQuery(graphene.ObjectType):
    """Api root query."""
    users = graphene.List(User)

    def resolve_users(self, info, page=None, **kwargs):
        request = info.context['request']
        query = user.get_query(info)
        pagination_kwargs = {
            'page': page,
            'per_page': PAGINATED_BY,
            'max_per_page': PAGINATED_BY
        }
        items = query.pagination(request, **pagination_kwargs).items
        return items


class CreateUser(graphene.Mutation):
    """Create user."""
    user = graphene.Field(User)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, password):
        user = models.User(username=username)
        user.set_password(password)
        user.save()

        return CreateUser(user=user)


class UpdateUser(graphene.Mutation):
    """Update user."""
    user = graphene.Field(User)

    class Arguments:
        id = graphene.ID()
        username = graphene.String()
        password = graphene.String()

    def mutate(self, info, id, username=None, password=None):
        user = models.User.query.get(id)
        if username is not None:
            user.username = username
        if password is not None:
            user.set_password(password)
        user.save()

        return UpdateUser(user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()


schema = graphene.Schema(query=RootQuery, mutation=Mutation)
