import pandas as pd
import streamlit as st
import json
import os

from mongoDB import NewsDB
from newsCleaner import CleanNews

screen = st.sidebar.selectbox(
    "View", ('Upload News', 'Submit News', 'Get News', "View News", "Download News"), index=0)
st.title(screen)

newsDB = NewsDB('hkFinanceDB', 'news', os.environ["MONGO_URL"])
collection = newsDB.connectDB()

if screen == "Upload News":
    uploaded_file = st.file_uploader("Choose a JSON file", type = ["json"])
    if(uploaded_file):
        data = json.load(uploaded_file)["batch"]
        newsDB.insertManyNews(collection, data)
        st.balloons()

elif screen == "Submit News":
    with st.form("News", clear_on_submit=True):
        title = st.text_input("title")
        content = st.text_area("content")
        source = st.text_input("source")
        data = {"title": title,
                "content": content,
                "source": source
                }
        submitted = st.form_submit_button("Submit")
        if submitted:
            newsDB.insertOneNews(collection, data)

elif screen == "Get News":

    newsSentimentDB = NewsDB('hkFinanceDB', 'newsSentiment', os.environ["MONGO_URL"])
    newsSentimentColl = newsSentimentDB.connectDB()

    # create a table when user submit their form and export them as a txt file(pos/neg) to store news title
    def exportNewsTitle():
        # get class label from user session
        classLabels = {key: val for key, val in st.session_state.items() if "new" in key}
        sorted_key = sorted(classLabels, key=lambda index: int(index[4:]))

        df = pd.DataFrame({
        "title": newsTitles,
        "class_label": [classLabels[key] for key in sorted_key]
        })

        # filter out the news without label
        df = df[df.class_label != "none"]
        df["last_modified"] = pd.Timestamp.now().strftime('%Y-%m-%d')

        # insert the list of dict(record) into mongodb
        train_data = df.to_dict("records")
        newsDB.insertManyNews(newsSentimentColl, train_data)
        #st.balloons()

        # write the txt file
        # with open("pos1.txt", "a", encoding='utf-8') as f:
        #     f.writelines([title + "\n" for title in pos.values])
        #
        # with open("neg1.txt", "a", encoding='utf-8') as f:
        #     f.writelines([title + "\n" for title in neg.values])



    # try to scape data from rss feed
    import feedparser
    from numpy.random import choice

    rssLinkDict = {
        "yahoo":"https://hk.finance.yahoo.com/news/rssindex",
        "mingpao": "https://news.mingpao.com/rss/pns/s00004.xml",
        "rthk": "http://rthk9.rthk.hk/rthk/news/rss/c_expressnews_cfinance.xml",
        "icable": "https://rsshub.app/icable/all?option=brief",
        # https://rsshub.app/now/news/rank?category=finance
        "Now 新聞(fetch from google)": "https://news.google.com/rss/search?q=site%3Ahttps%3A%2F%2Fnews.now.com%2Fhome%2Ffinance%20when%3A7d&hl=zh-HK&gl=HK&ceid=HK%3Azh-Hant"
    }

    newSource = st.radio("Generate 10 random from this source:", list(rssLinkDict.keys()))
    rssLink = rssLinkDict[newSource]

    NewsFeed = feedparser.parse(rssLink)
    entries = NewsFeed.entries
    # Draw 10 news from the feed and clean the text
    try:
        randomTenNews = [CleanNews(news.title, news.summary, news.link, newSource) for news in choice(entries, size=10)]
    except AttributeError:
        # Catch error of no summary/ title
        randomTenNews = [CleanNews(news.title, "", news.link, newSource) for news in choice(entries, size=10)]


    with st.form("Data Categorization", clear_on_submit=True):

        classLabels = dict()
        newsTitles = []

        for index, news in enumerate(randomTenNews):
            try:
                st.subheader(news.title)
                newsTitles.append(news.title)
            except Exception as e:
                print(e)

            try:
                st.write(news.summary)
            except Exception as e:
                print(e)

            try:
                st.write(news.link)
            except Exception as e:
                print(e)
            # use session to store the radio values
            st.radio("Class:", ["none", "positive", "neutral", "negative"], key=f"news{index+1}")

        submitted = st.form_submit_button("Submit", on_click=exportNewsTitle)

elif screen == "View News":

    # get all training data for sentiment analysis
    newsSentimentDB = NewsDB('hkFinanceDB', 'newsSentiment', os.environ["MONGO_URL"])
    newsSentimentColl = newsSentimentDB.connectDB()

    allNews = newsSentimentDB.findTop20News(newsSentimentColl)
    df = pd.DataFrame(allNews, columns = ["title", "class_label", "last_modified"])
    st.table(df)

elif screen == "Download News":
    newsSentimentDB = NewsDB('hkFinanceDB', 'newsSentiment', os.environ["MONGO_URL"])
    newsSentimentColl = newsSentimentDB.connectDB()

    allNews = newsSentimentDB.findAllNews(newsSentimentColl)
    df = pd.DataFrame(allNews)

    @st.cache
    def df2csv(df):
        return df.to_csv(index = False).encode("utf-8")

    @st.cache
    def df2json(df):
        return str({"batch":df.to_dict("records")}).encode("utf-8")

    csv = df2csv(df)
    json = df2json(df)

    st.download_button(
        label = "Download all training news as csv file",
        data = csv,
        file_name= "training-news.csv",
        mime="text/csv"
    )
    st.download_button(
        label = "Download all training news as json file",
        data = json,
        file_name= "training-news.json",
        mime="application/json"
    )
