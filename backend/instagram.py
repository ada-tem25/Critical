"""
Instagram source module - Downloads and transcribes audio from Instagram posts/reels.
"""
import os
import asyncio
import tempfile
import re
from typing import Optional
from pydantic import BaseModel, field_validator
from fastapi import APIRouter
import yt_dlp

# Import AssemblyAI helpers from STT module
from STT import (
    upload_to_assemblyai,
    create_transcription_job,
    poll_transcription_result,
)

router = APIRouter()


# ============== PYDANTIC MODELS ==============

class InstagramTranscriptionRequest(BaseModel):
    """Request model for Instagram transcription, sent by the frontend"""
    url: str

    @field_validator('url')
    @classmethod
    def validate_instagram_url(cls, v):
        # Checks that the URL is a valid Instagram post or reel URL
        instagram_pattern = r'^https?://(www\.)?instagram\.com/(p|reel|reels)/[\w-]+/?'
        if not re.match(instagram_pattern, v):
            raise ValueError('URL must be a valid Instagram post or reel URL')
        return v


class InstagramTranscriptionResponse(BaseModel):
    """Response model for Instagram transcription, sent back to the frontend"""
    status: str  # "completed" or "error"
    transcript: Optional[str] = None
    confidence: Optional[float] = None
    duration_seconds: Optional[float] = None
    processing_time_seconds: Optional[float] = None

    # Post metadata
    description: Optional[str] = None
    uploader: Optional[str] = None
    upload_date: Optional[str] = None
    error_code: Optional[str] = None
    message: Optional[str] = None


# ============== HELPER FUNCTIONS ==============

async def download_instagram_audio(url: str, output_dir: str) -> dict:
    """
    Downloads the audio from an Instagram URL using yt-dlp.
    Returns a dict with the metadata and the path to the stored audio.
    """
    output_template = os.path.join(output_dir, "audio.%(ext)s")

    ydl_opts = { # yt-dlp parameters
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
    }

    # yt-dlp is synchronous, so we run it in a thread to avoid blocking FastAPI's event loop
    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: # Audio downloaded and metadata retrieval done here. Audio is immediately stored in the output_dir with the name "audio.mp3" thanks to the "outtmpl" parameter, and metadata is stored in the "info" variable
            info = ydl.extract_info(url, download=True)
            return {
                'duration': info.get('duration', 0),
                'description': info.get('description'),
                'uploader': info.get('uploader') or info.get('channel'),
                'upload_date': info.get('upload_date'),
            }

    loop = asyncio.get_event_loop() # This points to the main event loop of FastAPI
    metadata = await loop.run_in_executor(None, _download) # This runs the blocking _download function in a separate thread, so that it doesn't block the main event loop

    audio_path = os.path.join(output_dir, "audio.mp3")
    if not os.path.exists(audio_path):
        raise FileNotFoundError("Error while creating the audio file temporary path")

    metadata['audio_path'] = audio_path
    return metadata


# ============== ENDPOINT ==============

@router.post("/api/transcribe/instagram", response_model=InstagramTranscriptionResponse)
async def transcribe_instagram(request: InstagramTranscriptionRequest):
    """
    Endpoint to transcribe the audio from an Instagram post, and fetch its metadata.

    Workflow:
    1. Downloads the audio with yt-dlp
    2. Uploads it to AssemblyAI
    3. Creates a transcription job
    4. Poll until completion of the transcription
    5. Returns the post transcription and metadata
    """
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir: # This structure ensures that the temporary directory is automatically deleted at the end of the block, even if an error occurs.

            # 1. Download the audio with yt-dlp, and retrieve the metadata of the post (duration, description, uploader name, upload date). The audio is stored in a temporary directory, and its path is returned in the "metadata" dict.
            try:
                metadata = await download_instagram_audio(request.url, temp_dir)
                audio_path = metadata['audio_path']
                duration = metadata['duration']
                print(f"[Instagram] Audio téléchargé: {audio_path} ({duration}s)")
                print(f"[Instagram] Compte: {metadata.get('uploader')} | Date: {metadata.get('upload_date')}")
            except Exception as e:
                print(f"[Instagram] Erreur téléchargement: {e}")
                return InstagramTranscriptionResponse(
                    status="error",
                    error_code="DOWNLOAD_FAILED",
                    message=f"Impossible de télécharger l'audio: {str(e)}"
                )

            # 2. Upload the audio to AssemblyAI and get the upload_url where the file will be transcribed on AssemblyAI's API.
            try:
                upload_url = await upload_to_assemblyai(audio_path)
            except Exception as e:
                print(f"[Instagram] Erreur upload: {e}")
                return InstagramTranscriptionResponse(
                    status="error",
                    error_code="UPLOAD_FAILED",
                    message=f"Échec de l'upload: {str(e)}"
                )

            # 3. Create the transcription job on AssemblyAI with the upload_url, and get the transcript_id to poll the result later.
            try:
                transcript_id = await create_transcription_job(upload_url)
            except Exception as e:
                print(f"[Instagram] Erreur création job: {e}")
                return InstagramTranscriptionResponse(
                    status="error",
                    error_code="TRANSCRIPTION_FAILED",
                    message=f"Échec de création du job: {str(e)}"
                )

            # 4. Poll until completion of the transcription, and get the result (transcript text, confidence score, etc.)
            try:
                TRANSCRIPTION_TIMEOUT_SECONDS = 120  # Max timeout for transcribing an Instagram audio (in seconds)
                result = await poll_transcription_result(transcript_id, TRANSCRIPTION_TIMEOUT_SECONDS)
                print(f"[Instagram] Confiance: {result.get('confidence')}")
                print("[Instagram] Transcription:", result.get("text"))
            except TimeoutError:
                return InstagramTranscriptionResponse(
                    status="error",
                    error_code="TIMEOUT",
                    message="Transcription took too long and was stopped"
                )
            except Exception as e:
                print(f"[Instagram] Erreur transcription: {e}")
                return InstagramTranscriptionResponse(
                    status="error",
                    error_code="TRANSCRIPTION_FAILED",
                    message=f"Transcription error: {str(e)}"
                )

        return InstagramTranscriptionResponse(
            status="completed",
            transcript=result.get("text"),
            confidence=result.get("confidence"),
            description=metadata.get('description'),
            uploader=metadata.get('uploader'),
            upload_date=metadata.get('upload_date')
        )

    except Exception as e:
        print(f"[Instagram] Erreur inattendue: {e}")
        return InstagramTranscriptionResponse(
            status="error",
            error_code="INTERNAL_ERROR",
            message=f"Erreur interne: {str(e)}"
        )
