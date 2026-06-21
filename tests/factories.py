from copy import deepcopy


def make_from[Entity](obj: Entity, **kwargs) -> Entity:
    new_obj = deepcopy(obj)
    for key, value in kwargs.items():
        if not hasattr(obj, key):
            raise AttributeError(f"Object {obj.__class__.__name__} has no attribute {key}")
        setattr(new_obj, key, deepcopy(value))
    return new_obj