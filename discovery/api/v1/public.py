import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from discovery import models


class Query(graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
