# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 21:06:49 2022

@author: t
"""

import praw
import streamlit as st
import pandas as pd
import re

from collections import Counter

# https://www.analyticsvidhya.com/blog/2019/08/how-to-remove-stopwords-text-normalization-nltk-spacy-gensim-python/
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS
# Load English tokenizer, tagger, parser, NER and word vectors
nlp = English()

@st.cache
def convert_df(df):
   return df.to_csv().encode('utf-8')


st.title('Reddit Comments Collector')
st.write('Using the Reddit API, this app fetches comments from Reddit threads.')


st.subheader("Input your Reddit API information")
st.write("To create an API key, [sign up for Reddit](https://www.reddit.com/register/) then [go here and scroll to the bottom to create an API key.](https://www.reddit.com/prefs/apps)")
st.write("Here's an image showing what everything is once you've created an API key.")
with st.expander("See image"):
    st.image('reddit_api_example.png')


username = st.text_input('Input your Reddit username here')
password = st.text_input("Input your Reddit password")
userAgent = "scraptest" + username
clientId = st.text_input("Input your personal use script ID")
clientSecret = st.text_input("Input your secret key")

st.write('(For the next question, input a Reddit thread url [like this](https://www.reddit.com/r/AskReddit/comments/qvlp2v/whats_the_biggest_waste_of_time/))')
reddit_url = st.text_input("Input the url for your Reddit thread here")

limit_search_posts = st.number_input("How many comments should we collect? (Write 9999 for unlimited comments (will take a while)).", value=0)

st.write(" ")
entered_info_button = st.button("Once you've inputted your Reddit information, click here to start the comments collector.")

if entered_info_button:
    r = praw.Reddit(user_agent=userAgent, client_id=clientId, client_secret=clientSecret) 


    reddit_url_id = reddit_url.split('/')[-3]
    # st.write(reddit_url_id)

    comments_list = []
        
    submission = r.submission(str(reddit_url_id))
    
    # https://praw.readthedocs.io/en/stable/tutorials/comments.html
    submission.comments.replace_more(limit= limit_search_posts) # None)
    for comment in submission.comments.list():
        comments_list.append( {'author': comment.author,
                                'text': comment.body})

    # convert to pandas df
    comments_df = pd.DataFrame(comments_list)

    csv = convert_df(comments_df)

    st.download_button(
       "Download the Reddit comments",
       csv,
       "reddit_comments_" + str(reddit_url_id) + ".csv",
       "text/csv",
       key='download-csv'
    )

    # get all comments into one long string
    comments_str_list = comments_df['text'].to_list()
    comments_str = " ".join(comments_str_list)

    # remove punctuation
    comments_str = re.sub(r'[^\w\s]', '', comments_str)
    # make all words lowercase
    comments_str = comments_str.lower()

    # turn the comments into spacy tokens
    #  "nlp" Object is used to create documents with linguistic annotations.
    my_doc = nlp(comments_str)

    # Create list of word tokens
    token_list = []
    for token in my_doc:
        token_list.append(token.text)

    # Create list of word tokens after removing stopwords
    filtered_sentence =[] 

    for word in token_list:
        lexeme = nlp.vocab[word]
        if lexeme.is_stop == False:
            filtered_sentence.append(word) 

    # make list of filtered words into one long string
    filtered_sentence_str = " ".join(filtered_sentence)

    # count top words
    # generate DF out of Counter
    rslt = pd.DataFrame(Counter(filtered_sentence).most_common(20),
                        columns=['Word', 'Frequency']).set_index('Word')
    # print(rslt)

    # plot
    top_words_download_df = convert_df(rslt)
    st.download_button(
       "Download the top words",
       top_words_download_df,
       "reddit_comments_top_words_" + str(reddit_url_id) + ".csv",
       "text/csv",
       key='download-csv'
    )

    st.subheader("Chart of the top words used in the comments")
    st.bar_chart(rslt)

    





    st.write(comments_list)




    
    