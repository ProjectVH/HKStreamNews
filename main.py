import streamlit as st
import os
import logging

from mongoDB import NewsDB


screen = st.sidebar.selectbox(
    "View", ('Overview', 'Fundamentals', 'News', 'Ownership', 'Strategy'), index=0)

st.title(screen)

symbol = st.sidebar.selectbox("Stock Symbol", [])

if screen == 'Overview':
    pass

elif screen == 'News':

    newsDB = NewsDB('hkFinanceDB','news',os.environ["MONGO_URL"])
    collection = newsDB.connectDB()

    allNews = newsDB.findAllNews(collection)

    if allNews:
        logging.info("found news in database")
    else:
        logging.info("no news in database")

    for article in allNews:
        st.subheader(article['title'])
        st.write(article['source'])
        st.write(article['content'])

elif screen == 'Fundamentals':
    pass
elif screen == 'Ownership':
    pass
elif screen == 'Strategy':
    pass