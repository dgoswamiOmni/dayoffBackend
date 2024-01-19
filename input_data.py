CREATE_TRIP = {
    "headers": {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXZhcnNoaSIsImV4cCI6MTcwNTYyODAyMiwiaWF0IjoxNzA1NTQxNjIyLCJqdGkiOiI3NjQ1NTcyMjUwIn0.9CHZ75fDlBX3okQHfFfdEvOXGGEXeqQprK1fYflQMT4"
    },
    "body": "{\"date\":\"2023-12-31\",\"username\":\"bruno\",\"time\":\"12:00 PM\",\"location\":\"Example Location\",\"description\":\"Example Description\"}"
}

JOIN_TRIP = {
    "headers": {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXZhcnNoaSIsImV4cCI6MTcwMzE3ODg5MiwiaWF0IjoxNzAzMDkyNDkyLCJqdGkiOiI2NWY3OTYzYi01MDllLTQ1ODEtYTVmMS00YjY0MmM1ZTkyOGUifQ.6LxyHqxZdN-I8DHQ8gNg4HvXBpRTRmnaqTvR-IETQPE"
    },
    "body": "{\"date\":\"2023-12-31\",\"time\":\"12:00 PM\",\"username\":\"bruno\",\"location\":\"Example Location\",\"description\":\"Example Description\",\"trip_id\":\"827deebe-f88a-447f-a3f8-81a2e89e3484\"}"
}
INVITE_TRIP = {
    "headers": {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXZhcnNoaSIsImV4cCI6MTcwMzE3ODg5MiwiaWF0IjoxNzAzMDkyNDkyLCJqdGkiOiI2NWY3OTYzYi01MDllLTQ1ODEtYTVmMS00YjY0MmM1ZTkyOGUifQ.6LxyHqxZdN-I8DHQ8gNg4HvXBpRTRmnaqTvR-IETQPE"
    },
    "body": "{\"date\":\"2023-12-31\",\"time\":\"12:00 PM\",\"username\":\"devarshi\",\"location\":\"Example Location\",\"description\":\"Example Description\",\"trip_id\":\"827deebe-f88a-447f-a3f8-81a2e89e3484\"}"
}

SEND_MESSAGE = {"headers": {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXZhcnNoaSIsImV4cCI6MTcwNTYyODAyMiwiaWF0IjoxNzA1NTQxNjIyLCJqdGkiOiI3NjQ1NTcyMjUwIn0.9CHZ75fDlBX3okQHfFfdEvOXGGEXeqQprK1fYflQMT4"
    },
    "body": "{\"date\":\"2023-12-31\",\"time\":\"12:00 PM\",\"username\":\"bruno\",\"room_id\":\"0123456789\",\"message\":\"Hello!\"}"
}