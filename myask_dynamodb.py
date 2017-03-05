# coding: utf-8
################################################################################
#
# myask_dynamodb : functions for storing user profile info in dynamodb
#
#-------------------------------------------------------------------------------
# https://github.com/acmurmeltier69/myask
# Written 2017 by acmurmeltier69 (acmurmeltier69@mnbvcx.eu)
# Shared under GNU GENERAL PUBLIC LICENSE Version 3
# https://github.com/acmurmeltier69/myask
#-------------------------------------------------------------------------------
# Notes:
# In order to use dynamo db, you need a valid aws account with dynamo db correctly configured
# When used locally, the system uses the credentials in the file ~/.aws/credentials
# This library can be used with the online dynamoDB server or a local server 
# --> change function _getDynamoDB accordingly
################################################################################
from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
import datetime 
from botocore.exceptions import ClientError
import myask_log
import argparse
import os

os.environ["TZ"] = "CET"

DBTYPE = "online"
DBRESOURCE = "eu-west-1"

def SetDbType(dbtype, resource=""):
    global DBTYPE
    global DBRESOURCE
    
    myask_log.debug(3, "myadk_dynamodb.SetDbType: dbtype='"+dbtype+"' resource='"+resource+"'")
    DBRESOURCE = resource
    if dbtype == "online": # use dynamo online db
        DBTYPE = "online"
        return True
    elif dbtype == "offline": # use dynamo  db installed locally
        DBTYPE = "offline"
        return True
    else:
        myask_log.error("myadk_dynamodb.SetDbType: invalid dbtype '"+dbtype+"'")
        return False
    
def _getDynamoDB():
    #--------------------------------------------------------------------------
    # helper function to return a resource pointing to dynamodb server
    #--------------------------------------------------------------------------
    global DBTYPE
    global DBRESOURCE
    if DBTYPE == "online": # use dynamo online db
        dynamodb = boto3.resource('dynamodb', region_name=DBRESOURCE)
    elif DBTYPE == "offline": # use dynamo  db installed locally
        dynamodb = boto3.resource('dynamodb', endpoint_url=DBRESOURCE)
    

    return dynamodb

def get_date_str():
    #--------------------------------------------------------------------------
    # returns a string for the current date in the form YYYY-MM-DD_hh:mm
    #--------------------------------------------------------------------------
    i = datetime.datetime.now()
    return  i.isoformat()   

class DecimalEncoder(json.JSONEncoder):
    #--------------------------------------------------------------------------
    # Helper class to convert a DynamoDB item to JSON.
    #--------------------------------------------------------------------------
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)



class dynamoDB:
    #--------------------------------------------------------------------------
    # class to manage access to the dynamodb user profile
    #--------------------------------------------------------------------------
    
    _dynamodb = ""
    _table = ""
    _sucess = "UNINITIALIZED"
    
    def __init__(self, tablename):
        #-----------------------------------------------------------------------
        # initialize a new dynamo db object by loading the table 'tablename'
        # The success information is stored in _success
        # The calling function must check this with GetStatus() call (should be "OK")
        #-----------------------------------------------------------------------
       
        self._table = ""
        self._dynamodb = _getDynamoDB()
        self._table = self._dynamodb.Table(tablename)

        
        self._sucess = "OK"

    def GetStatus(self):
        #-----------------------------------------------------------------------
        #  checks if last table was successful.
        # If yes, the system returns "OK".
        # Else a specific error string is returned
        #-----------------------------------------------------------------------
        return self._sucess
    
     
    def CreateNewUserProfile(self, userid, profile):
        #-----------------------------------------------------------------------
        # Creates a new user profile for the specified id
        # If the user profile already exists it is overwritten
        #-----------------------------------------------------------------------
        response = self._table.put_item(
            Item={
                    'UserID': userid,
                    'Created' : get_date_str(),
                    'NumQueries': 0,
                    'LastQuery': get_date_str(), 
                    'Profile': profile
                 })
        return response
    
    def _touchProfile(self, userid):
        response = self._table.update_item(
                    Key={'UserID': userid},
                    UpdateExpression="set NumQueries = NumQueries + :val, LastQuery = :t",
                    ExpressionAttributeValues = {
                            ':val': decimal.Decimal(1),
                            ':t' : get_date_str()
                    },
                    ReturnValues="UPDATED_NEW")
        myask_log.debug(5, "Updating UserProfileTimeStamps: " + str(response))

        return True
 
    def GetStatistics(self, userid):
        created = ""
        num_queries = -1
        last_query = ""
        
        if self._table == "": 
            myask_log.error("GetStatistics: attempted without valid table")
        try:
            response = self._table.get_item(Key={'UserID': userid})
        except ClientError as e:
            myask_log.error("GetStatistics: Error: "+e.response['Error']['Message'])
        else:
            if 'Item' in response:
                if 'Created' in response['Item']: created = response['Item']['Created']
                if 'NumQueries' in response['Item']: num_queries = response['Item']['NumQueries']
                if 'LastQuery' in response['Item']: last_query = response['Item']['LastQuery']
            else:
                myask_log.debug(5,"GetStatistics: User profile NOT found:"+ str(userid))

        return [created,num_queries,last_query]
        
        
    def FetchUserProfile(self, userid):
        #-----------------------------------------------------------------------
        # returns the "profile" part of a given user profile
        # if the user profile does not exist, profile is {}
        #-----------------------------------------------------------------------
        if self._table == "": 
            myask_log.error("fetchUserProfile: attempted without valid table")
            return {}
        try:
            response = self._table.get_item(Key={'UserID': userid})
        except ClientError as e:
            myask_log.error("fetchUserProfile: Error: "+e.response['Error']['Message'])
            return {}
        else:
            if 'Item' in response:
                if 'Item' in response and 'Profile' in response['Item']:
                    profile = response['Item']['Profile']
                    myask_log.debug(5,"fetchUserProfile: User profile found:"+ str(userid))
                    # update access log for this user profile
                    self._touchProfile(userid)
                    return profile
                else :
                    myask_log.debug(5,"fetchUserProfile: Invalid response format: "+ str(response))
                    return {}
            else:
                myask_log.debug(5,"fetchUserProfile: User profile NOT found:"+ str(userid))
                return {}

    def UpdateUserProfile(self, userid, profile):
        #-----------------------------------------------------------------------
        # Updates an existing user profile with the information in "profile"
        # If the user profile does not exist or cannot beupdated, returns False
        #-----------------------------------------------------------------------
        try:
            response = self._table.update_item(
                            Key={'UserID': userid},
                            UpdateExpression="set Profile = :p",
                            ExpressionAttributeValues = {':p':  profile},
                            ReturnValues="UPDATED_NEW")
        except ClientError as e:
            myask_log.error("UpdateUserProfile: Error: "+e.response['Error']['Message'])
            return False
        else:
            myask_log.debug(2, "UpdateUserProfile: " + str(response))

        return True

    def DeleteUserProfile(self, userid):
        #----------------------------------------------------------------------
        # delete a specific user profile from the table
        #----------------------------------------------------------------------
        
        try:
            self._table.delete_item(Key={'UserID': userid})
        except ClientError as e:
            myask_log.error("DeleteUserProfile: Error: "+e.response['Error']['Message'])
            return False
        else:
            print("DeleteItem succeeded")
            return True

    def printProfileSummary(self, dbitem, profilefields):
        user_id = "---"
        created = "---"
        num_queries = -1
        last_query = "---"
        profile = {}
        if 'UserID' in dbitem:
            user_id = str(dbitem['UserID'])[:25]            
        if 'NumQueries' in dbitem:
            num_queries = int(dbitem['NumQueries'])
        if 'Created' in dbitem:
            created = str(dbitem['Created'])[:16]
        if 'LastQuery' in dbitem:
            last_query = str(dbitem['LastQuery'])[:16]
        res_str = "UserID: {:25s} #:{:5d} Created: {:17s} Last: {:17s}:".format(user_id, num_queries, created, last_query)
            
        if 'Profile' in dbitem:
            res_str += "Profile: {"
            if profilefields == ["ALL"]:
                res_str+= str(dbitem['Profile'])
            else:
                for field in profilefields:
                    if field in dbitem['Profile']:
                        res_str += "'"+field +"' : '"+ str(dbitem['Profile'][field]) +"'"
            res_str += "}"
        print(res_str)
        
        
    def ScanAllProfiles(self, profilefields=["ALL"]):
        response = self._table.scan()

        for i in response['Items']:
            self.printProfileSummary(i, profilefields)
            while 'LastEvaluatedKey' in response:
                response = self._table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])

                for i in response['Items']:
                    self.printProfileSummary(i, profilefields)
                    
################################################################################
#  end of class dynamoDB
################################################################################

def CreateNewTable(tablename):
    dynamodb = _getDynamoDB()
    table = dynamodb.create_table(
            TableName= tablename,
            KeySchema=[
                {
                    'AttributeName': 'UserID',
                    'KeyType': 'HASH'  #Partition key
                }
            ],
            AttributeDefinitions=[
               {
                   'AttributeName': 'UserID',
                   'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            })

    table_status = table.table_status
    myask_log.debug(0, "Created table '"+tablename+"'. Table status:" + table_status)
    return table_status

################################################################################
#
# function for command line usage
#
################################################################################
#-------------------------------------------------------------------------------


def readJsonProfileFromFile(filename):   
    try:
        jsonfile = open(filename, 'r')
        profile = json.load(jsonfile)
    except IOError:
        print( "cannot read file '"+filename+"'")
    except:
        print("Unexpected error when reading json:", sys.exc_info()[0])
        raise
    else:
        print(" profile: "+str(profile))
        return profile
    
def main():
    # parse command line options
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", type=int,
                        help="define output verbosity")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-create", "--create_table", action="store_true",
                        help="Creates new database table")
    group.add_argument("-scan", "--scan_items", action="store_true",
                        help="Prints summary of complete scan of profiles")
    group.add_argument("-get", "--get_item", type=str,
                        help="Returns profile for given user ID")
    group.add_argument("-stat", "--item_statistics", type=str,
                        help="Returns access statistics for given user ID")
    group.add_argument("-add", "--add_item", type=str,
                        help="Add item with given ID to the database")
    group.add_argument("-upd", "--update_item", type=str,
                        help="Update item with given ID in the database")
    group.add_argument("-del", "--delete_item", type=str,
                        help="Delete item with given ID from the database")
    parser.add_argument("-profile", "--Profile_JSON_FILE", type=str, 
                        help="JSON file with user profile structure")
    parser.add_argument("-offline", "--offline_port", type=int, 
                        help="Use local database on the given port on localhost")
    parser.add_argument("table", help="database table name")

    args = parser.parse_args()    
    
    if  args.table: tablename = args.table
    else: tablename = "TABLE"
    

    if args.verbosity:
        myask_log.SetDebugLevel(args.verbosity)
        
    if args.offline_port:
        offline_endpoint  = "http://localhost:"+str(args.offline_port)
        SetDbType("offline", offline_endpoint)
        
    if args.create_table:
        CreateNewTable(tablename)    
    else:
        databasetable = dynamoDB(tablename)
        if args.scan_items:
            myask_log.debug(5, "Printing statistics")
            databasetable.ScanAllProfiles(["source"])
        elif args.get_item:
            user_id = str(args.get_item)
            myask_log.debug(5, "Fetching item '"+user_id+"'")
            profile = databasetable.FetchUserProfile(user_id)
            print("Profile for user "+user_id+":")
            print(profile)
        elif args.item_statistics:
            user_id = str(args.item_statistics)
            (created,num_queries,last_query) =  databasetable.GetStatistics(user_id)
            print ("Created    : "+created)
            print ("Last Query : "+last_query)
            print ("Num queries: "+str(num_queries))
        elif args.add_item:
            user_id = str(args.add_item)
            myask_log.debug(5, "Adding new item '"+str(user_id)+"'")
            if args.Profile_JSON_FILE:
                profile = readJsonProfileFromFile(args.Profile_JSON_FILE)
            else:
                profile = {}
            databasetable.CreateNewUserProfile(user_id, profile)
        elif args.update_item:
            user_id = str(args.update_item)
            myask_log.debug(5, "Updating item '"+str(user_id)+"'")
            if args.Profile_JSON_FILE:
                profile = readJsonProfileFromFile(args.Profile_JSON_FILE)
            else:
                profile = {}
            databasetable.UpdateUserProfile(user_id, profile)
        elif args.delete_item:
            user_id = str(args.delete_item)
            myask_log.debug(5, "Deleting item '"+user_id+"'")
            databasetable.DeleteUserProfile(user_id)
        else:
            myask_log.error("Missing command")
            parser.print_help()
    
if __name__ == "__main__":
    main()