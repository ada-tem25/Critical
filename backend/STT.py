import os
import asyncio
import json
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import websockets

app = FastAPI()

# AssemblyAI API key retrieval
load_dotenv()
if os.getenv("ASSEMBLYAI_KEY") is None: raise ValueError("ASSEMBLYAI_KEY is not set")
assemblyai_api_key = os.getenv("ASSEMBLYAI_KEY")


# ============== CONFIG ==============
# Expected sample rate of the incoming audio stream (must match the frontend)
SAMPLE_RATE = 16000

# AssemblyAI audio streaming model (this one detects the language automatically, no need to specify it in the frontend)
SPEECH_MODEL = "universal-streaming-multilingual"

# Max number of consecutive empty transcriptions before considering it a silence and stopping the stream
MAX_EMPTY_CHUNKS = 15

# AssemblyAI WebSocket URL
ASSEMBLYAI_WS_URL = "wss://streaming.assemblyai.com/v3/ws"
# ====================================


# CORS is the web browser security mechanism that restricts/allows selected requests. For local development, we allow all origins. In production, we will restrict to the frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Making the frontend files available from the backend...
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# ...so that when we access the backend URL from the browser (http://localhost:8001/), it serves the frontend page (in production, the frontend would be served separately and this wouldn't be necessary)
@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_path, "index.html"))


@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept() # the backend must begin by accepting the connexion

    assemblyai_ws = None
    should_stop = asyncio.Event()
    empty_chunk_count = 0 # Consecutive empty chunks (to detect silence)
    last_final_transcript = ""

    # Transcriptions received from AssemblyAI will be put in this queue before being sent to the frontend, to avoid concurrency issues between the tasks that receive from AssemblyAI and send to the client. The "send_transcriptions_to_client" task will read from this queue and send the transcriptions to the frontend in order.
    transcription_queue = asyncio.Queue()

    try:
        ws_url = f"{ASSEMBLYAI_WS_URL}?sample_rate={SAMPLE_RATE}&speech_model={SPEECH_MODEL}&format_turns=true"

        # We connect to AssemblyAI's WebSocket
        try:
            assemblyai_ws = await websockets.connect(ws_url, additional_headers={"Authorization": assemblyai_api_key}) 
            print("Connexion Backend<-->AssemblyAI établie")
        except websockets.exceptions.InvalidStatusCode as e: # Specific errors explained by AssemblyAI
            print(f"Erreur connexion AssemblyAI: HTTP {e.status_code}")
            await websocket.send_json({"error": f"Erreur AssemblyAI: HTTP {e.status_code}"})
            return
        except Exception as e: # To catch all other unexpected errors
            print(f"Erreur connexion AssemblyAI: {type(e).__name__}: {e}")
            await websocket.send_json({"error": f"Erreur connexion: {str(e)}"})
            return
        

        # 1st concurrent task of the websocket: receives the audio from the client and sends it to AssemblyAI in real-time
        async def receive_speech_from_client():
            while not should_stop.is_set():
                try:
                    message = await websocket.receive()

                    if message["type"] == "websocket.receive": # normal message, no error
                        if "bytes" in message and message["bytes"]: # the PCM16 audio of the message is in the "bytes" field
                            await assemblyai_ws.send(message["bytes"]) # it is sent directly to AssemblyAI without any processing, as AssemblyAI accepts raw PCM16 audio at 16kHz
                        elif "text" in message and message["text"]: # the control message "end_of_stream" is sent as text
                            data = json.loads(message["text"])
                            if data.get("type") == "end_of_stream":
                                await assemblyai_ws.send(json.dumps({"type": "Terminate"}))
                                await asyncio.sleep(1.5) # we wait a bit to let AssemblyAI send the final transcriptions before closing the connection. Maybe this should be improved in the future by waiting for a specific message from AssemblyAI instead of an arbitrary time.
                                break
                    elif message["type"] == "websocket.disconnect":
                        break

                except WebSocketDisconnect: # to handle the case when the client disconnects abruptly (for example by closing the browser tab), which would not trigger "await websocket.receive()". 
                    print("Websocket disconnected from client")
                    break
                except Exception as e:
                    print(f"Client disconnected: {e}")
                    break
        
        # 2nd concurrent task of the websocket: receives the transcriptions from AssemblyAI and puts them in the transcription_queue
        async def receive_transcriptions_from_assemblyai():
            nonlocal empty_chunk_count, last_final_transcript # "nonlocal" is necessary to reassign variables that are defined in a parent function
            
            try:
                async for message in assemblyai_ws:
                    if should_stop.is_set():
                        break

                    data = json.loads(message)
                    msg_type = data.get("type")
                    print(data)
                    if msg_type == "Begin": # Informs the frontend that the session has successfully started, so that it can update the UI accordingly (enable the "Stop" button, etc.)
                        await transcription_queue.put({
                            "status": "session_started",
                            "session_id": data.get("id")
                        })

                    elif msg_type == "Turn": # This is the main message type that contains the transcriptions, which can be final / interim
                        transcript = data.get("transcript", "")
                        is_final = data.get("end_of_turn", False)

                        words = data.get("words", [])
                        detected_language = None
                        if words:
                            detected_language = data.get("language_code") # Language retreival

                        if transcript and transcript.strip(): #Non-empty transcription
                            empty_chunk_count = 0

                            if is_final and transcript == last_final_transcript: continue # Skip if the final transcript is the same as the last one (sometimes AssemblyAI can resend the same final transcript multiple times, which can cause duplicates in the frontend)

                            print(f"[AssemblyAI] {'FINAL' if is_final else 'interim'}: \"{transcript}\"")

                            if is_final: last_final_transcript = transcript

                            confidence = 1.0 # We compute the confidence of the transcription
                            if words:
                                confidences = [w.get("confidence", 1.0) for w in words]
                                confidence = sum(confidences) / len(confidences) if confidences else 1.0

                            await transcription_queue.put({
                                "transcript": transcript,
                                "transcription_confidence": confidence,
                                "is_final": is_final,
                                "language": detected_language
                            })
                        else: # Empty transcription
                            empty_chunk_count += 1
                            print(f"[AssemblyAI] Empty chunk ({empty_chunk_count}/{MAX_EMPTY_CHUNKS})")

                            if empty_chunk_count >= MAX_EMPTY_CHUNKS:
                                print(f"[AssemblyAI] {MAX_EMPTY_CHUNKS} empty chunks detected, stopping stream for silence")
                                await transcription_queue.put({"status": "silence_timeout"})

                    elif msg_type == "Termination": # When AssemblyAI signals the end of the stream
                        await transcription_queue.put({"status": "stream_complete"})
                        break

                    elif msg_type == "Error": # When AssemblyAI signals an error (for example if the audio format is wrong, or if the session duration exceeds the limit, etc.)
                        error_msg = data.get("error", "Unknown error")
                        print(f"[AssemblyAI] Erreur: {error_msg}")
                        await transcription_queue.put({"error": error_msg})

            except websockets.exceptions.ConnectionClosed as e:
                print(f"AssemblyAI ConnexionClosed error: code={e.code}, reason={e.reason}")
            except Exception as e:
                print(f"AssemblyAI unknown error: {e}")
                await transcription_queue.put({"error": str(e)})

        # 3rd concurrent task of the websocket: sends the transcriptions received from the transcription_queue to the frontend in real-time. 
        async def send_transcriptions_to_client():
            while not should_stop.is_set():
                try:
                    data = await asyncio.wait_for(transcription_queue.get(), timeout=0.1)

                    if data.get("status") == "silence_timeout":
                        await websocket.send_json({
                            "status": "timeout",
                            "message": "Stream stopped due to silence"
                        })
                        await asyncio.sleep(0.5)
                        break

                    if data.get("status") == "stream_complete":
                        await websocket.send_json(data)
                        break

                    await websocket.send_json(data)

                except asyncio.TimeoutError: # Handles the case when there is no new transcription in the queue for 100ms, which is normal and should not be treated as an error by .wait_for()
                    continue
                except Exception as e:
                    print(f"Error while sending transcription to the client: {e}")
                    break

        

        # The 3 tasks that run concurrently within this websocket: receiving audio from client, receiving the transcriptions from AssemblyAI, and sending those transcriptions back to client (this 3rd part will be removed in production, as the user doesn't want to see its transcription in real-time)
        receive_task = asyncio.create_task(receive_speech_from_client())
        assemblyai_task = asyncio.create_task(receive_transcriptions_from_assemblyai())
        send_task = asyncio.create_task(send_transcriptions_to_client())

        # The "wait" function will wait until any of the 3 tasks is done (either the client disconnects, or the stream ends, or an error occurs), then it will signal the other tasks to stop and cancel them if they are still running. We don't want tasks running endlessly, to avoid consuming unnecessary resources
        done, pending = await asyncio.wait(
            [assemblyai_task, send_task, receive_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        should_stop.set()
        for task in pending:
            task.cancel() # We force the stop of tasks that have not yet reacted to the should_stop=True event
            try:
                await task
            except asyncio.CancelledError:
                pass

    except Exception as e:
        print(f"Erreur WebSocket: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
    finally: # This runs wathever happens before, and makes sure everything in this websocket is cleaned up properly
        should_stop.set()
        if assemblyai_ws:
            try:
                await assemblyai_ws.close()
            except:
                pass
        print("Websocket closed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
