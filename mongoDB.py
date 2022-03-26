import pymongo
from pymongo.errors import BulkWriteError

class MongoDB:
    def __init__(self, dbName, colName, MONGO_URL):
        self.dbName = dbName
        self.colName = colName
        self.MONGO_URL = MONGO_URL

    def connectDB(self):
        """
        make connection to database and collection
        :return: collection
        """
        dbName = self.dbName
        colName = self.colName
        dbConn = pymongo.MongoClient(self.MONGO_URL, tlsAllowInvalidCertificates = True)
        db = dbConn[dbName]
        collection = db[colName]
        return collection

class NewsDB(MongoDB):
    def __init__(self, dbName, colName, MONGO_URL):
        super(NewsDB, self).__init__(dbName, colName, MONGO_URL)

    def findAllNews(self, collection):
        """
        Get all the news from collection
        :return: list of dictionary
        """
        try:
            allNews = collection.find({})
        except:
            allNews = []

        return allNews

    def findTop20News(self, collection):
        """
        Get 20 recent news from collection, descending order
        :return: list of dictionary
        """
        try:
            allNews = collection.find({}).sort("last_modified", -1).limit(20)
        except:
            allNews = []

        return allNews

    def insertOneNews(self, collection, dict1):
        """
         Given a json(news record), insert it into news collection
        """
        from streamlit import success, error
        try:
            collection.insert_one(dict1)
            success("Success")
        except Exception as e:
            error(e)


    def insertManyNews(self, collection, lst):
        """
         Given a list of json(news record), insert all of them into news collection
        """
        from streamlit import success, error
        try:
            collection.insert_many(lst, ordered = False)
            success("Success")
        except BulkWriteError as e:
            error("DuplicateKeyError,"+str(e))
        except Exception as e:
            error(e)





