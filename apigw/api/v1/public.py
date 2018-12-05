from graphene_sqlalchemy import SQLAlchemyObjectType
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import to_unicode
from anthill.framework.apps import app
from apigw import models
import graphene
import json


class RootQuery(graphene.ObjectType):
    """Api root query."""

    request = graphene.JSONString(
        service_name=graphene.String(default_value=app.label),
        query=graphene.String()
    )

    @staticmethod
    async def resolve_request(root, info, service_name, query):
        handler = info.context['handler']
        try:
            metadata = next(filter(
                lambda x: x['name'] == service_name, handler.settings['services_meta']))
        except StopIteration:
            return {}
        else:
            data = await AsyncHTTPClient().fetch(
                metadata['public_api_url'],
                method=handler.request.method,
                body=json.dumps({'query': query}),
                headers=handler.request.headers
            )
            return json.loads(to_unicode(data.body))


# noinspection PyTypeChecker
schema = graphene.Schema(query=RootQuery)
