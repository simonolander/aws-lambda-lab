import sys
import logging
import rds_config
import pymysql
import json

""" Fetching config information and credentials from rds_config.py """
rds_host = rds_config.rds_host
rds_username = rds_config.rds_username
rds_password = rds_config.rds_password
rds_db_name = rds_config.rds_db_name

""" Setting up logging """
logger = logging.getLogger()
logger.setLevel(logging.INFO)

"""
Setting up database connection. 
This is done outside the lambda handler because we don't need to initialize the connection every time we run the lambda
"""
try:
    conn = pymysql.connect(rds_host, user=rds_username, passwd=rds_password, db=rds_db_name, connect_timeout=5)
except Exception as e:
    logger.error("Error connecting to database: " + str(e))
    sys.exit()

logger.info("SUCCESS: Connection to database succeeded")

"""
Validates the given event and extracts parameters.

Expected event shape:
{
    "body-json" : {},
    "params" : {
    "path" : {},
    "querystring" : {
        "limit" : (string between 0 and 2**31-1, or nothing)
    },
    "header" : {}
    },
    "stage-variables" : {}
}

returns: {
    "limit": int
}
"""
def validate_event(event):
    if type(event) is not dict:
        logger.info(event)
        raise Exception("Bad Request: event is not a dict")

    if "params" not in event:
        logger.info(event)
        raise Exception("Bad Request: event['params'] missing")

    params = event["params"]

    if type(params) is not dict:
        logger.info(event)
        raise Exception("Bad Request: event['params'] is not a dict")

    if "querystring" not in params:
        logger.info(event)
        raise Exception("Bad Request: event['params']['querystring'] missing")

    querystring = params["querystring"]

    if type(querystring) is not dict:
        logger.info(event)
        raise Exception("Bad Request: event['params']['querystring'] is not a dict")

    max_limit = 2147483647
    if "limit" in querystring:
        try:
            limit = int(querystring["limit"])
            if limit < 0:
                logger.info(event)
                raise Exception("Bad Request: event['params']['querystring']['limit'] can't be negative but is " + querystring["limit"])
            if limit > max_limit:
                logger.info(event)
                raise Exception("Bad Request: event['params']['querystring']['limit'] can't be greater than " 
                                + str(max_limit) + " but is " + querystring["limit"])
        except ValueError:
            raise Exception("Bad Request: event['params']['querystring']['limit'] '" + querystring["limit"] + "' is not a valid number")
    else:
        limit = max_limit

    return {
        "limit": limit
    }

"""
This is the main method of the lambda function. The default AWS name is lambda_handler.
The parameter event contains all the parameters from the rest request.
The parameter context contains a lot of system properties that we don't care about.

The method executes a select against the database connection and returns the result as a list of dicts.
"""
def lambda_handler(event, context):
    parameters = validate_event(event)
    with conn.cursor() as cur:
        sql = "SELECT id, username, message, created_time FROM messages ORDER BY created_time DESC LIMIT %s"
        cur.execute(sql, (parameters["limit"],))
        conn.commit()
        return [
            {
                "id": row[0],
                "username": row[1],
                "message": row[2],
                "created_time": str(row[3].astimezone()),
            }
            for row in cur
        ]
