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
2. install native dependencies (for cairo): `sudo apt-get install libcairo2-dev libjpeg-dev libgif-dev`
3. install python3: `sudo apt-get install python3.7`
4. install pip3: `sudo apt-get install python3-pip`
5. install dependencies: `pip3 install -r requirements.txt`
6. navigate into build directory: `cd src/build`
7. build native linux application: `make`
8. navigate back to source directory: `cd ..`
9. run python server: `python3.7 server.py`

# Using the application

### REST: Start Transcribe
```
POST /transcribe

body:
{
  "apiKey": API_KEY,
  "sessionId": SESSION_ID,
  "token": TOKEN,
  "filterEnabled": ENABLED [BOOLEAN]
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
direction: sent from client to server
event: join
data:
{
  "room": SESSION_ID
}
```

### SocketIO Leave Room
```
direction: sent from client to server
event: leave
data:
{
  "room": SESSION_ID
}
```

### SocketIO Transcription Text
```
direction: sent from server to client
event: transcription,
data: TRANSCRIPTION_TEXT (STRING),
```