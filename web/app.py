from distutils.log import debug
from operator import pos
from flask import Flask, jsonify, request
from pymongo import MongoClient
import en_core_web_sm
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

def verifyPassword(username, password):

    if password == users.find_one({"Username": username})[0]["Password"]:
        return True
    else: 
        return False



def countTokens(username):

    num_tokens = users.find_one({"Username": username})[0]["Tokens"]

    return num_tokens


class Detect(Resource):

    def post(self):
        #get posted data
        postedData = request.get_json()

        #get username, password and texts from posted data
        username = postedData["username"]
        password = postedData["password"]
        text1 = postedData["text1"]
        text2 = postedData["text2"]

        user_exists = verfiyUserName(username)
        if not user_exists:
            retJSON = {
                "status": 302,
                "message": "Username does not exist. Try registering if you do not have an account."
            }
            return jsonify(retJSON)

        verified = verifyPassword(username, password)

        if not verified:
            retJSON = {
                "status": 303,
                "message": "incorrect  password"
            }
            return jsonify(retJSON)
    
        num_tokens = countTokens(username)

        if num_tokens <= 0:
            retJSON = {
                "status": 302,
                "message": "insufficient tokens"
            }
            return jsonify(retJSON)
        
        nlp = en_core_web_sm.load()

        text1 = nlp(text1)
        text2 = nlp(text2)

        ratio = text1.similarity(text2)

        retJSON = {
            "status": "200", 
            "similarity": ratio,
            "message": "similarity calculated succesfully"
        }

        users.update_one(
            {
                "Username": username
            },
            {
                "$set": {
                    "Tokens": num_tokens-1
                }
            })

        return jsonify(retJSON)

api.add_resource(Register, "/register")
api.add_resource(Detect, "/detect")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)