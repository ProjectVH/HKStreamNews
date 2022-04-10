from bs4 import BeautifulSoup
import re

class CleanNews():

    def __init__(self, title, summary, link, source):
        self.title = title
        self.summary = summary
        self.link = link
        self.source = source
        self.remove_html()
        self.clean_title()

    def remove_html(self):
        """
        remove html element in the news title and summary
        """
        # remove xml encoding
        self.summary = re.sub(r"&lt;.*&gt;", "", self.summary)
        soup_title = BeautifulSoup(self.title, 'html.parser')
        soup_summary = BeautifulSoup(self.summary, 'html.parser')
        self.title = soup_title.get_text()
        self.summary = soup_summary.get_text()

    def clean_title(self):
        """
        Clean unnecessary source indication from Google News feed
        """
        if "(fetch from google)" in self.source:
            tmp = self.source.replace("(fetch from google)", "")
            self.title = self.title.replace(f" - {tmp}", "")




