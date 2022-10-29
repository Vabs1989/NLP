# Import libraries
import re
import numpy as np
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud
from better_profanity import profanity

# Remember to keep your Keys and Tokens a secret!
## Note: Don’t forget to remove the ‘#’ before each of these lines of code when you are providing the values
# and running the code

#consumer_key = 'xxxxx'
#consumer_secret = 'xxxxx'
#access_token = 'xxxxx'
#access_token_secret = 'xxxxx'

# Access Twitter Data
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# Working with Twitter Data

# Input a query from the user
query = input("Please enter your topic / person of interest: ")

# In this case, we will input the query as 'Elon Musk'
# Filter the query to remove retweets

filtered = query + "-filter:retweets"

# Generate the latest tweets on the given query
tweets = tweepy.Cursor(api.search_tweets,
                       q=filtered,
                       lang="en").items(100)

# Create a list of the tweets, the users, and their location
list1 = [[tweet.text, tweet.user.screen_name, tweet.user.location] for tweet in tweets]

# Convert the list into a dataframe

df = pd.DataFrame(data=list1,columns=['tweets','user', "location"])
# Convert only the tweets into a list

tweet_list = df.tweets.to_list()

# Create a function to clean the tweets. Remove profanity, unnecessary characters, spaces, and stopwords.

def clean_tweet(tweet):
    if type(tweet) == np.float:
        return ""
    r = tweet.lower()
    r = profanity.censor(r)
    r = re.sub("'", "", r) # This is to avoid removing contractions in english
    r = re.sub("@[A-Za-z0-9_]+","", r)
    r = re.sub("#[A-Za-z0-9_]+","", r)
    r = re.sub(r'http\S+', '', r)
    r = re.sub('[()!?]', ' ', r)
    r = re.sub('\[.*?\]',' ', r)
    r = re.sub("[^a-z0-9]"," ", r)
    r = r.split()
    stopwords = ["for", "on", "an", "a", "of", "and", "in", "the", "to", "from"]
    r = [w for w in r if not w in stopwords]
    r = " ".join(word for word in r)
    return r

cleaned = [clean_tweet(tw) for tw in tweet_list]

# Sentiment Analysis
# Define the sentiment objects using TextBlob
sentiment_objects = [TextBlob(tweet) for tweet in cleaned]
sentiment_objects[0].polarity, sentiment_objects[0]

# Create a list of polarity values and tweet text

sentiment_values = [[tweet.sentiment.polarity, str(tweet)] for tweet in sentiment_objects]
# Print the value of the 0th row.
sentiment_values[0]
# Print all the sentiment values
sentiment_values[0:99]

# Create a dataframe of each tweet against its polarity
sentiment_df = pd.DataFrame(sentiment_values, columns=["polarity", "tweet"])

# Save the polarity column as 'n'.
n = sentiment_df["polarity"]

# Convert this column into a series, 'm'.
m = pd.Series(n)

# Initialize variables, 'pos', 'neg', 'neu'.

pos = 0
neg = 0
neu = 0

# Create a loop to classify the tweets as Positive, Negative, or Neutral.
# Count the number of each.

for items in m:
    if items > 0:
        print("Positive")
        pos = pos + 1
    elif items < 0:
        print("Negative")
        neg = neg + 1
    else:
        print("Neutral")
        neu = neu + 1

print(pos, neg, neu)

# We will create a pie chart to graphically display the results of our analysis:
pieLabels = ["Positive","Negative","Neutral"]
populationShare=[pos,neg,neu]
figureObject, axesObject = plt.subplots()
axesObject.pie(populationShare,labels=pieLabels,autopct='%1.2f',startangle=90)
axesObject.axis('equal')
plt.show()

# We can also display the information in a textual format as shown:
# Display the number of twitter users who feel a certain way about the given topic.
print("%f percent of twitter users feel positive about %s"%(pos,query))
print("%f percent of twitter users feel negative about %s"%(neg,query))
print("%f percent of twitter users feel neutral about %s"%(neu,query))

# Create a Wordcloud from the tweets
all_words = ' '.join([text for text in cleaned])
wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(all_words)

plt.figure(figsize=(10, 7))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis('off')
plt.show()

#Twitter Sentiment Analysis Results ( Interpretation )
#From our code, we can conclude the following:

#37% of Twitter users who posted about Elon Musk feel positive about him.
#18% of Twitter users who posted about Elon Musk feel negative about him.
#45% of Twitter users who posted about Elon Musk feel neutral about him.
#Some of the most commonly associated words include ‘twitter’, ‘tesla’, ‘hiring’, ‘parag agarwal’,
# ‘trump’, ‘leaving’, ‘buy’, and ‘deal’.
#Background Note: At the time of writing this article, Elon Musk, who is the CEO of Tesla,
# has announced an offer to buy Twitter for about $44 billion. This brought about a huge discussion on the pros and
# cons of this move, including the possible return of former president of the United States, Donald Trump,
# to Twitter (his account had been suspended earlier). In the midst of all this, the CEO of Twitter, Parag Agarwal,
# announced a hiring freeze, as two top executives ended up leaving the company.






