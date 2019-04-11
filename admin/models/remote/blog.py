from anthill.platform.remote_models import remote_model_factory


__all__ = ['BlogPost', 'BlogCategory']


BlogPost = remote_model_factory('blog.Post')
BlogCategory = remote_model_factory('blog.Category')
