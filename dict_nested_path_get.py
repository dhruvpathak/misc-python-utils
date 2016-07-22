
def nested_path_get(obj, path_str, strict=True, mode='GET', default_return_value=None):
    """ gets value from an object though a provided path string, this is really 
    useful for nested dicts obtained from data sources like mongodb

    Args:
        obj (obj) : The object containing the data
        path_str ( str) : Dotted path to the target, e.g. mykey.mysecondary_key.my_tertiarykey
        strict (bool) : If True, method will throw an exception if no value exists at the provided
                        path i.e. the path is invalid. Else, the method returns None if there
                        is no value at provided path

    Returns:
        Value at the provided nested path

    Examples:
        >>> obj = { 'success':True,'data':{ 'rank':'student','age':20 }}
        >>> nested_path_get(obj,'data.rank')
        'student'
        >>> nested_path_get(obj,'data.profession', strict=False)
        # Returns None
        >>> nested_path_get(obj,'data.profession', strict=True)
        # raises exception

    """
    nested_keys = path_str.split(".")
    for index, key in enumerate(nested_keys):
        if re.match(r'^[-\w\|]+(\.[-\w\|]+)?(\.[-\w\|]+)?(\.[-\w\|]+)?$', key) is None:
            raise Exception("{0} is invalid path str".format(key))

        try:
            if mode == "POP" and index == len(nested_keys)-1:
                #if pop is required, pop object at last nested key level
                obj = obj.pop(key, default_return_value)
            else:
                obj = obj[key]
        except Exception as e:
            if strict is True:
                raise
            else:
                return default_return_value
    return obj
