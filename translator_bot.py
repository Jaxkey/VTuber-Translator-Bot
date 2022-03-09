import tweepy
import deepl
import numpy as np
from time import sleep

#### Twitter API Keys ####
CONSUMER_KEY = 'INSERT CONSUMER KEY HERE'
CONSUMER_SECRET = 'INSERT CONSUMER SECRET KEY HERE'
ACCESS_KEY = 'INSERT ACCESS KEY HERE'
ACCESS_SECRET = 'INSERT ACCESS SECRET KEY HERE'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
mentions = api.mentions_timeline()

#### DeepL API Key ####
translator = deepl.Translator('INSERT DEEPL KEY HERE')

NAMES_FILE = 'account_names.txt'
ID_FILE = 'last_seen_id.txt'


### Run the main translation ###
def run_translation():
    user_index = 0

    for user in handles_ids[0]:
        handle = user[0]  # index '0' contains handle
        last_tweet = user[1]  # index '1' contains last tweet id

        current_tweet_index = 0

        print('Name: ' + handle + ' ID: ' + last_tweet)

        # Find the first tweet that isn't a RT
        while True:
            tweet_text, tweet_id = get_tweet(handle, current_tweet_index)

            if not tweet_text.startswith('RT'):
                break

            print(handle + ' - RT Found')
            current_tweet_index += 1

        # See if last tweet was already translated
        if int(last_tweet) == tweet_id:
            print('Already translated Tweet with ID: ' + last_tweet)
            user_index += 1
            continue

        # Remove links to any media in the Tweet
        if "https://" in tweet_text:  # NOTE: This could potentially break if there is a standard link. I'll change this if it becomes an issue
            tweet_text = tweet_text[:tweet_text.index("https://")]

        print(tweet_text)

        # Check if enough characters remain to translate the Tweet
        if check_remaining_characters(len(tweet_text)):
            continue

        translated_text = translate_tweet(tweet_text)

        # Make sure translated Tweet is under 280 character limit
        if len(translated_text) > 280:
            print("Tweet was too long (must be less than or equal to 280 characters, was " + translated_text)
            user_index += 1
            continue

        api.update_status('@' + handle + ' ' + '【AI Translation 🤖】\n\n' + translated_text, in_reply_to_status_id=tweet_id)

        # Update the file to store the new id
        update_last_seen(tweet_id, user_index)
        user_index += 1


### Get most recent tweet number 'index' +1 from set user ###
### Return tweet's text and id ###
def get_tweet(handle, index):
    key = api.user_timeline(screen_name=handle, tweet_mode='extended')  # 'extended' grabs the entire text
    tweet_text = key[index].full_text
    tweet_id = key[index].id
    return tweet_text, tweet_id


### Translate and return? the text ###
def translate_tweet(tweet_text):
    translated = translator.translate_text(tweet_text, source_lang='JA', target_lang='EN-US')
    tr_string = str(translated)
    print(tr_string)

    return tr_string


### Initialize the main list from files (List = [[HANDLE, ID], [HANDLE, ID]...]) ###
def initialize_list():
    name_file = open('account_names.txt', 'r')
    id_file = open('last_seen_id.txt', 'r')

    names = []
    ids = []

    # Add names and ids from respective files until there are none left
    while True:
        name_line = name_file.readline()
        id_line = id_file.readline()

        if not name_line:
            break

        names.append(name_line.strip())
        ids.append(id_line.strip())

    name_file.close()
    id_file.close()

    return np.dstack((names, ids))


### Update last_seen_id.txt to the given id ###
def update_last_seen(tweet_id, index):
    # Read file into an array
    with open('last_seen_id.txt', 'r') as file:
        data = file.readlines()

    # Update the user's most recent id in the array
    data[index] = str(tweet_id) + '\n'

    # Write everything back
    with open('last_seen_id.txt', 'w') as file:
        file.writelines(data)

    file.close()


### Make sure there are enough characters remaining for translation ###
def check_remaining_characters(tweet_len):
    usage = translator.get_usage()

    if tweet_len + usage.character.count > usage.character.limit:
        print("Unable to translate. Out of characters.")
        return True

    return False


while True:
    handles_ids = initialize_list()
    print(handles_ids)
    run_translation()
    # Wait 15 minutes before running again
    sleep(900)
