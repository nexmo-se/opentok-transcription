#!/usr/bin/env python
from flask import Flask, json, request, jsonify
from flask_cors import CORS
import os, sys
import asyncio
from threading import Thread
import threading
import subprocess
from subprocess import Popen,PIPE
from string import ascii_uppercase
import webrtcvad
from pprint import pprint
from random import choice
import uuid
import time
import requests
from opentok import OpenTok
from overai_speech.asr import OverAiAsr
import logging


TRANSCRIPTION_SERVICE_WS = 'ws://asr-en.dev.ai.vonage.com'  # ASR server endpoint
CORRECTION_SERVICE_URL = 'https://asr-corrector.dev.ai.vonage.com/api/v1/asr/correct/'  # ASR correction service

# This is the in-memory map of all the native processes
nativeProcesses = {}
pythonThreads = {}

chunkSize = 32000
sleepTime = 2

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

def generatePayload(text):
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

async def transcribe_chunks(fifo, sessionId, opentok):
  asr = OverAiAsr(transcription_service_ws=TRANSCRIPTION_SERVICE_WS)
  async for chunk in fifo_stream(fifo):
    results_generator = asr.transcribe_buffer(chunk)

    for index, (partial, transcription, raw_transcriptions) in enumerate(results_generator):
      print(raw_transcriptions)
      if transcription:
        opentok.send_signal(sessionId, generatePayload(transcription))

  print('Stream ended')

async def launch_native_collect(apiKey, sessionId, secret):
  sessionOutput = open(sessionId + ".log",'w')
  opentok = OpenTok(apiKey, secret)
  transcriptionServiceToken = opentok.generate_token(sessionId)  # Token for transcription service


  path = "/tmp/"+''.join(choice(ascii_uppercase) for i in range(12))
  try:
    os.mkfifo(path,0o777)
  except OSError as e:
    print("Failed to create FIFO: %s" % e)
  else:
    print("FIFO Created")
  
  process = Popen(['src/build/vonage-audio-renderer', path, apiKey, sessionId, transcriptionServiceToken], stdout=sessionOutput, stderr=sessionOutput)
  nativeProcesses[sessionId] = process
  print("Started transcribing", sessionId)

  with open(path, 'rb') as fifo:
    await asyncio.gather(transcribe_chunks(fifo, sessionId, opentok))
  
  print("Thread ended")

api = Flask(__name__)
CORS(api)

@api.route('/transcribe', methods=['POST'])
def startTransribe():
  print('Start Transcribe')

  data = request.get_json()
  apiKey = data['apiKey']
  sessionId = data['sessionId']
  secret = data['secret']

  print('API Key:', apiKey)
  print('Session ID:', sessionId)
  print('secret:', secret)

  if sessionId in nativeProcesses:
    # Existed, should not start
    print('Transcription process existed for session ID, not creating new process')
    return jsonify({ "status": "started" })

  # Start new process
  thread = threading.Thread(target=asyncio.run, args=(launch_native_collect(apiKey, sessionId, secret),))
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
  api.run(host='0.0.0.0', port=5000)

print('done')
