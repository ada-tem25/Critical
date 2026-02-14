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

# Récupération de la clé API AssemblyAI
load_dotenv()
if os.getenv("ASSEMBLYAI_KEY") is None:
    raise ValueError("ASSEMBLYAI_KEY is not set")
assemblyai_api_key = os.getenv("ASSEMBLYAI_KEY")


# ============== CONFIG ==============
# Sample rate attendu par le frontend (doit correspondre au Web Audio API)
SAMPLE_RATE = 16000

# Modèle de streaming (universal-streaming-multi pour la détection automatique de langue)
SPEECH_MODEL = "universal-streaming-multilingual"

# Nombre max de chunks vides consécutifs avant arrêt (silence)
MAX_EMPTY_CHUNKS = 15

# URL du WebSocket AssemblyAI
ASSEMBLYAI_WS_URL = "wss://streaming.assemblyai.com/v3/ws"
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
    return FileResponse(os.path.join(frontend_path, "index2.html"))


@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()

    assemblyai_ws = None
    should_stop = asyncio.Event()

    # Compteur de transcriptions vides consécutives
    empty_chunk_count = 0

    # Pour éviter les doublons (AssemblyAI envoie parfois la même phrase finale 2 fois)
    last_final_transcript = ""

    # File d'attente pour les transcriptions à envoyer au client
    transcription_queue = asyncio.Queue()

    try:
        # Construction de l'URL avec les paramètres
        ws_url = f"{ASSEMBLYAI_WS_URL}?sample_rate={SAMPLE_RATE}&speech_model={SPEECH_MODEL}&format_turns=true"

        # Connexion au WebSocket AssemblyAI avec authentification
        print(f"Connexion à AssemblyAI avec modèle: {SPEECH_MODEL}")
        print(f"URL: {ws_url}")
        print(f"API Key (premiers chars): {assemblyai_api_key[:10]}...")

        try:
            assemblyai_ws = await websockets.connect(
                ws_url,
                additional_headers={"Authorization": assemblyai_api_key}
            )
            print("Connexion AssemblyAI établie")
        except websockets.exceptions.InvalidStatusCode as e:
            print(f"Erreur connexion AssemblyAI: HTTP {e.status_code}")
            await websocket.send_json({"error": f"Erreur AssemblyAI: HTTP {e.status_code}"})
            return
        except Exception as e:
            print(f"Erreur connexion AssemblyAI: {type(e).__name__}: {e}")
            await websocket.send_json({"error": f"Erreur connexion: {str(e)}"})
            return

        await websocket.send_json({
            "status": "connected",
            "message": "Connecté à AssemblyAI - Détection automatique de langue activée"
        })

        async def receive_from_assemblyai():
            """Reçoit les transcriptions d'AssemblyAI et les met dans la queue"""
            nonlocal empty_chunk_count, last_final_transcript

            try:
                async for message in assemblyai_ws:
                    if should_stop.is_set():
                        break

                    data = json.loads(message)
                    msg_type = data.get("type")

                    if msg_type == "Begin":
                        print(f"Session AssemblyAI démarrée: {data.get('id')}")
                        await transcription_queue.put({
                            "status": "session_started",
                            "session_id": data.get("id")
                        })

                    elif msg_type == "Turn":
                        transcript = data.get("transcript", "")
                        is_final = data.get("end_of_turn", False)

                        # Extraire la langue détectée si disponible
                        words = data.get("words", [])
                        detected_language = None
                        if words:
                            # AssemblyAI peut inclure la langue dans les métadonnées
                            detected_language = data.get("language_code")

                        if transcript and transcript.strip():
                            # Transcription non vide
                            empty_chunk_count = 0

                            # Filtrer les doublons (AssemblyAI envoie parfois 2x la même phrase finale)
                            if is_final and transcript == last_final_transcript:
                                print(f"[AssemblyAI] FINAL doublon ignoré: \"{transcript}\"")
                                continue

                            print(f"[AssemblyAI] {'FINAL' if is_final else 'interim'}: \"{transcript}\"")

                            if is_final:
                                last_final_transcript = transcript

                            # Calculer la confiance moyenne
                            confidence = 1.0
                            if words:
                                confidences = [w.get("confidence", 1.0) for w in words]
                                confidence = sum(confidences) / len(confidences) if confidences else 1.0

                            await transcription_queue.put({
                                "transcript": transcript,
                                "confidence": confidence,
                                "is_final": is_final,
                                "language": detected_language
                            })
                        else:
                            # Transcription vide
                            empty_chunk_count += 1
                            print(f"[AssemblyAI] Empty chunk ({empty_chunk_count}/{MAX_EMPTY_CHUNKS})")

                            if empty_chunk_count >= MAX_EMPTY_CHUNKS:
                                print(f"[AssemblyAI] {MAX_EMPTY_CHUNKS} chunks vides - arrêt pour silence")
                                await transcription_queue.put({
                                    "status": "silence_timeout",
                                    "message": "Arrêt automatique : silence détecté"
                                })

                    elif msg_type == "Termination":
                        print(f"Session terminée - Durée audio: {data.get('audio_duration_seconds')}s")
                        await transcription_queue.put({
                            "status": "stream_complete",
                            "audio_duration": data.get("audio_duration_seconds"),
                            "session_duration": data.get("session_duration_seconds")
                        })
                        break

                    elif msg_type == "Error":
                        error_msg = data.get("error", "Erreur inconnue")
                        print(f"[AssemblyAI] Erreur: {error_msg}")
                        await transcription_queue.put({"error": error_msg})

            except websockets.exceptions.ConnectionClosed as e:
                print(f"Connexion AssemblyAI fermée: code={e.code}, reason={e.reason}")
            except Exception as e:
                print(f"Erreur réception AssemblyAI: {e}")
                await transcription_queue.put({"error": str(e)})

        async def send_to_client():
            """Envoie les transcriptions de la queue vers le client"""
            while not should_stop.is_set():
                try:
                    data = await asyncio.wait_for(transcription_queue.get(), timeout=0.1)

                    if data.get("status") == "silence_timeout":
                        await websocket.send_json({
                            "status": "timeout",
                            "message": data.get("message", "Arrêt pour silence")
                        })
                        await asyncio.sleep(0.5)
                        break

                    if data.get("status") == "stream_complete":
                        await websocket.send_json(data)
                        break

                    await websocket.send_json(data)

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"Erreur envoi client: {e}")
                    break

        async def receive_from_client():
            """Reçoit l'audio du client et l'envoie à AssemblyAI"""
            while not should_stop.is_set():
                try:
                    message = await websocket.receive()

                    if message["type"] == "websocket.receive":
                        if "bytes" in message and message["bytes"]:
                            # Données audio PCM16
                            await assemblyai_ws.send(message["bytes"])

                        elif "text" in message and message["text"]:
                            data = json.loads(message["text"])
                            if data.get("type") == "end_of_stream":
                                print("End of stream reçu, envoi Terminate à AssemblyAI...")
                                await assemblyai_ws.send(json.dumps({"type": "Terminate"}))
                                # Attendre un peu pour recevoir les dernières transcriptions
                                await asyncio.sleep(1.5)
                                break

                    elif message["type"] == "websocket.disconnect":
                        print("Client déconnecté")
                        break

                except WebSocketDisconnect:
                    print("Client déconnecté")
                    break
                except Exception as e:
                    print(f"Erreur réception client: {e}")
                    break

        # Lancer les tâches en parallèle
        assemblyai_task = asyncio.create_task(receive_from_assemblyai())
        send_task = asyncio.create_task(send_to_client())
        receive_task = asyncio.create_task(receive_from_client())

        # Attendre qu'une tâche se termine
        done, pending = await asyncio.wait(
            [assemblyai_task, send_task, receive_task],
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
        if assemblyai_ws:
            try:
                await assemblyai_ws.close()
            except:
                pass
        print("Connexion fermée")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
