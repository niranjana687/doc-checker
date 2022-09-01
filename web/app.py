from distutils.log import debug
from flask import Flask, jsonify, request
from pymongo import MongoClient
import spacy
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

#connecting to db
client = MongoClient('localhost', 27017)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)