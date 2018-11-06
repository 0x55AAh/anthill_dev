from anthill.framework.auth import get_user_model
from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene


PAGINATED_BY = 50


class User(SQLAlchemyObjectType):
    """User model entity."""
    class Meta:
        model = get_user_model()


class RootQuery(graphene.ObjectType):
    """Api root query."""
    users = graphene.List(User)

    @staticmethod
    def resolve_users(root, info, page=None, **kwargs):
        request = info.context['request']
        query = User.get_query(info)
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

    @staticmethod
    def mutate(root, info, username, password):
        user = get_user_model()(username=username)
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

    @staticmethod
    def mutate(root, info, id, username=None, password=None):
        user = get_user_model().query.get(id)
        if username is not None:
            user.username = username
        if password is not None:
            user.set_password(password)
        user.save()

        return UpdateUser(user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()


# noinspection PyTypeChecker
schema = graphene.Schema(query=RootQuery, mutation=Mutation)
