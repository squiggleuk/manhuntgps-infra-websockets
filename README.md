# manhuntgps-infra-websockets

Using the serverless framework, we deploy the following:
 - Lambda functions (Python 3.7)
 - API Gateway (Websockets)
 - DynamoDB

**onConnect** When a client connects for the first time, we send details of all other currently connected players to them. We also add a row for the new client into the database.

**updateLocation** When a client sends a location update, we loop over all rows in the database, and send this update out to all other players. We also handle 401 errors (dead connection), removing these from the database.

**onDisconnect** When a client disconnects, we remove them from the database.


Getting it going...
```
sls plugin install -n serverless-python-requirements
sls deploy
```
