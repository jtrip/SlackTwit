from time import strftime, sleep
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
    try:
        # create a TwitterSearchOrder object, configure settings
        tso = TwitterSearchOrder() 
        tso.set_keywords(keywords)
        # tso.set_language('en')
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
    
    except TwitterSearchException as e: 
        print(e)


# iterates through search restults creates the links, sends one at a time
def SendTweets(att,slacktwit):
    # get today's date and the last hour (print for debug)
    today = int(strftime('%d'))
    print('date: ' + str(today))
    lastHour = int(strftime('%H'))+3
    print('hour: ' + str(lastHour))
    
    urlBase = 'https://twitter.com/'
    tweetlinks = []
    
    for tweet in att:
        userName = tweet['user']['screen_name'] 
        tweetID = str(tweet['id'])
        
        date_parts = tweet['created_at'].split()
        date_parts.pop(4) # remove that crap that probably indicates timezone?

        # only use tweets from today
        if int(date_parts[2]) == today:   
            # only use tweets from the last hour
            if int(date_parts[3].split(':')[0]) == lastHour:
                print tweet['user']['screen_name']
                print tweet['text']
                fullURL = urlBase + userName + '/status/' + tweetID
                print(fullURL)
                tweetlinks.append(' '.join(date_parts) + '\n' +  fullURL)
                
    tweetlinks = tweetlinks[::-1] # reverse the order to oldest first

    for tweetlink in tweetlinks:             
        msgpost(slacktwit,tweetlink)    
        sleep(1)    # to ensure all links are unfurled, may not be necesary 


def main():
    botUser = ChattyCharacter('slacktwit','#social_media', '')
    SendTweets(twitSearch(['i3Detroit']),botUser)


if __name__ == "__main__":
    main()
    
