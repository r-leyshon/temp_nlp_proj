"""
This script iterates through all of the Tweets in a .tsv file
and calls the Twitter API to check that each Tweet still exists
on Twitter. Any Tweets that no longer exist on Twitter are 
removed from the .tsv file.
"""

import pandas as pd
import time

from supporting_files.api_functions import set_up_adapter, bearer_oauth

# GLOBALS
SEARCH_URL = 'https://api.twitter.com/1.1/statuses/lookup.json'
TWEET_SAVE_LOCATION = '../data/tweets.tsv'
NEW_SAVE_LOCATION = '../data/tweets_synchronised.tsv'  # in prod this should be = TWEET_SAVE_LOCATION (overwrite)

def format_list_of_ids(list_of_ids):
    """
    Returns the given list of IDs as a single string
    of comma-separated IDs.
    
    params
    ------
    list_of_ids:    List[int]
                    List of Tweet IDs
    """
    return ','.join([str(tweet_id) for tweet_id in list_of_ids])

def get_next_n(list_of_ids, bookmark, n = 100):
    """
    Given a list of IDs and a "bookmark" index,
    return a subset of the list between the bookmark
    index and the nth subsequent index.
    
    params
    ------
    list_of_ids:    List[int]
                    List of Tweet IDs
    bookmark:       int
                    Index of start of subset
    n:              int
                    Size of subset
    """
    next_bookmark = bookmark + n
    next_n_tweets = list_of_ids[bookmark:next_bookmark]
    if len(next_n_tweets) < n:
        # No more Tweets to search, therefore no bookmark
        next_bookmark = None
    next_n_tweets = format_list_of_ids(next_n_tweets)
    return next_n_tweets, next_bookmark

def get_batch(list_of_ids, http):
    """
    Returns the given list of IDs as a single string
    of comma-separated IDs.
    
    params
    ------
    list_of_ids:    List[int]
                    List of Tweet IDs

    http:           requests.Session object
                    Has all the methods of the requests 
                    package as well as parameters that 
                    persist across requests.

    """
    url = SEARCH_URL + '?id=' + list_of_ids
    response = http.get(
            url, 
            auth=bearer_oauth
        )
    return response.json()

def fetch_all_tweets(list_of_ids):
    """
    Given the list of Tweet IDs, repeatedly call the
    Twitter API to fetch the metadata of the Tweets
    in batches of 100. Returns a list of IDs that were
    returned without error (i.e. the Tweets still exist)

    params
    ------
    list_of_ids:    List[int]
                    A list of Tweet IDs to search for 
    """
    bookmark = 0
    tweets = []
    http = set_up_adapter()
    while bookmark is not None:
        ids, bookmark = get_next_n(list_of_ids, bookmark)
        response = get_batch(ids, http)
        # Just store the IDs of the found Tweets
        tweets.extend([str(r['id']) for r in response if 'id' in r.keys()])
        time.sleep(1)
    print(f"{len(list_of_ids)} Tweets searched for, {len(tweets)} Tweets returned.")
    return tweets

def identify_missing_tweets(list_of_ids, found_ids):
    """
    Returns the list of IDs that are present in the
    list_of_ids list but not in the found_ids list.
    
    params
    ------
    list_of_ids:    List[str]
                    List of Tweet IDs
    found_ids:      List[str]
                    List of Tweet IDs, expected to be
                    returned by fetch_all_tweets() 
                    function
    """
    return list(set(list_of_ids).difference(set(found_ids)))

def filter_out_missing_tweets(tweets_df):
    """
    Takes a dataframe and fetches list of Tweet IDs
    that are present in the dataframe but NOT on 
    the Twitter API. Returns the dataframe filtered to
    remove these IDs.
    
    params
    ------
    list_of_ids:    List[int]
                    List of Tweet IDs
    """
    tweet_ids = tweets_df['id'].tolist()
    missing_tweet_ids = identify_missing_tweets(tweet_ids, fetch_all_tweets(tweet_ids))
    print(f"{len(missing_tweet_ids)} Tweets removed.")
    return tweets_df[~tweets_df['id'].isin(missing_tweet_ids)]

def main():
    # load tweets
    stored_tweets = pd.read_csv(TWEET_SAVE_LOCATION, sep = '\t')
    stored_tweets['id'] = stored_tweets['id'].astype(str)

    # identify and remove deleted tweets
    synchronised_tweets = filter_out_missing_tweets(stored_tweets)

    # save
    synchronised_tweets.to_csv(NEW_SAVE_LOCATION, sep = '\t', index = False)

    # Warn user if number of Tweets is too low
    if len(synchronised_tweets) <= 3600:
        print(f"Warning. Total number of Tweets has dropped by > 20%. Current size of dataset: {len(synchronised_tweets)}.")
        print(f"Please run script `collect_and_anonymise_tweets.py` to replenish. Set `total_to_collect` to {4500 - len(synchronised_tweets)}.")

if __name__ == '__main__':
    main()