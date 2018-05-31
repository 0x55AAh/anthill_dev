from anthill.framework.utils.crypto import get_random_string
import random


def get_random_secret_key():
    """
    Return a 50 character random string usable as a SECRET_KEY setting value.
    """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_random_string(50, chars)


def get_random_color():
    colors = [
        'primary', 'danger', 'success', 'warning', 'info',
        'pink', 'violet', 'purple', 'indigo', 'blue', 'teal',
        'green', 'orange', 'brown', 'grey', 'slate'
    ]
    return random.choice(colors)
