#!/usr/bin/env python
from flask import Flask, json, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit as socketEmit
from flask_cors import CORS
import os, sys
import asyncio
from threading import Thread
import threading
import subprocess
from subprocess import Popen,PIPE
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from random import choice
from string import ascii_uppercase
import webrtcvad
from pprint import pprint
import uuid
import time
import requests
from profanity import profanity
from opentok import OpenTok

# This is the in-memory map of all the native processes
nativeProcesses = {}
pythonThreads = {}

chunkSize = 3200
sleepTime = 0.05

profanity.set_censor_characters('*')

class MyEventHandler(TranscriptResultStreamHandler):
    def setSessionId(self, sessionId):
      self.sessionId = sessionId

    def setFilterEnabled(self, filterEnabled):
      self.filterEnabled = filterEnabled

    def setOpentokInstance(self, ot):
      self.opentok = ot

    def censorText(self, text):
      if self.filterEnabled is None or not self.filterEnabled:
        return text

      return profanity.censor(text)

    def generatePayload(self, text):
      signal = {
        '_head': {
          'id': 0,
          'seq': 0,
          'tot': 0,
        },
        'data': {
          'text': text
        }
      }
      payload = {
          'type': 'transcription',  # optional
          'data': json.dumps(signal)  # required
      }
      return payload

    def sendCCbroadcastMsg(self, text):
      print(text)
      censorredText = self.censorText(text)
      self.opentok.signal(self.sessionId, self.generatePayload(censorredText))

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        if len(results) > 0:
          result = results[0]
          if len(result.alternatives) > 0:
            alt = result.alternatives[0]
            self.sendCCbroadcastMsg(alt.transcript)

async def fifo_stream(fifo):
  # Prepare data chunk
  data = fifo.read(chunkSize)
  while len(data) is not 0:

    if len(data) == 0:
      # No More Data
      print("FIFO Writer closed, breaking")
      break

    #print("data length", len(data))
    yield data
    #print("after send")

    if sleepTime > 0:
      time.sleep(sleepTime)
    #print("after sleep")

    # Prepare next chunk
    data = fifo.read(chunkSize)
    #print("after read")

async def nonstop_write_chunks(stream, fifo):
  startTime = int(time.time())
  print('Start Time:', startTime)

  print('Writing Chunks')
  async for chunk in fifo_stream(fifo):
    chunkTime = int(time.time())
    differenceInSeconds = chunkTime - startTime
    #print('Chunk Elapsed Time:', differenceInSeconds)
    await stream.input_stream.send_audio_event(audio_chunk = chunk)
  print('Out of chunk loop')
  await stream.input_stream.end_stream()
  print('Stream ended')

async def nonstop_stream_transcribe(apiKey, sessionId, secret, filterEnabled = False):
  myoutput = open("out.log",'w')
  opentok = OpenTok(apiKey, secret)
  transcriptionServiceToken = opentok.generate_token(sessionId)  # Token for transcription service
  print(transcriptionServiceToken)
  # Create FIFO
  path = "/tmp/"+''.join(choice(ascii_uppercase) for i in range(12))
  try:
    os.mkfifo(path,0o777)
  except OSError as e:
    print("Failed to create FIFO: %s" % e)
  else:
    print("FIFO Created")
  
  # Launch Native Application
  print("Launching native application process")
  process = Popen(['src/build/vonage-audio-renderer', path, apiKey, sessionId, transcriptionServiceToken], stdout=myoutput, stderr=myoutput)
  nativeProcesses[sessionId] = process
  print("Process started", sessionId)

  with open(path, 'rb') as fifo:
    print("FIFO Opened")

    # Create Client (can this be single client?)
    client = TranscribeStreamingClient(region = "us-west-2")
    stream = await client.start_stream_transcription(language_code = "en-US", media_sample_rate_hz = 16000, media_encoding = "pcm")
    handler = MyEventHandler(stream.output_stream)
    handler.setSessionId(sessionId)
    handler.setFilterEnabled(filterEnabled)
    handler.setOpentokInstance(opentok)

    print("Starting gather")
    await asyncio.gather(nonstop_write_chunks(stream, fifo), handler.handle_events())
    print("Gather ended")
  
  print("Thread ended")

api = Flask(__name__)
CORS(api)
socketio = SocketIO(api, cors_allowed_origins='*', async_mode='threading')
print(socketio)

@api.route('/transcribe', methods=['POST'])
def startTransribe():
  print('Start Transcribe')

  data = request.get_json()
  apiKey = data['apiKey']
  sessionId = data['sessionId']
  secret = data['secret']
  filterEnabled = data['filterEnabled'] if 'filterEnabled' in data else True

  print('API Key:', apiKey)
  print('Session ID:', sessionId)
  print('secret:', secret)
  print('Filter Enabled:', filterEnabled)

  if sessionId in nativeProcesses:
    # Existed, should not start
    print('Transcription process existed for session ID, not creating new process')
    return jsonify({ "status": "started" })

  # Start new process
  thread = threading.Thread(target=asyncio.run, args=(nonstop_stream_transcribe(apiKey, sessionId, secret, filterEnabled),))
  thread.start()
  print('Thread started', sessionId)

  pythonThreads[sessionId] = thread

  return jsonify({ "status": "started" })

@api.route('/transcribe/<session_id>', methods=['DELETE'])
def deleteTranscribe(session_id):
  print('Stop Transcription', session_id)

  if session_id not in nativeProcesses:
    # Not Exist, should not stop
    print('Transcription process not exist for session ID, not stopping process')
    return jsonify({ "status": "not_exist" })

  # Stop Process
  print('Killing Native Process', session_id)
  process = nativeProcesses[session_id]
  process.kill()
  print('Killed Native Process', session_id)
  del nativeProcesses[session_id]

  # Stop Thread
  print('Killing Python Thread', session_id)
  thread = pythonThreads[session_id]
  thread.join()
  print('Killed Python Thread', session_id)
  del pythonThreads[session_id]

  return jsonify({ "status": "stopped" })

@api.route('/transcribe/<session_id>', methods=['GET'])
def getTranscribe(session_id):
  print('Get Transcription', session_id)
  return jsonify({ "exist": session_id in nativeProcesses })

if __name__ == '__main__':
  print('Starting Server')
  socketio.run(api, host='0.0.0.0', port=5000)

print('done')

