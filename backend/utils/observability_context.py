import contextvars


request_id_var = contextvars.ContextVar("request_id", default=None)


def get_request_id():
    return request_id_var.get()


def set_request_id(request_id):
    return request_id_var.set(request_id)


def reset_request_id(token):
    request_id_var.reset(token)
