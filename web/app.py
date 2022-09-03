from distutils.log import debug
from operator import pos
from flask import Flask, jsonify, request
from pymongo import MongoClient
import spacy
from flask_restful import Resource, Api
import bcrypt

app = Flask(__name__)
api = Api(app)

#connecting to db
client = MongoClient('localhost', 27017)
db = client.docCheckerDB
users = db["Users"]

#check if username is taken
def verifyUserName(username):
    if users.find_one({"Username": username}).count() > 0:
        return True
    else:
         return False

#registration end point
class Register(Resource):
    def post(self):
        #get the posted data
        postedData = request.get_json()

        #store it as password and username
        username = postedData["username"]
        password = postedData["password"]

        #check if the username alrewady exists
        user_exists = verfiyUserName(username)
    
        #if yes send fail message
        if user_exists:
            retJSON = {
                "status": 301,
                "message": "Username already exists"
            }
            return jsonify(retJSON)

        #if not hash password and add that and the username  to db send succesful message
        hashed_pw = bcrypt.hashedpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert_one({
            "Username": username,
            "Password": hashed_pw,
            "Tokens": 10
        })

        retJSON = {
            "status": 200,
            "message": "User registration succesful"

        }

        return jsonify(retJSON)
        
api.add_resource(Register, "/register")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)