import os
from dotenv import load_dotenv
import threading
import httpx
import time
from deepgram import DeepgramClient
from deepgram.core.events import EventType

#First step is to retrieve the Deepgram API key and make sure it is well set
load_dotenv()
if os.getenv("DEEPGRAM_KEY") is None: raise ValueError("DEEPGRAM_KEY is not set")
api_key=os.getenv("DEEPGRAM_KEY")

#Example of realtime streaming audio to be transcribed
URL = "http://stream.live.vc.bbcmedia.co.uk/bbc_world_service"

def main():
    try:
        deepgram: DeepgramClient = DeepgramClient(api_key=os.getenv("DEEPGRAM_KEY"))

        #This opens a websocket connection to the Deepgram API (more specifically, the nova-2 model). At this stage, the connection is set, but no data is sent/received
        with deepgram.listen.v1.connect(model="nova-2") as connection:
            
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
            connection.on(EventType.OPEN, lambda _: print("Connection opened"))
            connection.on(EventType.MESSAGE, on_message)
            connection.on(EventType.CLOSE, lambda _: print("Connection closed"))
            connection.on(EventType.ERROR, lambda error: print(f"Error: {error}"))


            #Two processes will need to be performed simultaneously: receiving the live audio track + sending it to Deepgram, AND receiving the transcriptions from Deegram + printing them
            #Hence, two threads will be used below. 

            lock_exit = threading.Lock() #This lock, when used later with acquire/release, prevents 2 threads to modify a variable (like 'exit') simultaneously
            exit = False

            #Function defining the thread that handles the listening of the Deepgram model
            def listening_thread():
                try:
                    connection.start_listening()
                except Exception as e:
                    print(f"Error in listening thread: {e}")

            #Function defining the thread that continuously sends the URL's audio stream to the deepgram API
            def myThread():
                try:
                    with httpx.stream("GET", URL) as r:
                        for data in r.iter_bytes(): #reads the audio stream by bits
                            
                            #if the signal to stop the listening has been sent, the thread is shut down
                            lock_exit.acquire()
                            if exit: 
                                break
                            lock_exit.release()

                            #else, it sends each audio bit to Deepgram
                            connection.send_media(data) 
                except Exception as e:
                    print(f"Error in HTTP streaming thread: {e}")


            #Both threads are initialized with their respective logic functions, and started in parallel
            listen_thread = threading.Thread(target=listening_thread)
            listen_thread.start()

            live_audio_thread = threading.Thread(target=myThread)
            live_audio_thread.start()


            print("🎙️ Listening... (automatic stop in 60 seconds)")
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
