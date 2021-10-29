# TWITTER API INTERACTION FUNCTIONS

import requests
import toml
from os import path
import sys

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


path_to_secrets_file = '../../secrets.toml' 

def get_bearer_token():
    """
    Fetches the bearer token from the secrets TOML file.
    
    Returns
    ------
    Bearer token:   str
                    Token to pass to api for authorization
    """
    if path.exists(path_to_secrets_file):
        try:
            secrets = toml.load(path_to_secrets_file)['twitter']
        except KeyError:
            # assume that Twitter credentials have still been included
            secrets = toml.load(path_to_secrets_file)
    else:
        # No file found
        print(f"Error: You need to save your bearer token in the file `{path_to_secrets_file}`.")
        sys.exit()
    try:
        return secrets['BEARER_TOKEN']
    except KeyError:
        print("You need to include a BEARER_TOKEN key in your secrets.toml file.")
        sys.exit()

def bearer_oauth(r):
    """
    This function authorises the bearer and was provided by Twitter
    Sets the request headers for authorization and returns.

    Params
    ------
    r:          request object
                To be sent to the Twitter API

    Returns
    -------
    r:          request object
                Returned after setting headers (r.headers)
    """
    r.headers["Authorization"] = f"Bearer {get_bearer_token()}"
    # try this without the User agent? If still works - note that this is a nice to have
    # also explain what it is :)
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def set_up_adapter():
    """
    Creates a requests.Session() object and configures it to
    apply a retry strategy: 3 total retries on statuses 
    429, 502, 503, and 504. Time lag between retries increases.
    Based on https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/

    Returns
    -------
    http:       requests.Session object
                Has all the methods of the requests package as
                well as parameters that persist across requests.
    """
    retry_strategy = Retry(
        total = 3, # number of retries to attempt
        status_forcelist=[429, 500, 502, 503, 504], # status codes that will force a retry
        backoff_factor=1, # determines time lag between retries (increases exponentially)
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    return http


def connect_to_endpoint(http, url, params):
    """
    This function is what connects us to the Twitter API so that we can request data

    Params
    ------
    http:       requests.Session object
                Has all the methods of the requests package as
                well as parameters that persist across requests.

    url:        str
                The endpoint to connect to

    params:     Dict
                The request parameters in dictionary format

    Returns
    ------
    response.json()     json
                        The response from the API in JSON format
    """
    response = http.get(
            url, 
            auth=bearer_oauth, 
            params=params
    )
    if response.status_code != 200:
        # TODO wrap this in a retry
        # TODO error handling - more specific messages for different codes
        raise Exception(response.status_code, response.text)
    return response.json()