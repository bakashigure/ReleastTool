""" utils
"""

def singleton(cls):
    """
    Singleton decorator

    Args :
        * ``cls (object)`` : class to decorate

    Returns :
        * ``object`` : decorated class
    """
    def wrapper(*args, **kwargs):
        if not hasattr(cls, '__instance'):
            setattr(cls, '__instance', cls(*args, **kwargs))
            wrapper.clean = lambda : delattr(cls, '__instance')
        return getattr(cls, '__instance')
    return wrapper
