from admin.handlers._base import UserTemplateServiceRequestHandler


class ServicesList(UserTemplateServiceRequestHandler):
    template_name = 'services-list.html'


class ServiceDetail(UserTemplateServiceRequestHandler):
    template_name = 'service-detail.html'
