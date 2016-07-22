__author__ = "Dhruv Pathak"


import cPickle
from django.core.cache import cache
import sys
import datetime
import logging
import time
from functools import wraps
from django.conf import settings
import traceback


logger = logging.getLogger(__name__)

class mDict(dict):
    pass

class mList(list):
    pass
    

def cache_result(cache_key = None,cache_kwarg_keys = None,seconds = 900,cache_filter=lambda x:True):
    def set_cache(f):
        @wraps(f)
        def x(*args, **kwargs):
            if settings.USE_CACHE is not True:
                result = f(*args, **kwargs)
                return result
            if cache_key is None:
                if cache_kwarg_keys is not None:
                    if len(cache_kwarg_keys) == 0 or len(args) > 0:
                        raise Exception("cache_kwarg_keys mode needs set kwargs,args should be empty")
                    kwargs_part_dict = {k:v for k,v in kwargs.items() if k in cache_kwarg_keys}
                    final_cache_key = "{0}#{1}#{2}".format(str(f.__module__),str(f.__name__),hash(cPickle.dumps(kwargs_part_dict,0)))

                else:
                    final_cache_key =  "{0}#{1}".format(str(f.__module__),str(f.__name__))
                    final_cache_key +=  "#" + hash(cPickle.dumps(args,0)) if len(args)> 0 else ''
                    final_cache_key +=  "#" + hash(cPickle.dumps(kwargs,0)) if len(kwargs)> 0 else ''
            else:
                final_cache_key = "{0}#{1}#{2}".format(f.__module__,f.__name__,cache_key)

            try:
                result = cache.get(final_cache_key)
            except Exception,e:
                result = None
                if settings.DEBUG is True:
                    raise
                else:
                    logger.exception("Cache get failed,k::{0},ex::{1},ex::{2}".format(final_cache_key,str(e),traceback.format_exc()))

            if result is not None and cache_filter(result) is False:
                result = None
                logger.error("Cache had invalid result:{0},not returned".format(result))

            if result is None: # result not in cache
                result = f(*args, **kwargs)
                if isinstance(result,(mDict,mList)):
                    result.ot = int(time.time())
                if cache_filter(result) is True:
                    try:
                        cache.set(final_cache_key, result, seconds)
                    except Exception,e:
                        if settings.DEBUG is True:
                            raise
                        else:
                            logger.exception("Cache set failed,k::{0},ex::{1},ex::{2},dt::{3}".format(final_cache_key,str(e),traceback.format_exc(),str(result)[0:100],))
                else:
                    logger.error("Result :{0} failed,not cached".format(result))

            else: # result was from cache
                if isinstance(result,(mDict,mList)):
                    result.src = 'C'
            return result
        return x
    return set_cache
    
    def get_nested_ordered_dict(input_dict):
        res = OrderedDict()
        for k, v in sorted(input_dict.items()):
            if isinstance(v, dict):
                res[k] = get_nested_ordered_dict(v)
            else:
                res[k] = v
        return res
