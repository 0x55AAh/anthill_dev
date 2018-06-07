import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from login import models


class RootQuery(graphene.ObjectType):
    pass


schema = graphene.Schema(query=RootQuery)
