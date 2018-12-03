import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from tornado.httpclient import AsyncHTTPClient
from apigw import models


class RootQuery(graphene.ObjectType):
    pass


# noinspection PyTypeChecker
schema = graphene.Schema(query=RootQuery)
