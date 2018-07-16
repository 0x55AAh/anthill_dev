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


schema = graphene.Schema(query=RootQuery)
