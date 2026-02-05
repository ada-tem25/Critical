import os
import asyncio
import threading
import time
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from deepgram import DeepgramClient
from deepgram.core.events import EventType

load_dotenv()

app = FastAPI()

# ============== CONFIGURATION ==============
# Langue par défaut si la détection échoue
DEFAULT_LANGUAGE = "fr"

# Durée de collecte d'audio pour la détection de langue (secondes)
# On collecte l'audio pendant ce temps avant de détecter la langue
LANGUAGE_DETECTION_DURATION = 3.0

# Timeout maximum pour la détection (si l'utilisateur ne parle pas)
LANGUAGE_DETECTION_TIMEOUT = 15.0

# Taille minimale du buffer audio pour tenter la détection (bytes)
# En dessous de ce seuil, on assume qu'il n'y a pas eu de parole
AUDIO_BUFFER_MIN_SIZE = 20000

# Timeout d'inactivité totale - arrête l'écoute si aucun son pendant ce temps (secondes)
INACTIVITY_TIMEOUT = 30.0
# ============================================

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
    """Détecte la langue à partir d'un buffer audio en utilisant l'API pre-recorded (synchrone)."""
    try:
        # Appeler l'API pre-recorded avec détection de langue
        response = deepgram.listen.v1.media.transcribe_file(
            request=audio_buffer,
            model="nova-2",
            detect_language=True,
            punctuate=True,
        )

        # Extraire la langue détectée depuis response.results.channels[0].detected_language
        if hasattr(response, 'results') and response.results:
            channels = getattr(response.results, 'channels', None)
            if channels and len(channels) > 0:
                channel = channels[0]
                if hasattr(channel, 'detected_language') and channel.detected_language:
                    lang = channel.detected_language
                    print(f"Langue détectée: {lang}")
                    return lang

        print(f"Langue non détectée, fallback sur '{DEFAULT_LANGUAGE}'")
        return DEFAULT_LANGUAGE
    except Exception as e:
        print(f"Erreur détection langue: {e}")
        return DEFAULT_LANGUAGE


@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()

    print("=" * 50)
    print("Client WebSocket connecté")
    print("=" * 50)

    api_key = os.getenv("DEEPGRAM_KEY")
    if not api_key:
        await websocket.send_json({"error": "DEEPGRAM_KEY non configurée"})
        await websocket.close()
        return

    deepgram = DeepgramClient(api_key=api_key)

    # Queue pour les transcriptions (thread-safe)
    transcription_queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    # Flag pour arrêter proprement
    should_stop = threading.Event()

    dg_context = None
    dg_connection = None

    try:
        # Phase 1: Collecter l'audio pendant quelques secondes pour détecter la langue
        await websocket.send_json({"status": "detecting_language", "message": "Parlez pour détecter la langue..."})

        audio_buffer = bytearray()
        start_time = time.time()

        print(f"Collecte audio pendant {LANGUAGE_DETECTION_DURATION}s...")

        while True:
            elapsed = time.time() - start_time

            # Fin de la collecte après LANGUAGE_DETECTION_DURATION secondes
            if elapsed >= LANGUAGE_DETECTION_DURATION:
                print(f"Fin collecte après {elapsed:.1f}s - {len(audio_buffer)} bytes collectés")
                break

            # Timeout de sécurité
            if elapsed > LANGUAGE_DETECTION_TIMEOUT:
                print(f"Timeout détection langue après {elapsed:.1f}s")
                break

            try:
                data = await asyncio.wait_for(websocket.receive_bytes(), timeout=0.5)
                audio_buffer.extend(data)

            except asyncio.TimeoutError:
                continue
            except WebSocketDisconnect:
                print("Client déconnecté pendant la détection")
                return

        # Décider si on a assez d'audio pour détecter la langue
        if len(audio_buffer) < AUDIO_BUFFER_MIN_SIZE:
            # Pas assez d'audio, fallback sur la langue par défaut
            print(f"Buffer trop petit ({len(audio_buffer)} bytes < {AUDIO_BUFFER_MIN_SIZE}), fallback sur '{DEFAULT_LANGUAGE}'")
            detected_language = DEFAULT_LANGUAGE
            await websocket.send_json({
                "status": "language_detected",
                "language": detected_language,
                "message": f"Langue par défaut: {detected_language}"
            })
        else:
            # Détecter la langue (exécuté dans un thread pour ne pas bloquer)
            print(f"Appel API détection langue ({len(audio_buffer)} bytes d'audio)")
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

        def on_message(message):
            if hasattr(message, 'channel') and hasattr(message.channel, 'alternatives'):
                alternative = message.channel.alternatives[0]
                transcript = alternative.transcript
                if transcript:
                    confidence = getattr(alternative, 'confidence', 1.0)
                    is_final = getattr(message, 'is_final', True)
                    asyncio.run_coroutine_threadsafe(
                        transcription_queue.put({
                            "transcript": transcript,
                            "confidence": confidence,
                            "is_final": is_final
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
                    data = await websocket.receive_bytes()
                    dg_connection.send_media(data)
                    # Mettre à jour le timestamp à chaque chunk reçu
                    last_audio_time = time.time()
                except WebSocketDisconnect:
                    print("Client déconnecté")
                    break
                except Exception as e:
                    print(f"Erreur réception audio: {e}")
                    break

        async def check_inactivity():
            """Arrête l'écoute si inactif trop longtemps"""
            while not should_stop.is_set():
                await asyncio.sleep(1.0)
                if time.time() - last_audio_time > INACTIVITY_TIMEOUT:
                    print(f"Inactivité de {INACTIVITY_TIMEOUT}s - arrêt de l'écoute")
                    await websocket.send_json({
                        "status": "timeout",
                        "message": f"Arrêt automatique après {int(INACTIVITY_TIMEOUT)}s d'inactivité"
                    })
                    break

        # Lancer les tâches en parallèle
        send_task = asyncio.create_task(send_transcriptions())
        receive_task = asyncio.create_task(receive_audio())
        inactivity_task = asyncio.create_task(check_inactivity())

        # Attendre que l'une des tâches se termine
        done, pending = await asyncio.wait(
            [send_task, receive_task, inactivity_task],
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
