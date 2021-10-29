import pandas as pd
import numpy as np
import pytest

"""----------------------------------------------------------------

        Functions from collect_and_anonymise_tweets.py

----------------------------------------------------------------"""

from collect_and_anonymise_tweets import anonymise_dataframe, replace_user_handles, anonymise_in_reply_to, check_usernames, sort_referenced_tweets

"""
Test for the anonymise_dataframe function.
This function should accept a dataframe containing unprocessed
Tweets and return a dataframe containing the same Tweets with 
usernames and user IDs removed.
"""

def test_anonymise_dataframe():
    """
    Check that the anonymise_dataframe function when applied to the test dataframe 
    returns the expected dataframe:
        - usernames other than @ONS replaced with @user
        - 'in_reply_to_user_id' column replaced with boolean 'in_reply_to_ons' column
    """
    test_df = pd.DataFrame(
        data = {
            'in_reply_to_user_id': ['1','24859200','219275799', 'three','135629500'],
            'text': ["@user345", "@ONS", "@ONSfan4", "hello @ONS @lukeskywalker @bobafett please RT", "@generalorgana i disagree about @ONS"]
        }
    )
    anon_df = pd.DataFrame(
        data = {
            'text': ["@user", "@ONS", "@user", "hello @ONS @user @user please RT", "@user i disagree about @ONS"],
            'in_reply_to_ons': [False,False,True, False,False]
        }
    )
    pd._testing.assert_frame_equal(anonymise_dataframe(test_df, ons_user_id='219275799'), anon_df)

"""
Tests for the replace_user_handles function
This function should accept a Tweet and return the same tweet with all
usernames other than @ONS replaced with @user.

We've written these tests for you, but you'll notice they all have the same
form - ideally you should parameterise them and make a single
test_replace_user_handles() function.
We've provided the test cases as a list to start you off.
"""

user_handles_test_cases = [
    ('@lando_calrissian123', '@user'),
    ('@bobafett @lando_calrissian123 @luke_skywalker @c3po whats up', '@user @user @user @user whats up'),
    ('hi @ONS I like stats', 'hi @ONS I like stats'),
    ('@generalorgana i disagree about @ONS', '@user i disagree about @ONS'),
    ('Hi @ONSfan_32 glad to hear you like stats', 'Hi @user glad to hear you like stats')
]

def test_single_username():
    """
    Test the function for a Tweet that consists of a single username (that is not @ONS).
    """
    assert replace_user_handles('@lando_calrissian123') == '@user'

def test_multiple_mentions():
    """
    Test the function for a Tweet that contains multiple usernames (that are not @ONS).
    """
    assert replace_user_handles('@bobafett @lando_calrissian123 @luke_skywalker @c3po whats up') =='@user @user @user @user whats up'

def test_ons_mention():
    """
    Test the function for a Tweet that contains the @ONS username - should not be changed.
    """
    assert replace_user_handles('hi @ONS I like stats') == 'hi @ONS I like stats'

def test_mixed_mentions():
    """
    Test the function for a Tweet that contains @ONS and another username.
    """
    assert replace_user_handles('@generalorgana i disagree about @ONS') == '@user i disagree about @ONS'

def test_username_containing_ons():
    """
    Test the function for a Tweet that contains a username that is similar to - but not the same as - @ONS.
    """
    assert replace_user_handles('Hi @ONSfan_32 glad to hear you like stats') == 'Hi @user glad to hear you like stats'

"""
Over to you - can you write a test for the anonymise_in_reply_to function?
anonymise_in_reply_to should accept a user ID and the @ONS user ID (219275799),
returning True if the user ID matches the @ONS user ID and False otherwise.
We've provided the parameters for this test, but you need to write it.
"""

anonymise_id_test_cases = [
    ('219275799', True),
    ('123456789', False),
    ('', False),
    (np.NaN, False)
]

@pytest.mark.parametrize("input_id, expected_output", anonymise_id_test_cases)
def test_anonymise_in_reply_to(input_id, expected_output):
    """
    If you pass user_id = '219275799' (the ONS user id), the function
    should return True. If you pass any other user_id, the function
    should return False.
    """
    pass

"""
Write a test for the check_usernames function
The function should return 1 if any non-anonymised 
usernames are found, otherwise 0.
Can you think of any additional tests (or test cases) to include?
"""

check_usernames_test_cases = [
    ('@user i disagree about @ONS', 0),
    ('@user i disagree about @ONS_fan32', 1),
    ('@user @user @user yes', 0),
    ('@user @user @missed_me yes', 1)
]

@pytest.mark.parametrize("input_string, expected_output", check_usernames_test_cases)
def test_check_usernames(input_string, expected_output):
    """
    Test that the function returns the expected outputs given the
    test cases.
    """
    pass

"""
Write tests for the sort_referenced_tweets function.
This function should return:
    - the input, if the input is not a list
    - the 'id' value of the dictionary in the list whose 'ref' value matches the passed 'ref_type'
    - np.NaN if the input is a list but does not contain a dictionary where the 'ref' value matches 'ref_type'
"""

# test cases
quoted_tweet_test_cases = [
    (np.NaN, np.NaN),
    ([{'ref': 'replied_to', 'id': '12345'}, {'ref': 'quoted', 'id': '67890'}], '67890'),
    ([{'ref': 'replied_to', 'id': '12345'}], np.NaN),
    ([{'ref': 'quoted', 'id': '67890'}], '67890')
]

repliedto_tweet_test_cases = [
    (np.NaN, np.NaN),
    ([{'ref': 'replied_to', 'id': '12345'}, {'ref': 'quoted', 'id': '67890'}], '12345'),
    ([{'ref': 'replied_to', 'id': '12345'}], '12345'),
    ([{'ref': 'quoted', 'id': '67890'}], np.NaN)
]

@pytest.mark.parametrize("input_list, expected_output", quoted_tweet_test_cases)
def test_sort_referenced_tweets_quoted(input_list, expected_output):
    """
    Test the sort_referenced_tweets function when the 
    ref_type parameter is 'quoted'
    """
    pass

@pytest.mark.parametrize("input_list, expected_output", repliedto_tweet_test_cases)
def test_sort_referenced_tweets_repliedto(input_list, expected_output):
    """
    Test the sort_referenced_tweets function when the 
    ref_type parameter is 'replied_to'
    """
    pass

"""----------------------------------------------------------------

        Functions from synchronise_tweets.py

----------------------------------------------------------------"""

"""
Write tests for some of the functions in the synchronise_tweets.py script.
Try to parameterize them so you can apply different test cases.
"""


from synchronise_tweets import format_list_of_ids, get_next_n, identify_missing_tweets

def test_list_of_ids():
    """
    Write a test for the function format_list_of_ids()
    """
    pass

def test_get_next_n():
    """
    Write a test or tests for get_next_n()
    Hint: you should create a test list and set n equal to something 
    much less than 100.
    """
    pass

def test_identify_missing_tweets():
    """
    Write a test for the identify_missing_tweets() function
    It accepts two lists of IDs as arguments and should return 
    IDs that are present in the first list but not the second.
    """
    pass
