# Vonage Video Transcription
Transcription Server using AWS Transcription Streams.

### Setup (Debian Linux)
1. clone this repo
2. install native dependencies (for cairo): `sudo apt-get install libcairo2-dev libjpeg-dev libgif-dev`
3. install opentok dependency: `sudo apt-get install libopentok-dev`
4. install python3: `sudo apt-get install python3.7`
5. install pip3: `sudo apt-get install python3-pip`
6. install dependencies: `pip3 install -r requirements.txt`
7. create empty build directory: `mkdir src/build`
8. navigate into build directory: `cd src/build`
9. run cmake `CC=clang CXX=clang++ cmake ..`
10. build native linux application: `make`
11. navigate back to source directory: `cd ..`
12. run python server: `python3.7 server.py`

Refer here for more information on compiling: https://github.com/nexmo-se/vonage-custom-audio_renderer

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

## Running with docker

build the docker image running

`docker build opentok-transcribe-overai .`

Make sure to replace `<KEY> , <SECRET> and <REGION>` with proper aws credentials


and then run it with

`docker run -p 5000:5000 -it opentok-transcribe`

