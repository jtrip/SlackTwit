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
        self.secrets = private.connections

    def send_slack_message(self, output):
        print('sending slack message')
        slack = slacker.Slacker(self.secrets['i3']['slack']['token'])
        slack.chat.post_message(
            self.channel,
            output,
            username=self.name,
            icon_url=self.pic
        )

    # Does the actual twitter search based on a list of keywords
    def search_twitter(self, keywords):
        print('searching twitter')
        # create a TwitterSearchOrder object, configure settings
        tso = TwitterSearchOrder()
        tso.set_keywords(keywords)
        # tso.set_language('en') # filter by language? no, for now
        tso.set_include_entities(True)

        # setup all the secrets
        twitter_search = TwitterSearch(
            consumer_key=self.secrets['i3']['twitter']['consumer_key'],
            consumer_secret=self.secrets['i3']['twitter']['consumer_secret'],
            access_token=self.secrets['i3']['twitter']['access_token'],
            access_token_secret=self.secrets['i3']['twitter']['access_token_secret']
        )

        # do the search, save it for amounts of fun that are not rate limited
        results = twitter_search.search_tweets_iterable(tso)
        return results

    # send recent tweet links one at a time to make sure they are unfurled
    def send_results(self, att):

        print(self)
        # we need to know the date and last hour in utc (print for log)
        utc_an_hour_ago = datetime.utcnow() - timedelta(hours=1)
        print('utc date: ' + str(utc_an_hour_ago.day))
        print('utc last hour: ' + str(utc_an_hour_ago.hour))

        url_base = 'https://twitter.com/'
        tweet_links = []

        for tweet in att:
            user_name = tweet['user']['screen_name']
            tweet_id = str(tweet['id'])

            date_parts = tweet['created_at'].split()
            date_parts.pop(4)  # remove timezone crap, because UTC

            # only use tweets from today
            if int(date_parts[2]) == utc_an_hour_ago.day:
                # only use tweets from the last hour
                if int(date_parts[3].split(':')[0]) == utc_an_hour_ago.hour:
                    try:
                        print(user_name)
                        print(tweet_id)
                        print(tweet['text'])
                        full_url = url_base + user_name + '/status/' + tweet_id
                        print(full_url)
                        tweet_links.append(full_url)
                    except:  # I once saw a tweet, but the log showed only user_name
                        print('weird tweet, no text?')

        tweet_links = tweet_links[::-1]  # reverse the order to oldest first

        for tweet_link in tweet_links[:10]:  # last minute limit to 10, needs improvement
            self.send_slack_message(tweet_link)


def main():
    i3_twitter_monitor = ChattyCharacter('slacktwit', '#test', '')
    results = i3_twitter_monitor.search_twitter(['Python3'])
    i3_twitter_monitor.send_results(results)


if __name__ == "__main__":
    main()
