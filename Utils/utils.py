def flatten_dict(d, parent_key='', sep='_'):
    if d is None:
        return {}
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, (list, tuple)):
            items.append((new_key, v))
        else:
            items.append((new_key, v))
    return dict(items)

# Export the flatten_dict function
__all__ = ['flatten_dict']
