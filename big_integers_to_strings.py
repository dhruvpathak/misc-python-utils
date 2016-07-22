def i64_to_str(obj, outformat=None):
    """Converts 64 bit integers into strings to make javascript friendly json, when Javascript parses
    json, the 64 bit integers get converted into float,which are prone to rounding errors, this
    utility method converts those integers to string representation.

    Args:
        obj (object) : The object containing data e.g dict or a list
        outformat (str) : If format string is provided,the matching data is formatted
                          according to this string

    Returns:
       obj : Same object with 64 bit integers converted to string

    Examples:

        >>> i64_to_str({'name':'John','data':{'types':[2,3,4],'ids':[2820046943342890302,4563046943342890302]}})
        {'name':'John','data':{'types':[2,3,4],'ids':["2820046943342890302","4563046943342890302"]}}

    """
    if isinstance(obj, list):
        return [i64_to_str(x, outformat=outformat) for x in obj]
    if isinstance(obj, dict):
        return {i64_to_str(k, outformat=outformat): i64_to_str(v, outformat=outformat) for k, v in obj.items()}
    if isinstance(obj, (int, long)) and obj >= 2**32:
        if outformat is not None:
            return outformat.format(obj)
        else:
            return str(obj)
    return obj
