# aws-lambda-lab
A small lab to get started with aws lambda

# Sign in

# Gateway
Choose new API
Choose API name
Enter some description of the API
Choose endpoint type regional
Hit create

Under the Actions dropdown, select create method
Select Method type GET
Hit the checkmark

In the setup select
Integration type: Lambda Function
Use Lambda Proxy integration: True
Lambda Function: getMessages
Lambda Region: us-west-2
Use Default Timeout: True
Hit Save
Accept the permissions popup

Method Execution

Go to Method Request
Authorization: NONE
Request Validator: Validate query string parameters and headers
API Key Required: false
Under URL Query String Parameters
Create a new parameter
Name: limit
Required: false
Caching: false

Go back to Method Execution
Go to Integration Request
Integration type: Lambda Function
Use Lambda Proxy integration: False
Lambda Region: us-west-2
Lambda Function: getMessages
Execution role: None
Invoke with caller credentials: false
Credentials cache: Do not add caller credentials to cache key
Use Default Timeout: true
Under URL Query String Parameters add a new entry:
Name: limit
Mapped from: method.request.querystring.limit
Caching: false
Under Mapping Templates:
Request body passthrough: When there are no templates defined
Under Content type, add a new mapping template:
Content type: application/json
Generate template: Method Request Passthrough
Hit Save
```
##  See http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html
##  This template will pass through all parameters including path, querystring, header, stage variables, and context through to the integration endpoint via the body/payload
#set($allParams = $input.params())
{
"body-json" : $input.json('$'),
"params" : {
#foreach($type in $allParams.keySet())
    #set($params = $allParams.get($type))
"$type" : {
    #foreach($paramName in $params.keySet())
    "$paramName" : "$util.escapeJavaScript($params.get($paramName))"
        #if($foreach.hasNext),#end
    #end
}
    #if($foreach.hasNext),#end
#end
},
"stage-variables" : {
#foreach($key in $stageVariables.keySet())
"$key" : "$util.escapeJavaScript($stageVariables.get($key))"
    #if($foreach.hasNext),#end
#end
},
"context" : {
    "account-id" : "$context.identity.accountId",
    "api-id" : "$context.apiId",
    "api-key" : "$context.identity.apiKey",
    "authorizer-principal-id" : "$context.authorizer.principalId",
    "caller" : "$context.identity.caller",
    "cognito-authentication-provider" : "$context.identity.cognitoAuthenticationProvider",
    "cognito-authentication-type" : "$context.identity.cognitoAuthenticationType",
    "cognito-identity-id" : "$context.identity.cognitoIdentityId",
    "cognito-identity-pool-id" : "$context.identity.cognitoIdentityPoolId",
    "http-method" : "$context.httpMethod",
    "stage" : "$context.stage",
    "source-ip" : "$context.identity.sourceIp",
    "user" : "$context.identity.user",
    "user-agent" : "$context.identity.userAgent",
    "user-arn" : "$context.identity.userArn",
    "request-id" : "$context.requestId",
    "resource-id" : "$context.resourceId",
    "resource-path" : "$context.resourcePath"
    }
}
```
Go back to Method Execution
Go to Method Response
Add a new Response:
Status Code: 400

Go back to Method Execution
Go to Integration Response
Add a new Integration Response:
Lambda Error Regex: Bad Request.*
Method response status: 400
Content handling: Passthrough

Go back to Method Execution
Go to Test
Test with different request parameters

Create a post method in the same way
This time, we change nothing in the Method request settings
In the Integration Request section, we add a application/json mapping exactly like the one we did in getMessages
In the Method Response section, we add 400 as a possible response code
In the Integration Response section, we add the same mapping as in getMessages
Now we can test the POST method as well!

```
sios:Desktop sios$ mysql -h r2m-academy-lab.c891uj4a8hrg.us-east-2.rds.amazonaws.com -u root -p r2m_academy_lab
Enter password:
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 21
Server version: 8.0.11 Source distribution

Copyright (c) 2000, 2018, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> show tables;
+---------------------------+
| Tables_in_r2m_academy_lab |
+---------------------------+
| messages                  |
+---------------------------+
1 row in set (0.72 sec)

mysql> describe messages;
+--------------+--------------+------+-----+-------------------+----------------+
| Field        | Type         | Null | Key | Default           | Extra          |
+--------------+--------------+------+-----+-------------------+----------------+
| id           | int(11)      | NO   | PRI | NULL              | auto_increment |
| username     | varchar(255) | NO   |     | NULL              |                |
| message      | text         | NO   |     | NULL              |                |
| created_time | datetime     | NO   |     | CURRENT_TIMESTAMP |                |
+--------------+--------------+------+-----+-------------------+----------------+
4 rows in set (0.13 sec)

mysql> select * from messages;
+----+----------+---------------------+---------------------+
| id | username | message             | created_time        |
+----+----------+---------------------+---------------------+
|  1 | sios     | First message whoo! | 2018-11-04 13:00:05 |
+----+----------+---------------------+---------------------+
1 row in set (0.19 sec)```