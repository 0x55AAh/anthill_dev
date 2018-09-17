import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from exec import models


class RootQuery(graphene.ObjectType):
    pass


schema = graphene.Schema(query=RootQuery)
