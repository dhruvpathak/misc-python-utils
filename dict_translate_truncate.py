
def translate_dict_keys(orig_dict, translate_map, nested=False, ignore_extra=False):
    """ Translates a dictionary's keys according to provided mapping , can also be
        used to prune a dictionary by discarding keys of dictionary which are not mapped

    Args:
        orig_dict (object) : The original dict to be translated
        translate_map (object) : A dict containing key-value pairs of translations
        nested ( Optional[bool] ) : If true, the translation is done on subkeys as well
        ignore_extra ( Optional[bool] ) : If true, all keys which are not present in translate_map
                                          will be discarded

    Returns:
       obj : Object with dict keys translated or rejected

    Examples:

        >>> translate_dict_keys({'name':'geneva','country':'switzerland'},{'name':'n','country':'cnt'})
            {'n':'geneva','cnt':'switzerland'}
        >>> translate_dict_keys({'name':'geneva','country':'switzerland'},{'name':'n'},ignore_extra=True)
            {'n':'geneva'}

    """
    translated_dict = {}
    for k, v in orig_dict.iteritems():
        value = v
        if nested is True:
            if isinstance(v, dict):
                value = translate_dict_keys(v, translate_map, nested, ignore_extra)
            elif isinstance(v, list):
                value = [translate_dict_keys(x, translate_map, nested, ignore_extra) if isinstance(x, dict) else x for x in v]

        if ignore_extra is False:
            translated_dict[translate_map.get(k, k)] = value
        else: # ignore the keys not present in translate map
            if k in translate_map:
                translated_dict[translate_map[k]] = value
    return translated_dict
