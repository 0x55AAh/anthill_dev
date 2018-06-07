import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from admin import models


class RootQuery(graphene.ObjectType):
    hello = graphene.String(description='A typical hello world')

    def resolve_hello(self, info):
        return 'World'


class Mutation(graphene.ObjectType):
    pass


schema = graphene.Schema(query=RootQuery)
