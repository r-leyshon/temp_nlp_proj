"""
This script collects Tweets from the past week from the Twitter API,
stores them in a dataframe, and performs anonymisation steps such
as removing user IDs and usernames, before appending the dataframe to a .tsv file.
"""

import time
import re
import os
import pandas as pd
import numpy as np
from supporting_files.api_functions import set_up_adapter, connect_to_endpoint

def collect_tweets(url, parameters, total_to_collect, verbose):
    """
    Connect to endpoint and gather historical tweets using query parameters.
    
    Parameters:
    -----------
    url:            str
                    URL of endpoint to query
    parameters:     dict
                    Dictionary of query parameters
    max_tweets:     int
                    Maximum number of Tweets to collect
    verbose:        bool
                    If True, print updates on progress
                    
    Returns:
    ----------
    List of collected Tweets. Each Tweet is in dictionary format
    with keys 'id' (the ID of the Tweet) and 'text' (the content
    of the Tweet).

    Exception handling
    ----
    Check that Tweets are not null (or not what we expect)
    - length not 0
    - not isna
    - has keys that we want


    """
    tweets = []
    num_requests = 0
    http = set_up_adapter()
    if verbose:
        print("Collecting Tweets. This might take a while!")
    # Keep calling the API until we have the desired number of Tweets
    while len(tweets)<total_to_collect:
        # Get a batch of 100 Tweets
        response = connect_to_endpoint(http, url, parameters)
        num_requests += 1
        tweets.extend(response['data'])
        try:
            # If the API returned a pagination token, add it to our query parameters
            parameters['next_token'] = response['meta']['next_token']
        except KeyError:
            # If no token was returned, there are no more Tweets to collect
            break
        if verbose:
            print(f"\t{len(tweets)} Tweets collected!")
        # Rate limiting - pause the program so as not to overload the API
        if num_requests >= 450:
            pause = input(f"Approaching Twitter API rate limit. Pause, or exit with {len(tweets)} Tweets obtained? \nPress p for pause or any other key to exit:\t")
            if pause.lower() == 'p':
                time.sleep(15*60)
                num_requests = 0
            else:
                break
    print(f"{len(tweets)} Tweets collected.")
    return tweets


def sort_referenced_tweets(entry, ref_type):
    """
    Returns the ID of a referenced Tweet if its type
    matches the given 'ref_type' (quoted or replied_to),
    otherwise returns NaN.
    
    params
    ------
    entry:    List[Dict]
              A list of dictionaries detailing the 
              references of the Tweet in question (e.g.
              {'type': 'quoted', 'id': '12345'}) if
              applicable (otherwise NaN).
    ref_type: str
              The type of reference to extract (either
              quoted or replied_to)

    Test
    ----
    Expected inputs and outputs - pass a "test" list of dicts
    Parameterised test for different conditions.
    """
    if type(entry) != list:
        # No referenced Tweets, return NaN
        return entry
    for ref in entry:
        if ref['type'] == ref_type:
            # Matching type, return ID
            return ref['id']
    # Referenced Tweet does not match ref_type, return NaN
    return np.NaN


def anonymise_in_reply_to(user_id, ons_user_id):
    """
    Returns True if user_id provided matches
    the user_id of the @ons account.
    
    params
    ------
    user_id:   str
               Identifier of Twitter user
    """
    if user_id == ons_user_id:
        return True
    return False


def extract_user_handles(text):
    """
    Returns all user handles found in the given text.
    User handles are assumed to have format "@\w+"
    
    params
    ------
    text:    str
             The text of a Tweet
    """
    user_handle_format = re.compile(r'@\w+')
    user_handles = re.findall(user_handle_format, text)
    return user_handles


def replace_user_handles(text):
    """
    Extracts usernames from the given text and replaces 
    each one with one of the pseudo-random usernames in
    the given user_dictionary. Returns given text with 
    usernames replaced.
    
    params
    ------
    text:             str
                      Text containing usernames
    user_dictionary:  Dict
                      Dictionary of old and pseudo-random 
                      usernames in format:
                      {'original_username': 'new_username'}
    """
    handles = extract_user_handles(text)
    for user in handles:
        # Don't replace @ONS
        if user != '@ONS':
            text = text.replace(user, '@user')
    return text

def create_dataframe(tweets_dict):
    """
    Returns a dataframe built from provided dictionary

    params
    ------
    tweets_dict:    dict
                    Dictionary of Twitter API data with
                    attributes ID, created_at, 
                    in_reply_to_user_id, referenced_tweets, 
                    and text.
    """
    df = pd.DataFrame(tweets_dict)
    df = df[['id', 'created_at', 'in_reply_to_user_id', 'referenced_tweets', 'text']]
    return df

def check_usernames(text):
    """
    Searches the given text for usernames that have not been anonymised
    (i.e. any username that is not @ons or @user)
    Returns 1 if any non-anonymised usernames are found, otherwise 0.

    params
    ------
    text:       str
                The text to search for usernames
    """
    found_usernames = extract_user_handles(text)
    for username in found_usernames:
        if username not in ['@ONS', '@user']:
            # username other than @ONS and @user has been found
            return 1
    return 0

def all_usernames_removed(df):
    missed_usernames = df['text'].apply(check_usernames)
    if sum(missed_usernames) > 0:
        return False
    else:
        return True

def anonymise_dataframe(df, ons_user_id):
    """
    Given a dataframe containing Twitter data, returns
    the same dataframe with all user IDs and usernames
    removed.

    params
    ------
    df:         pd.DataFrame
                A dataframe containing Twitter API data 

    Test
    ----
    Does this function remove usernames and user IDs from a mini test dataframe?
    """
    df_new = df.copy()

    # remove user IDs
    df_new['in_reply_to_ons'] = df_new['in_reply_to_user_id'].apply(anonymise_in_reply_to, ons_user_id = ons_user_id)
    
    # replace all usernames - sometimes takes two passes
    while not all_usernames_removed(df_new):
        df_new['text'] = df_new['text'].apply(replace_user_handles)
    return df_new.drop(columns = ['in_reply_to_user_id'])

def tidy_dataframe(df):
    """
    Given a dataframe containing Twitter API data,
    returns the dataframe with 'quoted tweets' and
    'replied to tweets' in separate columns, rather
    than as dictionaries in a single column.

    params
    ------
    df:         pd.DataFrame
                A dataframe containing Twitter API data 
    """
    df_new = df.copy()

    # Extract quoted and replied to Tweet IDs
    df_new['quoted_tweet'] = df_new['referenced_tweets'].apply(sort_referenced_tweets, ref_type='quoted')
    df_new['repliedto_tweet'] = df_new['referenced_tweets'].apply(sort_referenced_tweets, ref_type='replied_to')

    df_new = df_new[['id', 'created_at', 'in_reply_to_ons', 'repliedto_tweet', 'quoted_tweet', 'text']]

    return df_new

def check_file_exists(filepath):
    """
    Check that the filepath to the save location is an existing file.
    If it is, return append mode and no headers.
    If it is not, return write mode and headers.

    params
    ------
    filepath:    str
                 Location of file to check
    """
    if os.path.exists(filepath):
        mode = 'a'
        header = False
    else:
        mode = 'w'
        header = True
    return mode, header

def main(ons_user_id, search_url, query_params, tweet_save_location):
    # Gather Tweets from previous week
    tweets = collect_tweets(search_url, query_params, total_to_collect = 2000, verbose = True)
    
    # convert to dataframe
    tweets_df = create_dataframe(tweets)

    # anonymise the dataframe
    tweets_df = anonymise_dataframe(tweets_df, ons_user_id)

    # tidy the dataframe
    tweets_df = tidy_dataframe(tweets_df)

    # check that the file exists
    mode, header = check_file_exists(tweet_save_location)

    # append to tweets TSV file or create
    tweets_df.to_csv(tweet_save_location, sep = '\t', index=False, mode=mode, header=header)

if __name__ == '__main__':

    ONS_USER_ID = '219275799'
    SEARCH_URL = 'https://api.twitter.com/2/tweets/search/recent'
    QUERY_PARAMS = {
        # the query parameter is our filter
        'query': '(#ons OR @ons OR "Office for National Statistics") -is:retweet lang:en -#fwb -from:ons',
        'max_results': 100,
        'tweet.fields': 'text,created_at,referenced_tweets',
        'expansions': 'in_reply_to_user_id'
    }
    TWEET_SAVE_LOCATION = '../data/tweets.tsv'

    main(ONS_USER_ID, SEARCH_URL, QUERY_PARAMS, TWEET_SAVE_LOCATION)