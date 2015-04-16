__author__ = 'bsullivan'

import tweepy
import csv
import requests

"""
_UmmWaqqas
moakhan_
UmmatiMuhammed_
"""

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


def get_tweets(username, list_of_keys, count):

    auth = tweepy.OAuthHandler(list_of_keys[0], list_of_keys[1])
    auth.set_access_token(list_of_keys[2], list_of_keys[3])
    api = tweepy.API(auth)

    results = api.user_timeline(screen_name = username, count=count, include_entities="True")

    for tweet in results:
        if 'media' in tweet.entities:
            for image in tweet.entities['media']:
                #image_content = requests.get(media["media_url"])
                print image["media_url"]

    """
    filename = username + "_tweets.csv"
    with open(filename, "a") as tweetCSV:
        writer = csv.writer(tweetCSV)
        writer.writerow(["id", "created_at", "text", "media"])
        writer.writerows(results)
    """

    return results


def tweet_printer(tweet):
    print "TWEET ID: " + tweet.id_str
    print "TIME: ",
    print tweet.created_at
    print "TEXT: " + tweet.text.encode("utf-8")


def main():
    print "TWITTER SCRAPER!"
    print
    print "1. Assign new keys (if you're using a different computer)"
    print "2. Print the latest tweet from a given user."
    print "Q. Quit"
    print
    list_of_keys = assign_keys("C:\Users\\bsullivan\Desktop\\twittercredentials.txt")
    while True:
        choice = raw_input("Make your pick (1, 2, or Q).\n")
        if choice == "1":
            filepath = raw_input("Enter the new filepath: ")
            list_of_keys = assign_keys(filepath)
            print
        if choice == "2":
            username = raw_input("Enter the username." )
            count = int(raw_input("Enter the number of tweets you want. "))
            tweets = get_tweets(username, list_of_keys, count)
            for tweet in tweets:
                tweet_printer(tweet)
        if choice == "Q":
            break
        else:
            "Please choose 1, 2, or Q."


if __name__ == "__main__":
    main()