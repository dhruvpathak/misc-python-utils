__author__ = 'Dhruv Pathak'

"""Some methods for common data manipulation or processing"""

import random
from itertools import islice
import re
import logging
import time
from collections import OrderedDict

logger = logging.getLogger(__name__)



def nested_path_get(obj, path_str, strict=True, mode='GET', default_return_value=None):
    """ Gets value from an object though a provided path string, useful in
    retreving data from nested dictionaries, for example a document retreived from
    MongoDB.

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
            student
        >>> nested_path_get(obj,'data.profession', strict=False)
        # Returns None
        >>> nested_path_get(obj,'data.profession', strict=True )
        # raises exception
        >>> nested_path_get(obj,'data.profession', strict=False, default_return_value='doctor' )
            doctor

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


def i64_to_str(obj, outformat=None):
    """Converts 64 bit integers into strings to make javascript friendly json

    Args:
        obj (object) : The object containing data e.g dict or a list
        outformat (str) : If format string is provided,the matching data is formatted
                          according to this string, for example to make 64 bit integer
                          strings friendly to default excel or csv sheets format

    Returns:
       obj : Same object with 64 bit integers converted to string

    Examples:

        >>> i64_to_str({'name':'delhi','data':{'types':[2,3,4],'ids':[2820046943342890302,4563046943342890302]}})
        {'name':'delhi','data':{'types':[2,3,4],'ids':["2820046943342890302","4563046943342890302"]}}

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

def translate_dict_keys(orig_dict, translate_map, nested=False, ignore_extra=False):
    """ Translates a dictionary's keys according to provided mapping , can also be
        used to discard parts of dictionary which are not mapped

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



def get_nested_ordered_dict(input_dict):
    """sorts a dict recursively and converts each dict to an Ordered Dict"""
    res = OrderedDict()
    for k, v in sorted(input_dict.items()):
        if isinstance(v, dict):
            res[k] = get_nested_ordered_dict(v)
        else:
            res[k] = v
    return res



def iteration_chunks(iterable, n, chunk_type=tuple):
    """Yields chunks of any iterable .e.g 5 chunks of size 20 each for a 100 length iterable

    Args:
        iterable : Iterable like dict,list,tuple etc
        n (int): size of each chunk
        chunk_type ( Optional[type]) : Type of chunk to be returned, default is tuple

    Yields: Chunk of required size and type

    """
    it = iter(iterable)
    while True:
        chunk = tuple(islice(it, n)) if chunk_type is tuple else chunk_type(islice(it, n))
        if not chunk:
            return
        yield chunk


class mDict(dict):
    """a dummy class extending dict, to add custom attributes"""
    pass


class mList(list):
    """a dummy class extending list, to add custom attributes"""
    pass



def extract_bits_int64(num, index_start, length):
    """ extracts `length` bits starting from index_start in a 64 bit number

    Args:
        num(int): a 64 bit integer
        index_start : the starting index of the bits
        length : number of bits starting from index_start


    Returns:
       int: the number represented by those bits


    """
    total_bits = (1 << 64 - 1).bit_length()
    if (index_start >= 0 and index_start + length > total_bits) or (index_start < 0 and abs(index_start)+1 < length):
        return None
    mask = (1 << length) - 1
    mask_shift = (total_bits - index_start - length) if index_start >= 0 else (abs(index_start) + 1 - length)
    mask = mask << mask_shift
    result = (int(num) & mask) >> mask_shift
    return result




def dict_search_by_parts(dicts, dict_part):
    """Returns index of a dict in a list/iterator of dicts, if
       all keys and values of the subdictionary are found in that dict

    Args:
        dicts (list) : The list containing the dicts
        dict_part (dict) : The partial dict that is to be matched to the items
                        of dicts

    Returns:
       int : The first index of the dict which matches the partial input dict, None if
             nothing matches.

    Examples:

        >>> dicts = [ { 'id':3,'name':'John','age':23},{'id':5,'name':'Mary','age':22},{'id':9,'name':'Matt','age':25 } ]
        >>> dict_part = { 'id':5}
        >>> dict_search_by_parts(dicts,dict_part)
        1  # Index of {'id':5,'name':'Mary','age':22}

    """
    for index, current_dict in enumerate(dicts):
        # if this dict has all keys required and the values match
        if all(key in current_dict and current_dict[key] == val
               for key, val in dict_part.items()):
            return index
    return None




def csv_outformatter(data, transformations, flags):
    """

    Args:
        data: List of list of elements that represents the csv data
        transformations: The rules of transforming the data before generating the csv
        flags:encoding for the csv

    Returns: returns list of list of data of csv

    Examples:

    """
    sample_sublist_size = 100
    col_zip = [list(col) for col in zip(*data)]
    for trans in transformations:
        if trans.get("operation_on", "") == "column":
            pass
        elif trans.get("operation_on", "") == "data_type":
            for col in col_zip:
                matches_type = False
                sub_list = random.sample(col, min(sample_sublist_size, len(col)))
                if (float([isinstance(ele, trans['selector']) for ele in sub_list].count(True)) / len(sub_list)) > 0.4:
                    matches_type = True
                if matches_type is False:
                    continue
                if trans["op_name"] == "to_str":
                    if trans["args"].get("out_format", None) is not None:
                        col[:] = [trans["args"]["out_format"].format(col_ele) for col_ele in col[:]]
                    else:
                        col[:] = ["{0}".format(col_ele) for col_ele in col[:]]
        # apply global flags
    for flag in flags:
        if flag == "encoding":
            for col in col_zip:
                if flags["encoding"] == "ascii":
                    col[:] = [col_ele.encode('ascii', 'replace') if any([isinstance(col_ele, type_check) for type_check in [unicode]]) else col_ele for col_ele in col[:]]
                elif flags["encoding"] == "utf-8":
                    col[:] = [col_ele.encode('utf-8', 'replace') if any([isinstance(col_ele, type_check) for type_check in [unicode, str]]) else col_ele for col_ele in col[:]]
    return zip(*col_zip)



