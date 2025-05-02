def get_nested_value(data, key_path):
    """
    Utility function to extract nested values from a dictionary using dot-separated keys.
    """
    keys = key_path.split('.')
    value = data
    for key in keys:
        if value is None:
            break
        value = value.get(key)
    return value
