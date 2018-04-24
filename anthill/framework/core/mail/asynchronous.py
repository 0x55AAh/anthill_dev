"""
Async tools for sending email.
"""
from anthill.framework.utils.asynchronous import thread_pool_exec
from . import (
    send_mail as _send_mail,
    send_mass_mail as _send_mass_mail,
    mail_admins as _mail_admins,
    mail_managers as _mail_managers,
    get_connection as _get_connection
)

__all__ = [
    'send_mail', 'send_mass_mail', 'mail_admins',
    'mail_managers', 'get_connection'
]

send_mail = thread_pool_exec.as_future(_send_mail)
send_mass_mail = thread_pool_exec.as_future(_send_mass_mail)
mail_admins = thread_pool_exec.as_future(_mail_admins)
mail_managers = thread_pool_exec.as_future(_mail_managers)
get_connection = thread_pool_exec.as_future(_get_connection)
