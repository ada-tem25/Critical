import os
import asyncio
import threading
import time
import json
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from deepgram import DeepgramClient
from deepgram.core.events import EventType

app = FastAPI()

#First step is to retrieve the Deepgram API key and make sure it is well set
load_dotenv()
if os.getenv("DEEPGRAM_KEY") is None: raise ValueError("DEEPGRAM_KEY is not set")
deepgram_api_key=os.getenv("DEEPGRAM_KEY")


# ============== CONFIG ==============
# Language detection duration (in seconds)
LANGUAGE_DETECTION_DURATION = 4.0

# If the language detection fails, falls back on this default language
DEFAULT_LANGUAGE = "fr" # It will later become a user parameter

# Max number of consecutive empty transcriptions before stopping the audio stream recording
MAX_EMPTY_CHUNKS = 15
# ====================================


# CORS pour le développement local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir les fichiers statiques du frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_path, "index.html"))


def detect_language_sync(deepgram: DeepgramClient, audio_buffer: bytes) -> str:
    """
    Détecte la langue à partir d'un buffer audio en utilisant l'API pre-recorded.
    Retourne la langue par défaut si aucune parole n'est détectée (transcription vide).
    """
    try:
        response = deepgram.listen.v1.media.transcribe_file(
            request=audio_buffer,
            model="nova-2",
            detect_language=True,
            punctuate=True,
        )

        if hasattr(response, 'results') and response.results:
            channels = getattr(response.results, 'channels', None)
            if channels and len(channels) > 0:
                channel = channels[0]
                alternatives = getattr(channel, 'alternatives', None)

                # Vérifier si la transcription est non vide (= quelqu'un a parlé)
                if alternatives and len(alternatives) > 0:
                    transcript = getattr(alternatives[0], 'transcript', '').strip()
                    if transcript:
                        # Transcription non vide = parole détectée
                        lang = getattr(channel, 'detected_language', None)
                        if lang:
                            print(f"Parole détectée: '{transcript[:50]}...' -> Langue: {lang}")
                            return lang

        # Aucune transcription = pas de parole = langue par défaut
        print(f"Pas de parole détectée, utilisation de la langue par défaut: {DEFAULT_LANGUAGE}")
        return DEFAULT_LANGUAGE
    except Exception as e:
        print(f"Erreur détection langue: {e}")
        return DEFAULT_LANGUAGE


#The main endpoint that the frontend will call (through a websocket) when starting to record audio
@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept() #the backend must begin by accepting the connexion

    deepgram = DeepgramClient(api_key=12)

    # Thread-safe way to put the transcriptions in a queue before sending them to the frontend
    transcription_queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    # Proper way to define variables that will be accessed by multiple threads
    should_stop = threading.Event()

    dg_context = None
    dg_connection = None

    try:
        
        # ------- 1st step: Collect a few seconds of audio to detect the language (since deepgram cannot do this during an audio stream)
        await websocket.send_json({"status": "detecting_language", "message": "Language detection..."})
        audio_buffer = bytearray()
        start_time = time.time()

        # Audio collection
        while True:
            elapsed_time = time.time() - start_time

            if elapsed_time >= LANGUAGE_DETECTION_DURATION:
                print(f"- language detection ended after {elapsed_time:.1f}s")
                break

            try: #while the language detection time is not elapsed, the audio is continuously retreived
                data = await asyncio.wait_for(websocket.receive_bytes(), timeout=0.5)
                audio_buffer.extend(data)
            except asyncio.TimeoutError:
                continue
            except WebSocketDisconnect:
                print("Client deconnection during detection")
                return

        # Language detection (executed in a separate thread)
        detected_language = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: detect_language_sync(deepgram, bytes(audio_buffer))
        )

        # Informer le client de la langue détectée
        await websocket.send_json({
            "status": "language_detected",
            "language": detected_language,
            "message": f"Langue détectée: {detected_language}"
        })

        print(f"Démarrage streaming avec langue: {detected_language}")

        # Phase 2: Streaming avec la langue détectée
        connection_options = {
            "model": "nova-2",
            "language": detected_language,
            "punctuate": True,
            "interim_results": True,
        }

        # Ouvrir connexion Deepgram
        dg_context = deepgram.listen.v1.connect(**connection_options)
        dg_connection = dg_context.__enter__()

        # Compteur de transcriptions vides consécutives
        empty_chunk_count = [0]  # Liste pour pouvoir modifier dans la closure

        def on_message(message):
            if hasattr(message, 'channel') and hasattr(message.channel, 'alternatives'):
                alternative = message.channel.alternatives[0]
                transcript = alternative.transcript
                is_final = getattr(message, 'is_final', True)

                if transcript and transcript.strip():
                    # Transcription non vide
                    print(f"[Deepgram] {'FINAL' if is_final else 'interim'}: \"{transcript}\"")
                    empty_chunk_count[0] = 0  # Reset du compteur
                    confidence = getattr(alternative, 'confidence', 1.0)
                    asyncio.run_coroutine_threadsafe(
                        transcription_queue.put({
                            "transcript": transcript,
                            "confidence": confidence,
                            "is_final": is_final
                        }),
                        loop
                    )
                else:
                    # Transcription vide
                    empty_chunk_count[0] += 1
                    print(f"[Deepgram] Empty chunk ({empty_chunk_count[0]}/{MAX_EMPTY_CHUNKS})")

                    if empty_chunk_count[0] >= MAX_EMPTY_CHUNKS:
                        print(f"[Deepgram] {MAX_EMPTY_CHUNKS} chunks vides consécutifs - arrêt pour silence")
                        asyncio.run_coroutine_threadsafe(
                            transcription_queue.put({
                                "status": "silence_timeout",
                                "message": "Arrêt automatique : silence détecté"
                            }),
                            loop
                        )

        def on_error(error):
            print(f"Deepgram error: {error}")
            asyncio.run_coroutine_threadsafe(
                transcription_queue.put({"error": str(error)}),
                loop
            )

        # Enregistrer les handlers
        dg_connection.on(EventType.OPEN, lambda _: print("Deepgram WebSocket ouvert"))
        dg_connection.on(EventType.MESSAGE, on_message)
        dg_connection.on(EventType.CLOSE, lambda _: print("Deepgram WebSocket fermé"))
        dg_connection.on(EventType.ERROR, on_error)

        # Thread pour écouter les réponses Deepgram
        def listening_thread():
            try:
                dg_connection.start_listening()
            except Exception as e:
                print(f"Erreur listening thread: {e}")

        listen_thread = threading.Thread(target=listening_thread, daemon=True)
        listen_thread.start()

        print("Connexion Deepgram établie")

        # Envoyer le buffer initial à Deepgram (pour ne pas perdre les premiers mots)
        dg_connection.send_media(bytes(audio_buffer))

        async def send_transcriptions():
            """Envoie les transcriptions au client"""
            while not should_stop.is_set():
                try:
                    data = await asyncio.wait_for(transcription_queue.get(), timeout=0.1)

                    # Gérer le silence_timeout
                    if data.get("status") == "silence_timeout":
                        print("Envoi du message timeout au frontend...")
                        await websocket.send_json({
                            "status": "timeout",
                            "message": data.get("message", "Arrêt pour silence")
                        })
                        # Laisser le temps au message d'être transmis avant de fermer
                        await asyncio.sleep(0.5)
                        print("Message timeout envoyé, fermeture...")
                        break

                    await websocket.send_json(data)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"Erreur envoi transcription: {e}")
                    break

        # Timestamp du dernier audio non-vide reçu
        last_audio_time = time.time()

        async def receive_audio():
            """Reçoit l'audio du client et l'envoie à Deepgram"""
            nonlocal last_audio_time
            while not should_stop.is_set():
                try:
                    message = await websocket.receive()

                    if message["type"] == "websocket.receive":
                        if "bytes" in message and message["bytes"]:
                            # Audio data
                            dg_connection.send_media(message["bytes"])
                            last_audio_time = time.time()
                        elif "text" in message and message["text"]:
                            # JSON message (end_of_stream, etc.)
                            data = json.loads(message["text"])
                            if data.get("type") == "end_of_stream":
                                print("End of stream reçu, finalisation...")
                                # Attendre les dernières transcriptions de Deepgram
                                await asyncio.sleep(1.5)
                                await websocket.send_json({"status": "stream_complete"})
                                print("Stream complete envoyé")
                                break
                    elif message["type"] == "websocket.disconnect":
                        print("Client déconnecté")
                        break
                except WebSocketDisconnect:
                    print("Client déconnecté")
                    break
                except Exception as e:
                    print(f"Erreur réception audio: {e}")
                    break



        # Lancer les tâches en parallèle
        send_task = asyncio.create_task(send_transcriptions())
        receive_task = asyncio.create_task(receive_audio())

        # Attendre que l'une des tâches se termine
        done, pending = await asyncio.wait(
            [send_task, receive_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # Signaler l'arrêt et annuler les tâches en attente
        should_stop.set()
        for task in pending:
            task.cancel()
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
    finally:
        should_stop.set()
        if dg_context:
            try:
                dg_context.__exit__(None, None, None)
            except:
                pass
        print("Connexion fermée")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
