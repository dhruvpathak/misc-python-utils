from collections import OrderedDict

def get_nested_ordered_dict(input_dict):
    """ orders a dict recursively so that each subdict is also ordered,
        this utility can help in generating equal hash for equal dicts for example
        irrespective of inner order of keys

    Args:
        input_dict (dict) : The input unordered dict
        

    Returns:
       dict : dict whose keys are ordered, and all the subdicts are ordered as well

    """
    res = OrderedDict()
    for k, v in sorted(input_dict.items()):
        if isinstance(v, dict):
            res[k] = get_nested_ordered_dict(v)
        else:
            res[k] = v
    return res
