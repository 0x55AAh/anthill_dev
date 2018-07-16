import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from profile import models


PAGINATED_BY = 50


class Profile(SQLAlchemyObjectType):
    """Profile model entity."""
    class Meta:
        model = models.Profile


class RootQuery(graphene.ObjectType):
    """Api root query."""
    profiles = graphene.List(Profile)

    def resolve_profiles(self, info, page=None, **kwargs):
        request = info.context['request']
        query = Profile.get_query(info)
        pagination_kwargs = {
            'page': page,
            'per_page': PAGINATED_BY,
            'max_per_page': PAGINATED_BY
        }
        items = query.pagination(request, **pagination_kwargs).items
        return items


schema = graphene.Schema(query=RootQuery)
