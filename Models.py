#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      nickw
#
# Created:     01/04/2019
# Copyright:   (c) nickw 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from passlib.hash import argon2
import feedparser
from dateutil.parser import parse
import datetime


#This model will be controlling everything to do that involves the user colletcion inside mongodb
#It consists of three sub-routines that focus on the following;
#UserExistCheck, Which checks for a user inside mongo
#SaveUser, which will save the user into mongos collection
#GetUser, which will find the user and then return that object
class UserModel:
    #Point the initalizer to mongodb's collection by passing in the database object fromt he controller
    def __init__(self, db):
        self.collection = db.users

    #Take in username, then use that to get the result from mongo and if the result is found, return it OR return a none object
    def UserExistCheck(self, Username):
        #Query mongo for the user
        UserEntry = self.collection.find_one({'Username': Username})
        #Perform a simpe if, to determine if the user was found or not.
        if UserEntry == None:
            print(Username, "not found in the database")
            return None

        else:
            print("User Found")
            return UserEntry


    #Save the user, by taking in both the username and password then checking for a prexisting user, and then finally saving.
    def SaveUser(self, Username, Password):
        #Run the UserExistCheck to determine if a user exists or not.
        UserEntry = self.UserExistCheck(Username)
        #Determine the result of the previously executed code
        if UserEntry != None:
            return "User already Exists"

        #Create our user object from the passed in parameters, we also need to pass in none to act as a placeholder for the login time
        User_Object = User(Username, Password, None)
        #Run the objects update login time function which will create its first entry for the login time
        User_Object.UpdateLoginTime()
        #Salt the user objects password
        User_Object.EncryptPassword()
        #Convert the object into a dictonary as you can't save to mongo as an object
        User_Dict = User_Object.__dict__
        #Insert the dictonary into the database, and catch the result
        result = self.collection.insert_one(User_Dict)
        #Display to the server
        print('One post: {0}'.format(result.inserted_id))
        #Return the object to the controller for further use in the templating engine.
        return User_Object
    #Fetch the user from the database using the passed in parameters. Determine a number of different factors, such as if the user exists, or if the password is incorrect ect..
    def GetUser(self, Username, Password):
        #Run the UserExistCheck to determine if a user exists or not.
        UserEntry = self.UserExistCheck(Username)
        #Determine the result of the previously executed code
        if UserEntry == None:
            return None, "User Doesnt Exist"

        #Pop the results _id result from mongodb, for both security purposes and our object doesn't use this as a field
        UserEntry.pop('_id')
        #Transform our returned database entry into a user object
        UserEntry = User(UserEntry['Username'], UserEntry['Password'], UserEntry['LastLogin'])

        #Run the password against the user objects salted password to determine verification
        if UserEntry.VerifyPassword(Password):
            print(Username, " was found and password verified")
            return UserEntry, ("User Found, Password Verified")
        else:
            print(Username, " was found, Password Incorrect")
            return None, ("User Found, Password Incorrect")

    #Execute the update time to update the database to match the latest login from the user
    def UpdateTime(self, UserObject):
        self.collection.update_one({'Username': UserObject.GetUsername()}, {"$set": {"LastLogin": UserObject.UpdateLoginTime()}})



#This class models a user object that will allow the user object to be represented in the system
#It contains multiple functions that allow the RSS feed system to function;
#Amoung the usual getters and setters there are unique functions that are made use of
#UpdateLoginTime allows the user to update their current time to match the current system time
#Encrypt password, which mades use of the argon2 encryption package to convert the database password into a 4 rounded hash and salted password.
#Verify Password which allows the user to feed in a raw password, and compare this to the hash and salted password
class User:
    def __init__(self, Username, Password, LastLogin):
        self.Username = ""
        self.Password = ""
        self.LastLogin = ""
        self.SetUsername(Username)
        self.SetPassword(Password)
        self.SetLastLogin(LastLogin)

    def SetLastLogin(self, LastLogin):
        self.LastLogin = LastLogin

    #This function updates the current system time. for some reason, an issue exists revolving around GMT summer and winter times. When grabbing the data from the service it recieves it in winter time,
    #However when saving it still saves in summer time, meaning that any posts in the previous hour are classified as being an hour in the past.
    #As such I have implimented the addition of an hour to any future use of date time in a class system.
    def UpdateLoginTime(self):
        CurrentTime =  parse(str(datetime.datetime.astimezone(datetime.datetime.now()+ datetime.timedelta(hours=1))))
        self.LastLogin = CurrentTime
        return self.LastLogin

    def GetLastLogin(self):
        return  parse(str(datetime.datetime.astimezone(self.LastLogin)))

    def GetFeeds(self):
        return self.Feeds

    def UpdateFeeds(self):
        self.Feeds.append(Feed)

    def SetUsername(self, Username):
        self.Username = Username

    def SetPassword(self, Password):
        self.Password = Password

    def GetUsername(self):
        return self.Username

    def GetPassword(self):
        return self.Password

    #This function makes use of the password encryption library which includes argon2 conversion.
    #Argon2 includes salting with the inital hash so there is no need to independently include this
    def EncryptPassword(self):
        self.Password = argon2.using(rounds=4).hash(self.Password)


    #This function verifys the password by feeding in the attempted password and running argon2's verify function to compare the two, return the appropriate result.
    def VerifyPassword(self, attempt):
        if argon2.verify(attempt, self.GetPassword()):
            return True
        else:
            return False

#This record class models the record of each RSS feed. Therefore each RSS feed has many related records inside it
class Record:
    #Each Record is linked to a feed, a feed contains many Records
    def __init__(self, Origin, Title, Summary, Link, Published):
        #Control Data
        self.BelongsTo = ""
        #Internal Data
        self.Title = ""
        self.Summary = ""
        self.Link = ""
        self.Published = ""
        self.GenerateRecord(Origin, Title, Summary, Link, Published)

    #This generate record takes in passed data and populates the records object data
    def GenerateRecord(self, Origin, Title, Summary, Link, Published):
        self.SetBelongsTo(Origin)
        self.SetTitle(Title)
        self.SetSummary(Summary)
        self.SetLink(Link)
        self.SetPublished(Published)

    def SetBelongsTo(self, Value):
        self.BelongsTo = Value

    def GetBelongsTo(self):
        return self.BelongsTo

    def SetTitle(self, Value):
        self.Title = Value

    def GetTitle(self):
        return self.Title

    def SetSummary(self, Value):
        self.Summary = Value

    def GetSummary(self):
        return self.Summary

    def SetLink(self, Value):
        self.Link = Value

    def GetLink(self):
        return self.Link

    #Published date is related to the time that article was uploaded to website
    def SetPublished(self, Value):
        #Use the parse module to convert the raw feed into a date time format.
        Published = parse(str(Value))
        self.Published =parse(str(datetime.datetime.astimezone(Published)))

    def GetPublished(self):
        return parse(str(datetime.datetime.astimezone(self.Published)))

    #Not used anymore
    def PublishedStringConvert(self):
        self.Published = self.Published



import json

#The RSS Feed controls any use of the RSS class, the RSS class is largely made
#up of records and small bits of information to create the RSS feed object.
#It contains a large amount of functions that do some seemly strange things on first inspection
#Load data is similar to the record, it just injects the rss feed object with the data required to use it.
#Records to dictonarys works as mongodb doesn't allow object storing so you have to convert the records contained in the RSS object into a dictonary
#Records to objects is the inverse of this, and converts the dictonary result into an object for use in the system.
#Checkifaccessed function allows the user to check the accessed dictonary to see if a user has accessed this rss feed before, and if so when.
#Removed access does the same, except removes the users record from the dictonary.
#InitalParseResult is the inital creation of RSS object when it has never been created before, otherwise update parser is used which will add the latest records into the database
#UserViewed updates the users record to show that the user accessed that rss feed and at what time
class RSS:
    def __init__(self, Link):

        self.UsersAccessed = []
        self.Link = ""
        self.Records = []
        self.LastUpdated = ""

        self.SetLink(Link)

    #Loads in the data to populate the object
    def LoadData(self, UsersAccessed, Records, LastUpdated):
        self.UsersAccessed = UsersAccessed
        self.Records = Records
        self.LastUpdated = LastUpdated


    def AddRecord(self, Record):
        self.Records.append(Record)

    def GetRecords(self):
        return self.Records
    #See description above, simply creates a array of dictonarys, converts the records to strings and appends them.
    def RecordsToDictonary(self):
        Dictonarys = []
        #Convert objects to dictonary so python can dump them as a json
        for Record in self.Records:
            Record.PublishedStringConvert()
            Dictonarys.append(Record.__dict__)

        self.Records = Dictonarys
    #See description above, simply updates self records to contain the new up to date list of records as an object
    def RecordsToObjects(self):
        Objects = []
        for Result in self.Records:
            Title = Result['Title']
            Summary = Result['Summary']
            Link = Result['Link']
            Published = Result['Published']
            New_Record = Record(self.Link, Title, Summary, Link, Published)
            Objects.append(New_Record)

        self.Records = Objects

    def SetLink(self, Value):
        self.Link = Value

    def GetLink(self):
        return self.Link

    def GetAccessed(self):
        return self.UsersAccessed

    #each entry in the users accessed array is checked for the user matching, if a match is found, return the appropriate result
    def CheckIfUserAccessed(self, username):
        for entry in self.UsersAccessed:
            if entry['Username'] == username:
                print("User has accessed before")
                return True
        return False
    #Removes an entry from users accessed
    def RemoveAccessed(self, username):
        for entry in self.UsersAccessed:
            if entry['Username'] == username:
                self.UsersAccessed.remove(entry)
    #updates the time of the object to the time of calling, see preevious objects descriptions for why.
    def SetLastUpdated(self):
        CurrentTime =  parse(str(datetime.datetime.astimezone(datetime.datetime.now())+ datetime.timedelta(hours=1)))
        self.LastUpdated = CurrentTime

    def GetLastUpdated(self):
        return parse(str(datetime.datetime.astimezone(self.LastUpdated)))
    #Inital parser uses the parse package and is fed a link, this results in a cursor object which we can use
    #to convert the returned result into a collection of objects within the object
    def InitalParseResult(self):
        Feed = feedparser.parse(self.GetLink())
        for Result in Feed.entries:
            Title = Result['title']
            Summary = Result['summary']
            Link = Result['link']
            Published = Result['published']
            New_Record = Record(self.Link, Title, Summary, Link, Published)
            self.AddRecord(New_Record)
        #Call this function to update the last updated field in the feed.
        self.SetLastUpdated()

    #Does the same as inital parse, except adds in a section for checking if that record currently exists.
    #If a record is parsed and found to be newer than the the update time of the RSS feed, append it to the list.
    def UpdateParser(self):
        Feed = feedparser.parse(self.GetLink())
        for Result in Feed.entries:
            Title = Result['title']
            Summary = Result['summary']
            Link = Result['link']
            Published = Result['published']
            New_Record = Record(self.Link, Title, Summary, Link, Published)

            if New_Record.GetPublished() > self.GetLastUpdated():


                self.AddRecord(New_Record)

        self.SetLastUpdated()

    #Append the user viewed field to include the latest time a user has accessed this RSS feed.
    def UserViewed(self, Username):
        CurrentTime =  parse(str(datetime.datetime.astimezone(datetime.datetime.now())))

        for entry in self.UsersAccessed:
            if entry['Username'] == Username:
                entry['Time'] = CurrentTime
                return


        self.UsersAccessed.append({"Username": Username, "Time": CurrentTime})


    #NOT USED, previously used to convert to JSON and return the result to the controller, no longer needed.
    def StringifyResult(self):
        Objects = []
        #Convert objects to dictonary so python can dump them as a json
        #for Record in self.Records:
            #Record.PublishedStringConvert()
            #Objects.append(Record.__dict__)

        #Convert Object dictonary list to JSON and return
        JSON = json.dumps(Objects)
        return JSON

#This model handles a large amount of the heavy duty work found when interacting with the RSS Feeds. as such is more complex then that its usermodel counterpart
#It consists of nine seperate functions that are used to interact and modify the database. Each of these generally returns results
#LoadDataToObject - As found with previous model, mongodb doesn't take objects in as a raw save instead it needs to be saved as a JSON or dictonary.
#Therefore this function takes in the feed previously obtained by the database and converts it into an object, returning the object.
#UserAccessFeed - This function finds the appropriate feed from the database and captures it based on the link (Acting as primary key), Then updates the appropriate information
#To show that a use has accessed this feed.
#UserAccessAllFeeds - Same as above however it does it for each feed that a user has saved.
#AccessFeed - This is used to access ONE feed independently of interacting with the user accessed variable. This is done as there was a need to load a feed that may not need saved
#SaveRSSFeed - this function finds a feed and if a feed is found pass it into the access feed, and if not found call the save feed to save it and access at the same time.
#SaveFeed - this is used by the previous stated function to save the feed by inserting into the database
#ParseFeed - Isn't used but used to be used to return a parsed JSON feed back to the controller.
#UpdateUserAccessed - this function simply appends the user accessed field in the database to match the most up to date version within the passed in object
#User_DeleteFeed - This feature allows the use to delete a feed assosiated with their account
#DeleteUserAllAccessed - Not used but may find use for future.
class RSSModel:
    def __init__(self, db):
        self.collection = db.Feeds
    #Query database, if a match is found call the access feed and pass in the link, otherwise save the feed instead.
    def SaveRSSFeed(self, link):
        Feed = self.collection.find_one({'Link': link})

        if Feed == None:
            return self.SaveFeed(link)

        else:
            return self.AccessFeed(link)

    #See previous examples for explanation, simply loads data into object form.
    def LoadDataToObject(self, link, Feed):

        UsersAccessed = Feed['UsersAccessed']
        Records = Feed['Records']
        LastUpdated = Feed['LastUpdated']

        Object = RSS(link)

        Object.LoadData(UsersAccessed, Records, LastUpdated)

        return Object


    #User queried database, if a feed is found, save the feed and update that a user viewed it, otherwise load that information
    def UserAccessFeed(self, link, Username):

        Returned_Feed = self.collection.find_one({'Link': link})

        if Returned_Feed == None:
            Feed = self.SaveFeed(link)
        else:
            Feed = self.LoadDataToObject(link, Returned_Feed)
            if Feed.CheckIfUserAccessed(Username):
                return True
        #Update the feeds information to include the current time saying that they accessed the feed.
        Feed.UserViewed(Username)
        #Update the record inside the database
        self.UpdateUserAccessed(link, Feed)

        return False
    #A more complex version of the previous function
    #This function finds all where an element match is found with the username, if records are found develop two lists, one that contains the feed itself, the other that contains the consolidated list
    #The consolidated list allows the front end to produce a condensed list of feeds indepedent of the RSS object.
    def UserAccessAllFeeds(self, User):
        Returned_Feeds = self.collection.find({'UsersAccessed' : {"$elemMatch": {"Username": User.GetUsername()}}})

        if Returned_Feeds == None:
            return "None found"
        else:
            FeedArray = []
            Consolidated_List = []
            #For each entry in the feed, convert it to an object andrun its functions too update it
            for feed in Returned_Feeds:
                FeedObject = self.LoadDataToObject(feed['Link'], feed)
                FeedObject.RecordsToObjects()
                FeedObject.UpdateParser()
                #Convert the records back into a dictonary for saving to the database using an update method
                FeedObject.RecordsToDictonary()
                FeedDict = FeedObject.__dict__

                result = self.collection.update_one({'Link': FeedDict['Link']}, {"$set": {"Records": FeedDict['Records'],"LastUpdated": FeedDict['LastUpdated']}})
                #convert the dictonary back into an object for use later by the controller
                FeedObject.RecordsToObjects()
                #Compare time stamps and develop the consolidated list
                for Record in FeedObject.GetRecords():
                    if Record.GetPublished() > User.GetLastLogin():
                        Consolidated_List.append(Record)


                FeedArray.append(FeedObject)

        return FeedArray, Consolidated_List

    #Access Feed for users who have just queried RSS feed NOT saving it
    def AccessFeed(self, link):
        Returned_Feed = self.collection.find_one({'Link': link})

        Feed = self.LoadDataToObject(link, Returned_Feed)

        return Feed


    def SaveFeed(self, link):
        #Build the object
        Feed = RSS(link)
        #Develop the feed
        Feed.InitalParseResult()
        #The returned feed is capture for return
        Returned_Feed = Feed
        #Convert data for saving
        Feed.RecordsToDictonary()
        #feed object is converted
        Feed = Feed.__dict__
        #insert the data and return it.
        result = self.collection.insert_one(Feed)
        print('One post: {0}'.format(result.inserted_id))
        return Returned_Feed

    #Not used
    def ParseFeed(self, Feed):
        Feed.RecordsToObjects()

        return Feed.StringifyResult()
    #Call an update function to convert the users accesesed to the latest version
    def UpdateUserAccessed(self, link, Feed):
        result = self.collection.update_one({'Link': link}, {"$set": {"UsersAccessed": Feed.GetAccessed()}})

    #Delete the feed's entry in the useers accessed that the system uses to assosiate it with their account.
    def User_DeleteFeed(self, link, Username):
        #Find the entry in the database
        Returned_Feed = self.collection.find_one({'Link': link})
        #Convert the entry to an object
        Feed = self.LoadDataToObject(link, Returned_Feed)
        #Call the function to remove the access from the user
        Feed.RemoveAccessed(Username)
        #Update the record in teh database
        result = self.collection.update_one({'Link': link}, {"$set": {"UsersAccessed": Feed.GetAccessed()}})

        return "This feed has been removed from your account"


    #Built to impliment future access of the deletion of a user acount.
    def DeleteUserAllAccessed(self, Username):
        Returned_Feeds = self.collection.find({'UsersAccessed' : {"$elemMatch": {"Username": Username}}})

        if Returned_Feeds == None:
            return "None found"
        else:
            for feed in Returned_Feeds:
                Feed = self.LoadDataToObject(Returned_Feeds['link'], Returned_Feed)

                print(Username)

                Feed.RemoveAccessed(Username)

                result = self.collection.update_one({'Link': link}, {"$set": {"UsersAccessed": Feed.GetAccessed()}})


