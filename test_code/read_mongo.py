
# ✅ Minimal Working Code (No Spark / No Databricks)
# pip install pymongo pandas

# 🧠 Notes
#     query={} will return all documents.
#     You can pass a Mongo-style filter query like:

#     query = {"status": "active"}
#     projection = {"name": 1, "email": 1, "_id": 0}

# ✅ When to Use This (vs Spark)
# Data < 100,000 documents (light data) OR Databricks not available


import pymongo
import pandas as pd

def read_mongo_to_df(mongo_uri, db_name, collection_name, query={}, projection=None):
    # Connect to MongoDB
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Fetch documents
    documents = list(collection.find(query, projection))

    # Convert to DataFrame
    df = pd.DataFrame(documents)
    
    # Optional: remove MongoDB _id column if not needed
    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)

    return df

if __name__ == "__main__":
    mongo_uri = "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/"
    db_name = "your_database"
    collection_name = "your_collection"

    df = read_mongo_to_df(mongo_uri, db_name, collection_name)

    print(df.head())




# # ========================================
# # from Databricks
# # ========================================

# org.mongodb.spark:mongo-spark-connector_2.12:10.1.1
# (Replace 2.12 and version if your Spark/Scala version is different)

# ✅ Working PySpark Code to Read from MongoDB in Databricks

# # Input parameters
# mongo_uri = "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/"
# database = "your_database_name"
# collection = "your_collection_name"

# # Full collection URI
# full_uri = f"{mongo_uri}{database}.{collection}?retryWrites=true&w=majority"

# # Create Spark session with Mongo config
# spark = SparkSession.builder \
#     .appName("ReadFromMongoDB") \
#     .config("spark.mongodb.read.connection.uri", full_uri) \
#     .getOrCreate()

# # Read from MongoDB collection
# df = spark.read.format("mongodb").load()

# # Show sample records
# df.show(truncate=False)

# ✅ Optional Enhancements

# If you want to parameterize more cleanly:
# from pyspark.sql import SparkSession

# def read_mongo_collection(mongo_uri, database, collection):
#     full_uri = f"{mongo_uri}{database}.{collection}?retryWrites=true&w=majority"
#     spark = SparkSession.builder \
#         .appName("ReadMongoCollection") \
#         .config("spark.mongodb.read.connection.uri", full_uri) \
#         .getOrCreate()
#     return spark.read.format("mongodb").load()
