import functools


class SessionAPI:
    def __call__(self):
        """Decorator marks function as an session api method."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator


session_api = SessionAPI()
