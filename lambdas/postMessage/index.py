import sys
import logging
import rds_config
import pymysql

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
    connection = pymysql.connect(rds_host, user=rds_username,
                                 passwd=rds_password, db=rds_db_name, connect_timeout=5)
except Exception as e:
    logger.error("Error connecting to database: " + str(e))
    sys.exit()

logger.info("Connection to database succeeded")


def validate_event(event):
    """
    Validates the given event and extracts parameters.

    Expected event shape:
    {
        "body-json" : {
            "message": String (max 255 characters),
            "username": String
        },
        "params" : {
            "path" : {},
            "querystring" : {},
            "header" : {}
        },
        "stage-variables" : {}
    }

    returns: {
        "username": string,
        "message": string,
    }
    """
    if type(event) is not dict:
        logger.info(event)
        raise Exception("Bad Request: event is not a dict")

    if "body-json" not in event:
        logger.info(event)
        raise Exception("Bad Request: event['body-json'] missing")

    body = event["body-json"]

    if type(body) is not dict:
        logger.info(event)
        raise Exception("Bad Request: event['body-json'] is not a dict")

    if "username" not in body:
        logger.info(event)
        raise Exception("Bad Request: event['body-json']['username'] missing")

    username = body["username"]

    if type(username) is not str:
        logger.info(event)
        raise Exception(
            "Bad Request: event['body-json']['username'] is not a str")

    if len(username) > 255:
        raise Exception(
            "Bad Request: event['body-json']['username'] can't be larger than 255 characters, but is " + username)

    if "message" not in body:
        logger.info(event)
        raise Exception("Bad Request: event['body-json']['message'] missing")

    message = body["message"]

    if type(message) is not str:
        logger.info(event)
        raise Exception(
            "Bad Request: event['body-json']['message'] is not a str")

    return username, message


def lambda_handler(event, context):
    """
    This is the main method of the lambda function. The default AWS name is lambda_handler.
    The parameter event contains all the parameters from the rest request.
    The parameter context contains a lot of system properties that we don't care about.

    The method executes a an insert into the database with the provided username and message and returns the result.

    The procedure looks like this:

        create procedure insert_message(
            in p_username varchar(255),
            in p_message text
        )
        begin
        insert into messages (username, message) values (p_username, p_message);
        select id, username, message, created_time from messages where id=last_insert_id();
        end

    """
    username, message = validate_event(event)
    with connection.cursor() as cursor:
        statement = "CALL insert_message(%s, %s)"
        cursor.execute(statement, (username, message))
        result = cursor.fetchall()
        logger.info("Inserted message: " + str(result))
        inserted_message = {
            "id": result[0][0],
            "username": result[0][1],
            "message": result[0][2],
            "created_time": str(result[0][3].astimezone()),
        }
        connection.commit()
        return inserted_message
