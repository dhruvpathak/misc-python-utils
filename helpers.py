__author__ = 'Dhruv Pathak'

import urllib2
import urllib
from django.conf import settings
import logging
from functools import wraps
import time
import difflib
import jellyfish
import re
import base64


logger = logging.getLogger("common")



def url_fetch(url, params={}, config={}):
    """A utility to fetch data from a url

    Args:
        url (str) : url from which data has to be fetched
        params (dict) : dict containing request parameters (GET or POST)
        config (dict) : dict containing following configuration variables:

            **method** (str): "GET" or "POST". Default: "GET"

            gzip** (bool) : Flag to specify if accepting gzip content is allowed. Default: False

            **timeout** (int) : Timeout value (in seconds). Default: No timeout

            **use_proxy** (bool): Flag to specify if proxy is to be used. Default: False

            **auth** (dict): dict containing basic auth username and password

            **username** (str) : basic auth username

            **password** (str): basic auth password

    Returns:

        dict : dict containing following keys:

            **success**: True for cases when Http request was successful, False in all other cases.

            **data**: Data returned by the call

            **error**: Contains the error message in case any exception is raised

            **content_encoding**: content encoding of the response

    """
    defaults = {'method': 'GET'}
    defaults.update(config)
    config = defaults
    try:
        if config['method'] == "POST":
            request = urllib2.Request(url, data=urllib.urlencode(params))
        else:
            request = urllib2.Request(url + "?" + urllib.urlencode(params)) if len(params.keys()) > 0 else urllib2.Request(url)

        if config.get("auth") is not None and config["auth"].get("password") is not None and config["auth"].get("username"):
            base64string = base64.encodestring('%s:%s' % (config["auth"]["username"], config["auth"]["password"])).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)
        if config.get('gzip') is True:
            request.add_header('Accept-Encoding', 'gzip, deflate, sdch')

        for header_key,header_val in config.get("headers",{}).items():
            request.add_header(header_key,header_val)

        if settings.EXTERNAL_REQUEST_SETTINGS['proxy_enabled'] is True and config.get('use_proxy',True) is True:
            opener = urllib2.build_opener(urllib2.ProxyHandler(settings.EXTERNAL_REQUEST_SETTINGS['proxy_config']))
            if config.get('timeout') is not None:
                resp_data = opener.open(request, timeout=config["timeout"])
            else:
                resp_data = opener.open(request)
        else:
            if config.get('timeout') is not None:
                resp_data = urllib2.urlopen(request, timeout=config["timeout"])
            else:
                resp_data = urllib2.urlopen(request)

        content_encoding = resp_data.info().getheader('Content-Encoding')
        return {'success': True, 'data': resp_data.read(), 'content_encoding': content_encoding}

    except Exception, e:
        try:
            return {"success": False, "data": str(e.read()), "error": str(e)}
        except:
            return {'success': False, 'data': str(e)}



def env_run_filter_decorator(allowed_environment="PROD"):
    """ A decorated method will only run in the allowed_environment.
        The current environment of the app can be retreived
        in multiple ways .e.g environment variables of the OS,
        settings or configurations, this method reliese on a django
        example using its settings file.
    """
    def func_decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            do_nothing = lambda x: None
            if settings.ENVIRONMENT.lower() != allowed_environment.lower():
                logger.debug("Current environment:{0}, Task {1} can only be run in: {2} environment,skipped.".format(settings.ENVIRONMENT, f.__name__, allowed_environment))
                return do_nothing
            ret_func = f(*args, **kwargs)
            return ret_func
        return wrapped
    return func_decorator


def find_string_similarity(first_str, second_str, normalized=False, ignore_list=[]):
    """ Calculates matching ratio between two strings

    Args:
        first_str (str) : First String
        second_str (str) : Second String
        normalized (bool) : if True ,method removes special characters and extra whitespace
                            from strings then calculates matching ratio
        ignore_list (list) : list has some characters which has to be substituted with "" in string


    Returns:
       Float Value : Returns a matching ratio between 1.0 ( most matching ) and 0.0 ( not matching )
                    using difflib's SequenceMatcher and and jellyfish's jaro_winkler algorithms with
                    equal weightage to each

    Examples:
        >>> find_string_similarity("hello world","Hello,World!",normalized=True)
        1.0
        >>> find_string_similarity("entrepreneurship","entreprenaurship")
        0.95625
        >>> find_string_similarity("Taj-Mahal","The Taj Mahal",normalized= True,ignore_list=["the","of"])
        1.0
    """
    first_str = process_str_for_similarity_cmp(first_str, normalized=normalized, ignore_list=ignore_list)
    second_str = process_str_for_similarity_cmp(second_str, normalized=normalized, ignore_list=ignore_list)
    match_ratio = (difflib.SequenceMatcher(None, first_str, second_str).ratio() + jellyfish.jaro_winkler(unicode(first_str), unicode(second_str)))/2.0
    return match_ratio


def process_str_for_similarity_cmp(input_str, normalized=False, ignore_list=[]):
    """ Processes string for similarity comparisons , cleans special characters and extra whitespaces
        if normalized is True and removes the substrings which are in ignore_list)

    Args:
        input_str (str) : input string to be processed
        normalized (bool) : if True , method removes special characters and extra whitespace from string,
                            and converts to lowercase
        ignore_list (list) : the substrings which need to be removed from the input string

    Returns:
       str : returns processed string

    """
    for ignore_str in ignore_list:
        input_str = re.sub(r'{0}'.format(ignore_str), "", input_str, flags=re.IGNORECASE)

    if normalized is True:
        input_str = input_str.strip().lower()
        #clean special chars and extra whitespace
        input_str = re.sub("\W", "", input_str).strip()

    return input_str




def record_time(f):
    """ Records and logs the time taken by a function
    Args:
        f (method) : method for which ,time has to be logged

    Returns:
       time: returns time taken by a function

    Examples:
         >>>@record_time
         >>>def some_method():

    """
    def time_recorder(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        logger.info("Time recorder| Method: {0}.{1} Time: {2}".format(f.__module__, f.__name__, time.time() - start_time))
        return result
    return time_recorder