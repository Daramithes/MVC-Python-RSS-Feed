#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      nickw
#
# Created:     01/04/2019
# Copyright:   (c) nickw 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from Models import *
from pymongo import MongoClient
from flask import Flask, request, render_template
from flask_api import  status
from bson.json_util import dumps
import json
import urllib.request
import feedparser
import cgi
import re

client = MongoClient('localhost', 27017)
db = client['Enterprise-Web']
UserModel= UserModel(db)
RSSModel = RSSModel(db)

import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)
app.debug = True


#This route is the starting page that the user will start on, just return it
@app.route('/', methods=["GET"])
def Login():
    return render_template('login.html'), status.HTTP_200_OK
#This post method processes the users login attempt
@app.route('/Login', methods=["POST"])
def LoginUser():

    #Extract the data from the post requests body
    data = request.get_json()

    #Ensure  dictonary keys are appropriate for further use
    if DataKeyCheck(data, ["Username", "Password"]):
        return "Your object headings are not valid", status.HTTP_400_BAD_REQUEST
    #Return Santized Data
    SanitizedData = SanitizeInput(data)
    #Check for valid characters

    if CheckForInvalidCharacter(SanitizedData):
        return "Invalid input", status.HTTP_400_BAD_REQUEST

    #Check for password strength

    #Query Database if User Exists, and provide response
    Username = SanitizedData['Username']
    Password = SanitizedData['Password']
    #Run the models get user function and pull out the assosiated object and resulting string.
    User, Result = UserModel.GetUser(Username,Password)
    #Compare results either return a rendered page or error message.
    if Result == "User Found, Password Verified":
        Feeds, Consolidated_List = RSSModel.UserAccessAllFeeds(User)
        UserModel.UpdateTime(User)
        return render_template('RSS.html', Feeds = Feeds, Consolidated_List = Consolidated_List, name = User.GetUsername()), status.HTTP_202_ACCEPTED
    elif Result == "User Doesnt Exist":
        return "User Not Found", status.HTTP_404_NOT_FOUND
    else:
        return "User found, password incorrect", status.HTTP_401_UNAUTHORIZED

#This post request handles the users register attempt
@app.route('/Register', methods=["POST"])
def RegisterUser():
   #Extract JSON from the request
    data = request.get_json()

    #Ensure  dictonary keys are appropriate for further use
    if DataKeyCheck(data, ["Username", "Password"]):
        return "Your object headings are not valid", status.HTTP_400_BAD_REQUEST

    #Return Santized Data
    SanitizedData = SanitizeInput(data)

    #Check for valid characters

    if CheckForInvalidCharacter(SanitizedData):
        return "Invalid Input", status.HTTP_400_BAD_REQUEST

    #Check for password strength

    if PasswordStrength(data['Password']):
        return "Your Password is not strong enough", status.HTTP_400_BAD_REQUEST

    #Extract the santized data and store as variable
    Username = SanitizedData['Username']
    Password = SanitizedData['Password']
    #Call the models save user function
    User = UserModel.SaveUser(Username, Password)
    #Examine returned response, if its a string return an error, otherwise compile the templating engines response and return to the user.
    if User == "User already Exists":
        return "User Already Exists", status.HTTP_409_CONFLICT
    else:
        Feeds, Consolidated_List = RSSModel.UserAccessAllFeeds(User)
        return render_template('RSS.html', Feeds = Feeds, Consolidated_List = Consolidated_List, name =  User.GetUsername()), status.HTTP_201_CREATED

#This function handles a request for ONE feed, this feed isn't saved.
@app.route('/RSS-One', methods=["POST"])
def AccessOneFeed():
    data = request.get_json()

    #Ensure  dictonary keys are appropriate for further use
    if DataKeyCheck(data, ["Link"]):
        return "Your object headings are not valid", status.HTTP_400_BAD_REQUEST

    #Return Santized Data
    SanitizedData = SanitizeInput(data)

    #Check for valid characters

    if CheckForInvalidCharacter(SanitizedData):
        return "Invalid Input", status.HTTP_400_BAD_REQUEST

    #Run a series of checks to see if the link is valid XML
    if WebAddressExist(SanitizedData['Link']):
        return "Invalid Link", status.HTTP_400_BAD_REQUEST

    link = SanitizedData['Link']

    #Call the models save feed function
    RSS = RSSModel.SaveRSSFeed(link)
    #Convert the response to an object and run it into the templating engine for a response.
    RSS.RecordsToObjects()

    return render_template('Single_Template.html', Feed = RSS), status.HTTP_200_OK

#Same as before, except save the information to the database.
@app.route('/RSS-Save', methods=["POST"])
def UserSaveFeed():
    data = request.get_json()

        #Ensure  dictonary keys are appropriate for further use
    if DataKeyCheck(data, ["Link", 'Username']):
        return "Your object headings are not valid", status.HTTP_400_BAD_REQUEST

    #Return Santized Data
    SanitizedData = SanitizeInput(data)

    #Check for valid characters

    if CheckForInvalidCharacter(SanitizedData):
        return "Invalid Input", status.HTTP_400_BAD_REQUEST
   #Run a series of checks to see if the link is valid XML
    if WebAddressExist(SanitizedData['Link']):
        return "Invalid Link", status.HTTP_400_BAD_REQUEST

    Link = SanitizedData['Link']
    Username = SanitizedData['Username']
    #Examine response, and inform the user in the front end.
    if RSSModel.UserAccessFeed(Link, Username):
        return "User Already Saved", status.HTTP_409_CONFLICT
    else:
        return "Feed saved successfully, it will appear on next login", status.HTTP_201_CREATED

#This entry point handles when the user clicks remove, and deletes the record from their database.
@app.route('/RSS-Delete', methods=["POST"])
def UserDeleteFeed():
    #Extract data from the post request
    data = request.get_json()

            #Ensure  dictonary keys are appropriate for further use
    if DataKeyCheck(data, ["Link", 'Username']):
        return "Your object headings are not valid", status.HTTP_400_BAD_REQUEST

    #Return Santized Data
    SanitizedData = SanitizeInput(data)

    #Check for valid characters

    if CheckForInvalidCharacter(SanitizedData):
        return "Invalid Input", status.HTTP_400_BAD_REQUEST

    #Run a series of checks to see if the link is valid XML
    if WebAddressExist(SanitizedData['Link']):
        return "Invalid Link", status.HTTP_400_BAD_REQUEST

    Link = SanitizedData['Link']
    Username = SanitizedData['Username']

    #Run the models feed delete information and return the result.
    Result = RSSModel.User_DeleteFeed(Link, Username)

    return Result, status.HTTP_202_ACCEPTED

#This function takes in input, expected to be a dictonary, and runs it against each input.
#Each input is checked for any invalid characters using a regular expression search.
#Depending on the input TYPE it will be examiend against different conditions.
def CheckForInvalidCharacter(Input):

    for value in Input:
        if value == "Link":
            if not bool(re.search('^[a-zA-Z0-9:/.]+$', Input[value])):
                return True
        elif value == "Username":
            if not bool(re.search('^[a-zA-Z0-9]+$', Input[value])):
                print("Username - ", Input[value])
                return True
        else:
            if not bool(re.search('^[a-z0-9A-Z,.@;:"[}}{|!£$%^&*()-_]+$', Input[value])):
                print("Password - ", Input[value])
                return True

    return False

#Runs a serverside password strength test using serverside code.
def PasswordStrength(Password):
    if len(str(Password)) < 6:
        return True
    elif bool(re.search('^[a-z]+$', Password)):
        return True
    elif bool(re.search('^[0-9]+$', Password)):
        return True
    elif bool(re.search('^[A-Z]+$', Password)):
        return True
    elif bool(re.search('^[a-z0-9]+$', Password)):
        return True
    elif bool(re.search('^[a-zA-Z]+$', Password)):
        return True
    elif bool(re.search('^[0-9A-Z]+$', Password)):
        return True
    elif bool(re.search('^[a-z0-9a-z]+$', Password)):
        return True
    elif bool(re.search('^[,.@;:"[}}{|!£$%^&*()-]+$', Password)):
        return True
    elif bool(re.search('^[a-z,.@;:"[}}{|!£$%^&*()-]+$', Password)):
        return True
    elif bool(re.search('^[A-Z,.@;:"[}}{|!£$%^&*()-]+$', Password)):
        return True
    elif bool(re.search('^[0-9,.@;:"[}}{|!£$%^&*()-]+$', Password)):
        return True
    elif bool(re.search('^[a-z0-9,.@;:"[}}{|!£$%^&*()-]+$', Password)):
        return True
    elif bool(re.search('^[a-zA-Z,.@;:"[}}{|!£$%^&*()-]+$', Password)):
        return True
    elif bool(re.search('^[A-Z0-9,.@;:"[}}{|!£$%^&*()-]+$', Password)):
        return True
    elif bool(re.search('^[a-z0-9A-Z,.@;:"[}}{|!£$%^&*()-_]+$', Password)):
        return False

#Depending on what is passed in, run checks against it.
#Will be used to examine the headers of data passed in against what is expected
#This is done to help prevent any input tampering though header manipulation.
def DataKeyCheck(Data, Headers):
    for value in Data:
        if not value in Headers:
            return True
    return False


#Convert any input into its HTML escaped format using the CGI library
def SanitizeInput(Input):
    for value in Input:
        Input[value] = cgi.escape(str(Input[value]))
    return Input
#Check the passed in web address for appropriate URL information. It will attempt to open the web address and get the code from that for later use
#If that code is not 200, it means either the XML couldn't be parsed, or the web address is not valid
#Added try except for exceptional conditions causing breakage.
def WebAddressExist(WebAddress):

   try:
        status = urllib.request.urlopen(WebAddress).getcode()

        if status == 200:
            Feed = feedparser.parse(WebAddress)
            if not Feed.entries:
                return True
        return False
   except:
        return True






app.run()
