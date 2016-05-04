from datetime import datetime, timedelta
from TwitterSearch import *
import slacker
import private

# I used this because I use it for other slack 'post as' scripts
class ChattyCharacter:
    def __init__(self, name, channel, pic):
        self.name = name
        self.channel = channel
        self.pic = pic


# send a post to slack using the ChattyCharacter data
def msgpost(thecharacter, output):
    slack = slacker.Slacker(private.i3)
    slack.chat.post_message(
        thecharacter.channel, 
        output, 
        username=thecharacter.name, 
        icon_url=thecharacter.pic
    )


# Does the actual twitter search based on a list of keywords
def twitSearch(keywords):
    # create a TwitterSearchOrder object, configure settings
    tso = TwitterSearchOrder() 
    tso.set_keywords(keywords)
    # tso.set_language('en') # filter by language? no, for now
    tso.set_include_entities(True)

    # setup all the secrets
    ts = TwitterSearch(
        consumer_key          = private.consumer_key,    
        consumer_secret       = private.consumer_secret,  
        access_token          = private.access_token,        
        access_token_secret   = private.access_token_secret       
    )

    # do the search, save it for amounts of fun that are not rate limited 
    return ts.search_tweets_iterable(tso)
    

# send recent tweet links one at a time to make sure they are unfurled 
def SendTweets(att,slacktwit):
    # we need to know the date and last hour in utc (print for log)
    utc_an_hour_ago = datetime.utcnow() - timedelta(hours=1)
    print('utc date: ' + str(utc_an_hour_ago.day))
    print('utc last hour: ' + str(utc_an_hour_ago.hour))

    urlBase = 'https://twitter.com/'
    tweetlinks = []
    
    for tweet in att:
        userName = tweet['user']['screen_name'] 
        tweetID = str(tweet['id'])
        
        date_parts = tweet['created_at'].split()
        date_parts.pop(4) # remove timezone crap, because UTC

        # only use tweets from today
        if int(date_parts[2]) == utc_an_hour_ago.day:   
            # only use tweets from the last hour
            if int(date_parts[3].split(':')[0]) == utc_an_hour_ago.hour:
                try:
                    print userName
                    print tweetID
                    print tweet['text']
                    fullURL = urlBase + userName + '/status/' + tweetID
                    print(fullURL)
                    tweetlinks.append(fullURL)
                except:  #I once saw a tweet, but the log showed only userName
                    print "weird tweet, no text?"
                    
    tweetlinks = tweetlinks[::-1] # reverse the order to oldest first

    for tweetlink in tweetlinks:             
        msgpost(slacktwit,tweetlink)


def main():
    botUser = ChattyCharacter('slacktwit','#outreach', '')
    SendTweets(twitSearch(['i3Detroit']),botUser)


if __name__ == "__main__":
    main()
    
