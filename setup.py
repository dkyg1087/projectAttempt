from flask import Flask
from flask_pymongo import PyMongo
app = Flask(__name__)
mongo = PyMongo(app,uri="mongodb://localhost:27017/testData")
def create_app():
    return app
def get_db():
    return mongo