import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from store import models


class RootQuery(graphene.ObjectType):
    pass


# noinspection PyTypeChecker
schema = graphene.Schema(query=RootQuery)
