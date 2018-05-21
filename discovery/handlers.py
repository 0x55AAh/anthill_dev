from anthill.framework.handlers import RequestHandler, JSONHandlerMixin
import json


class RegisterService(JSONHandlerMixin, RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    async def get(self):
        """List requests for register requested service"""
        try:
            data = await self.application.get_requests_for_register_service()
            self.write(data)
        except Exception as e:
            self.write({'error': str(e)})

    async def post(self, name):
        """Create new request for register requested service"""
        networks = self.get_argument('networks')
        try:
            request_id = await self.application.create_request_for_register_service(
                name, json.loads(networks))
            self.write({'request_id': request_id})
        except Exception as e:
            self.write({'error': str(e)})

    async def put(self):
        """Accept request for register requested service"""
        request_id = self.get_argument('request_id')
        try:
            service_name, networks = await self.application.get_request_for_register_service(request_id)
            self.write({service_name: networks})
        except Exception as e:
            self.write({'error': str(e)})

    async def delete(self):
        """Discard request for register requested service"""
        request_id = self.get_argument('request_id')
        try:
            await self.application.delete_request_for_register_service(request_id)
        except Exception as e:
            self.write({'error': str(e)})
