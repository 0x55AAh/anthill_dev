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


class CreateProfile(graphene.Mutation):
    """Create profile."""
    profile = graphene.Field(Profile)

    class Arguments:
        user_id = graphene.String(required=True)
        payload = graphene.String(required=True)

    @staticmethod
    def mutate(root, info, user_id, payload):
        profile = models.Profile(user_id=user_id, payload=payload)
        profile.save()

        return CreateProfile(profile=profile)


class UpdateProfile(graphene.Mutation):
    """Update profile."""
    profile = graphene.Field(Profile)

    class Arguments:
        user_id = graphene.ID()
        payload = graphene.String()

    @staticmethod
    def mutate(root, info, user_id, payload=None):
        profile = models.Profile.query.filter_by(user_id=user_id).first()
        if payload is not None:
            profile.payload = payload
        profile.save()

        return UpdateProfile(profile=profile)


class Mutation(graphene.ObjectType):
    create_profile = CreateProfile.Field()
    update_profile = UpdateProfile.Field()


# noinspection PyTypeChecker
schema = graphene.Schema(query=RootQuery, mutation=Mutation)
