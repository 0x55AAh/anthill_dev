from anthill.framework.utils.asynchronous import thread_pool_exec as future_exec
from .core import as_internal, InternalAPI
from typing import Optional


@as_internal()
def test(api_: InternalAPI, **options):
    return {'method': 'test', 'service': api_.service.name}


@as_internal()
def ping(api_: InternalAPI, **options):
    return {'message': 'pong', 'service': api_.service.name}


@as_internal()
def doc(api_: InternalAPI, **options):
    return {'methods': ', '.join(api_.methods)}


@as_internal()
def get_service_metadata(api_: InternalAPI, **options):
    return api_.service.app.metadata


@as_internal()
def reload(api_: InternalAPI, **options):
    import tornado.autoreload
    # noinspection PyProtectedMember
    tornado.autoreload._reload()


@as_internal()
async def update(api_: InternalAPI, version: Optional[str], **options):
    update_manager = api_.service.update_manager
    await update_manager.update(version)


def get_model_class(model_name: str):
    from anthill.framework.apps import app
    return app.get_model(model_name)


async def get_model_query(model_name: str, page: int = 1, page_size: int = 0,
                          in_list: Optional[list] = None, identifier_name: str = 'id',
                          **filter_data):
    model = get_model_class(model_name)
    query = model.query.filter_by(**filter_data)
    if page_size:
        query = query.limit(page_size)
        if page:
            query = query.offset((page - 1) * page_size)
    if in_list:
        identifier = getattr(model, identifier_name)
        query = query.filter(identifier.in_(in_list))
    return query


async def get_model_object(model_name: str, object_id: str, identifier_name: str = 'id'):
    query = await get_model_query(model_name, **{identifier_name: object_id})
    return await future_exec(query.one)


@as_internal()
async def object_version(api_: InternalAPI, model_name: str, object_id: str, version: int,
                         identifier_name: str = 'id', **options):
    obj = await get_model_object(model_name, object_id, identifier_name)
    return await future_exec(obj.versions.get, version)


@as_internal()
async def object_recover(api_: InternalAPI, model_name: str, object_id: str, version: int,
                         identifier_name: str = 'id', **options) -> None:
    obj = await get_model_object(model_name, object_id, identifier_name)
    version = await future_exec(obj.versions.get, version)
    await future_exec(version.revert)


@as_internal()
async def object_history(api_: InternalAPI, model_name: str, object_id: str,
                         identifier_name: str = 'id', **options):
    obj = await get_model_object(model_name, object_id, identifier_name)
    return obj.versions


@as_internal()
async def get_model(api_: InternalAPI, model_name: str, object_id: str,
                    identifier_name: str = 'id', **options):
    obj = await get_model_object(model_name, object_id, identifier_name)
    return obj.dump().data


@as_internal()
async def get_models(api_: InternalAPI, model_name: str,
                     filter_data: Optional[dict] = None, in_list: Optional[list] = None,
                     identifier_name: str = 'id', page: int = 1, page_size: int = 0,
                     **options):
    model = get_model_class(model_name)
    query = await get_model_query(
        model_name, page, page_size, in_list, identifier_name, **(filter_data or {}))
    objects = await future_exec(query.all)
    return model.dump_many(objects).data


@as_internal()
async def create_model(api_: InternalAPI, model_name: str, data: dict, **options):
    model = get_model_class(model_name)
    obj = await future_exec(model.create, **data)
    return obj.dump().data


@as_internal()
async def update_model(api_: InternalAPI, model_name: str, object_id: str, data: dict,
                       identifier_name: str = 'id', **options):
    obj = await get_model_object(model_name, object_id, identifier_name)
    await future_exec(obj.update, **data)
    return obj.dump().data


@as_internal()
async def delete_model(api_: InternalAPI, model_name: str, object_id: str,
                       identifier_name: str = 'id', **options):
    obj = await get_model_object(model_name, object_id, identifier_name)
    await future_exec(obj.delete)


@as_internal()
def model_fields(api_: InternalAPI, model_name: str, **options):
    from sqlalchemy import inspect
    model = get_model_class(model_name)
    return inspect(model).columns.keys()
