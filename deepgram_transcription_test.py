import os
from dotenv import load_dotenv
import threading
import httpx
import time
import sounddevice as sd
import numpy as np
from deepgram import DeepgramClient
from deepgram.core.events import EventType

#First step is to retrieve the Deepgram API key and make sure it is well set
load_dotenv()
if os.getenv("DEEPGRAM_KEY") is None: raise ValueError("DEEPGRAM_KEY is not set")
api_key=os.getenv("DEEPGRAM_KEY")

# ========== CONFIGURATION ==========
# Choose audio source: "URL" or "MICROPHONE"
SOURCE = "MICROPHONE"  # Change to "URL" to use internet stream

# URL configuration (used only if SOURCE = "URL")
URL = "http://stream.live.vc.bbcmedia.co.uk/bbc_world_service"

# Microphone configuration (used only if SOURCE = "MICROPHONE")
SAMPLE_RATE = 16000  # Deepgram recommends 16kHz
CHANNELS = 1  # Mono audio
CHUNK_SIZE = 1024  # Number of frames per buffer



def main():
    try:
        deepgram: DeepgramClient = DeepgramClient(api_key=os.getenv("DEEPGRAM_KEY"))

        # This opens a websocket connection to the Deepgram API
        # For microphone: specify encoding since we send raw PCM audio
        # For URL: Deepgram auto-detects the encoded format (MP3, AAC, etc.)
        connection_options = {"model": "nova-2"}
        if SOURCE == "MICROPHONE":
            connection_options.update({
                "encoding": "linear16",
                "sample_rate": SAMPLE_RATE,
                "channels": CHANNELS,
            })

        with deepgram.listen.v1.connect(**connection_options) as connection:
            
            #This function is called each time the Deepgram API a transcription message
            def on_message(message) -> None:
                if hasattr(message, 'channel') and hasattr(message.channel, 'alternatives'):
                    alternative = message.channel.alternatives[0]
                    sentence = alternative.transcript #If the attributes exist, retreive the sentence
                    if len(sentence) == 0: #Empty transcriptions are ignored
                        return

                    #Print the transcription in real time
                    print(f"📝 {sentence}", flush=True)

                    #Alerts if there is low confidence at some point
                    if hasattr(alternative, 'confidence'):
                        confidence = alternative.confidence
                        if confidence < 0.8:
                            print(f" ⚠️ [Confidence faible: {confidence:.2f}]")
                 

            #Websocket's handlers (when a message is received, when the connection is opened or closed etc.)
            connection.on(EventType.OPEN, lambda _: print("Deepgram websocket opened"))
            connection.on(EventType.MESSAGE, on_message)
            connection.on(EventType.CLOSE, lambda _: print("Deepgram websocket closed"))
            connection.on(EventType.ERROR, lambda error: print(f"Deepgram websocket error: {error}"))


            #Two processes will need to be performed simultaneously: receiving the live audio track + sending it to Deepgram, AND receiving the transcriptions from Deegram + printing them
            #Hence, two threads will be used below. 

            lock_exit = threading.Lock() #This lock, when used later with acquire/release, prevents 2 threads to modify a variable (like 'exit') simultaneously
            exit = False

            #Function defining the thread that handles the listening of the Deepgram API's signals (OPEN, MESSAGE, CLOSE etc.) 
            def listening_thread():
                try:
                    print('* Listerning thread started')
                    connection.start_listening()
                except Exception as e:
                    print(f"Error in listening thread: {e}")

            #Function defining the thread that continuously sends audio to Deepgram API (from URL or microphone)
            def audio_streaming_thread():
                try:
                    if SOURCE == "URL": #Stream audio from URL
                        print('* Audio stream thread started (URL source)')
                        
                        with httpx.stream("GET", URL) as r:
                            for data in r.iter_bytes(): #reads the audio stream by bits
                                lock_exit.acquire()
                                if exit: #if the signal to stop the listening has been sent, the thread is shut down
                                    lock_exit.release()
                                    break
                                lock_exit.release()
                                connection.send_media(data)

                    elif SOURCE == "MICROPHONE": #Stream audio from microphone
                        print('* Audio stream thread started (microphone source)')

                        def audio_callback(indata, _frames, _time_info, status):
                            if status:
                                print(f"Audio status: {status}")

                            lock_exit.acquire()
                            should_exit = exit
                            lock_exit.release()

                            if not should_exit:
                                # Convert float32 audio to int16 (Deepgram expects int16)
                                audio_data = (indata * 32767).astype(np.int16)
                                connection.send_media(audio_data.tobytes())

                        print('... start recording from microphone')
                        # Start recording from microphone
                        with sd.InputStream(
                            samplerate=SAMPLE_RATE,
                            channels=CHANNELS,
                            dtype=np.float32,
                            blocksize=CHUNK_SIZE,
                            callback=audio_callback
                        ):
                            print('.')
                            while True:
                                lock_exit.acquire()
                                if exit:
                                    lock_exit.release()
                                    break
                                lock_exit.release()
                                time.sleep(0.1)

                    else:
                        print(f"❌ Invalid SOURCE: {SOURCE}. Use 'URL' or 'MICROPHONE'")

                except Exception as e:
                    print(f"Error in audio streaming thread: {e}")


            #Both threads are initialized with their respective logic functions, and started in parallel
            listen_thread = threading.Thread(target=listening_thread)
            listen_thread.start()
            
            time.sleep(0.5)

            live_audio_thread = threading.Thread(target=audio_streaming_thread)
            live_audio_thread.start()

            # Display appropriate message based on source
            source_message = "URL stream" if SOURCE == "URL" else "microphone"
            print(f"🎙️ Listening from {source_message}... (automatic stop in 60 seconds)")
            time.sleep(60)
            lock_exit.acquire()
            exit = True
            lock_exit.release()
            print("\n⏹️  End of listening.")

            #Wait for both threads to close and join with timeout
            live_audio_thread.join(timeout=5.0)
            listen_thread.join(timeout=5.0)

    except Exception as e:
        print(f"Could not open socket: {e}")
        return

if __name__ == "__main__":
    main()
