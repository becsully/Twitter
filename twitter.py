# Hey! 
# This script can be run out of the Terminal or Command Prompt on your computer
# with minimal instruction / knowledge of programming (hopefully!). 
# Macs come with Python pre-installed. Windows users will have to download it.
# Another package called pip makes it very easy to install Tweepy. 
# Once you have Python and pip installed, simply type
#     pip sudo install tweepy
# into the Command Prompt or Terminal, and you will be good to go. 
#
# Save this twitter.py script in a file of your choice, and be sure to include
# a text file with the four credentials necessary to access the Twitter API: 
# The consumer key, the consumer secret, the access key, and the access secret. 
# You can get all four of these from http://dev.twitter.com. 
# Save all four in a text file, with each on its own line. 
# Save that text file in the same directory as this Python script. 
# Then head to Terminal/Command Prompt and save tweets to your heart's content.
# Navigate to the directory where you saved twitter.py, then type
#     python twitter.py


import tweepy
import csv
import urllib
import os
import shutil
from tempfile import NamedTemporaryFile


# This function just reads your credentials file and returns a Python-readable list of the four keys.
def assign_keys(filename):
    consumer_key, consumer_secret, access_key, access_secret = "", "", "", ""
    list_of_keys = [consumer_key, consumer_secret, access_key, access_secret]
    count = 0
    with open(filename, "r") as keys:
        for line in keys:
            list_of_keys[count] = line.replace("\n","")
            count += 1
        keys.close()
    return list_of_keys


# This sends the credentials to Twitter and returns with access to the API. 
def authenticate(list_of_keys):
    auth = tweepy.OAuthHandler(list_of_keys[0], list_of_keys[1])
    auth.set_access_token(list_of_keys[2], list_of_keys[3])
    api = tweepy.API(auth)
    return api


# This will return the ID number of the most recent tweet of a given user. 
def find_latest_tweet(username, list_of_keys):
    api = authenticate(list_of_keys)
    results = api.user_timeline(screen_name=username, count=1)
    return results[0].id


# This function accesses the API and returns a list of tweets 
# and all their properties, given a set of parameters to work with.)
def get_tweets(username, list_of_keys, count, max_id=None, since_id=None):
    api = authenticate(list_of_keys)
    results = api.user_timeline(screen_name=username, count=count, include_entities="True", max_id=max_id, since_id=None)
    return results


# This accepts a single tweet "object," checks for an embedded photo, and saves a local version.
def picture_saver(username, tweet): #accepts a SINGLE TWEET OBJECT
	
	# These two lines check the present directory and 
	# create a new folder under the username for Pictures.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dir = os.path.join(script_dir, username, 'Pictures')
    try:
        os.makedirs(dest_dir)
    except OSError:
        pass

	# This saves each image embedded in the tweet in the folder created above. 
    for image in tweet.entities['media']:
        try:
            filename = image["media_url"].split("/")[-1]
            path = os.path.join(dest_dir, filename)
            testfile = urllib.URLopener()
            testfile.retrieve(image["media_url"], path)
        except IOError:
            pass


# this function just takes a list of Tweet "objects" and saves the 
# relevant info in an easier-to-work-with Python list.			
def ready_tweets(username, tweets, save_pictures):
    outtweets = []
    for tweet in tweets:
        media_urls = []
        if "media" in tweet.entities:
            if save_pictures:
                picture_saver(username, tweet)
            for image in tweet.entities['media']:
                media_urls.append(image["media_url"])
        outtweets.append([tweet.id_str, tweet.created_at, tweet.text.encode("utf-8"), media_urls])
    return outtweets


# This is what you want to run the first time you save a user's tweets. 
# The Twitter API limits searches to 200 tweets at a time, and limits the total
# to about 3200. Older tweets are inaccessible from the API. 
# This function will retrieve the latest 3200 or so tweets, and save them
# (with date/time posted, tweet ID, text, and URL to any photo) in
# an Excel-readable CSV file. 
def tweets_to_csv(username, keys, save_pictures=False):

    alltweets = []
    new_tweets = get_tweets(username, keys, 200)
    alltweets.extend(new_tweets)
    oldest = alltweets[-1].id - 1

    while len(new_tweets) > 0:
        print "getting tweets before %s" % oldest
        new_tweets = get_tweets(username, keys, 200, max_id = oldest)
        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1
        print "...%i tweets downloaded so far\n" % len(alltweets)

    outtweets = ready_tweets(username, alltweets, save_pictures)

	# this bit of "path" code is creating a folder for the username
	# where it will save the CSV file. 
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dir = os.path.join(script_dir, username)
    try:
        os.makedirs(dest_dir)
    except OSError:
        pass
    filename = username + "_tweets.csv"
    with open(os.path.join(dest_dir, filename), "w") as tweetCSV:
        writer = csv.writer(tweetCSV)
        writer.writerow(["TWEET ID", "DATE/TIME", "TEXT OF TWEET", "PHOTO URL(S)"])
        writer.writerows(outtweets)

		
# Once you've created the initial CSV file, you can run this function
# to update it. It will check what the person's newest tweet is, along with
# the last tweet you saved to the CSV, and fill in all the tweets
# that they've posted since. 
def update(username, keys, save_pictures=False):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    user_dir = os.path.join(script_dir, username)
    filename = username + "_tweets.csv"
    with open(os.path.join(user_dir, filename), "r") as tweetCSV:
        latest = list(tweetCSV)[1].split(",")[0]
        tweetCSV.close()

    print "LATEST TWEET IN CSV: " + latest
    newest = find_latest_tweet(username, keys)
    print "NEWEST TWEET IN TIMELINE: " + str(newest)

    tweets_to_add = []
    while True:
        if int(latest) < int(newest):
            newtweets = get_tweets(username, keys, 200, since_id=latest)
            tweets_to_add.extend(newtweets)
            latest = tweets_to_add[-1].split(",")[0]
        else: break

    final_new_tweets = ready_tweets(username, tweets_to_add, save_pictures)

    tempfile = NamedTemporaryFile(delete=False)
    with open(os.path.join(user_dir, filename), "r") as csvfile, tempfile:
        reader = csv.reader(csvfile)
        writer = csv.writer(tempfile)
        writer.writerow(["TWEET ID", "DATE/TIME", "TEXT OF TWEET", "PHOTO URL(S)"])
        writer.writerows(final_new_tweets)
        for row in reader:
            if row[0] == "TWEET ID": pass
            else:
                writer.writerow(row)

    shutil.move(tempfile.name, os.path.join(user_dir, filename))


# this just prints the tweet info out nicely for you in the Terminal / Command Prompt.
def tweet_printer(tweet):
    print "TWEET ID: " + tweet.id_str
    print "TIME: ",
    print tweet.created_at
    print "TEXT: " + tweet.text.encode("utf-8")
    if "media" in tweet.entities:
        for image in tweet.entities["media"]:
            print "MEDIA TYPE: " + image["type"]
            print "MEDIA URL: " + image["media_url"]
    else:
        print "MEDIA: (none)"


def main():
    print "TWITTER SCRAPER!"
    print
    try:
		## Update this file path to use this on your computer! 
        list_of_keys = assign_keys("C:\\Users\\bsullivan\\Desktop\\twittercredentials.txt")
    except IOError:
        print "Choose Option 1 to enter the file path of your authentication document."
        print "If you don't have one, get the four Twitter keys and save them on separate lines in a txt file."
    while True:
	    print
	    print "1. Assign new keys (if you want to change the user authentication)"
        print "2. Print a given number of a given user's latest tweets."
        print "3. Save a given user's tweets to CSV (photo URLs only)."
        print "4. Save a given user's tweets to CSV, and save photos to local folder."
        print "5. Update a user's CSV with their latest tweets (photo URLs only)."
        print "6. Update a user's CSV with their latest tweets, and save photos to local folder."
        print "Q. Quit"
        print
        choice = raw_input("Make your pick (1, 2, 3, 4, 5, 6, or Q).\n")
        if choice == "1":
            print "Enter the file path of your credentials. (If it's in the same"
            filepath = raw_input("directory as this script, the path is just the file name and extension.) ")
            list_of_keys = assign_keys(filepath)
            print
        if choice == "2":
            username = raw_input("Enter the username." )
            count = int(raw_input("Enter the number of tweets you want. "))
            tweets = get_tweets(username, list_of_keys, count)
            for tweet in tweets:
                tweet_printer(tweet)
        if choice == "3":
            username = raw_input("Enter the username." )
            tweets_to_csv(username, list_of_keys)
        if choice == "4":
            username = raw_input("Enter the username." )
            tweets_to_csv(username, list_of_keys, save_pictures=True)
        if choice == "5":
            username = raw_input("Enter the username." )
            update(username, list_of_keys)
        if choice == "6":
            username = raw_input("Enter the username." )
            update(username, list_of_keys, save_pictures=True)
        if choice == "Q" or choice == "q":
            break
        else:
            "Please choose 1, 2, 3, 4 5, 6, or Q. (Don't type a space.)"


if __name__ == "__main__":
    main()