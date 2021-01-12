# Vonage Video Transcription
Transcription Server using AWS Transcription Streams.

### Python Dependencies
- flask
- flask_socketio
- flask_cors
- asyncio
- amazon_transcribe
- webrtcvad
- pprint
- requests
- uuid

### Setup (Debian Linux)
1. clone this repo
2. install python3: `sudo apt-get install python3.7`
3. install pip3: `sudo apt-get install python3-pip`
4. install dependencies: `pip3 install -r requirements.txt`
5. navigate into build directory: `cd src/build`
6. build native linux application: `make`
7. navigate back to source directory: `cd ..`
8. run python server: `python3.7 server.py`

# Using the application

### REST: Start Transcribe
```
POST /transcribe

body:
{
  "apiKey": API_KEY,
  "sessionId": SESSION_ID,
  "token": TOKEN
}
```

Response
```
{
  "status": STRING [started]
}
```

### REST: Stop Transcribe
```
DELETE /transcribe/:sessionId
```

Response
```
{
  "status": STRING [stopped/not_exist]
}
```

### REST Check Transcribe Existence
```
GET /transcribe/:sessionId
```

Response
```
{
  "exist": BOOLEAN
}
```


### SocketIO Join Room
```
event: join
data:
{
  "room": SESSION_ID
}
```

### SocketIO Leave Room
```
event: leave
data:
{
  "room": SESSION_ID
}
```