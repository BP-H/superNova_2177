class Column:
    def __init__(self, *args, **kwargs):
        pass

class Integer:
    pass

class String:
    pass

class Text:
    pass

class Boolean:
    pass

class DateTime:
    pass

class ForeignKey:
    def __init__(self, *args, **kwargs):
        pass

class Table:
    def __init__(self, *args, **kwargs):
        pass

class Float:
    pass

class JSON:
    pass

class Session:
    pass

class IntegrityError(Exception):
    pass

def create_engine(*args, **kwargs):
    return None

def sessionmaker(*args, **kwargs):
    def maker(*margs, **mkwargs):
        return Session()
    return maker

def relationship(*args, **kwargs):
    return None

def declarative_base():
    class Base:
        pass
    return Base

class func:
    pass
