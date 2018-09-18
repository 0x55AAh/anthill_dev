from anthill.platform.api.internal import RequestTimeoutError
from anthill.platform.utils.internal_api import internal_request
from graphene_sqlalchemy import SQLAlchemyObjectType
from anthill.framework.apps import app
from admin import models
import graphene


class ServiceMetadata(graphene.ObjectType):
    """Service metadata entry."""

    title = graphene.String()
    description = graphene.String()
    icon_class = graphene.String()
    color = graphene.String()
    version = graphene.String()

    def __lt__(self, other):
        return self.title < other.title


class RootQuery(graphene.ObjectType):
    """Api root query."""

    services_metadata = graphene.List(ServiceMetadata, description='List of services metadata.')

    # noinspection PyMethodMayBeStatic
    async def resolve_services_metadata(self, info, **kwargs):
        services_metadata = []
        try:
            services = await internal_request('discovery', method='get_services')
        except RequestTimeoutError:
            pass
        else:
            for name in services.keys():
                if name == app.name:
                    # Skip current application
                    continue
                try:
                    metadata = await internal_request(name, method='get_service_metadata')
                    services_metadata.append(ServiceMetadata(**metadata))
                except RequestTimeoutError:
                    pass
            services_metadata.sort()
        return services_metadata


class Mutation(graphene.ObjectType):
    pass


schema = graphene.Schema(query=RootQuery)
