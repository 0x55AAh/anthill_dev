import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from admin import models


class Query(graphene.ObjectType):
    hello = graphene.String(description='A typical hello world')

    def resolve_hello(self, info):
        return 'World'


schema = graphene.Schema(query=Query)
