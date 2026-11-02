import os
import time
import requests
from pydub import AudioSegment

# ---------------------------------------------------------------------------
# Sarvam (Hinglish) config - unchanged
# ---------------------------------------------------------------------------
# Sarvam's sync STT-translate API rejects audio longer than 30s.
# We slice each chunk into 25s pieces (with a 5s safety margin) before sending.
SARVAM_PIECE_SECONDS = 25

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

# ---------------------------------------------------------------------------
# Groq Whisper (English) config
# ---------------------------------------------------------------------------
GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_WHISPER_MODEL = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo")
GROQ_MAX_RETRIES = 4


def _send_to_groq(audio_path: str) -> str:
    """Send one audio file to Groq's Whisper API and return the transcript."""
    # Read the key at call time so it works with .env / HF secrets / Streamlit secrets
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set in environment / .env")

    headers = {"Authorization": f"Bearer {api_key}"}

    for attempt in range(1, GROQ_MAX_RETRIES + 1):
        with open(audio_path, "rb") as f:
            files = {"file": (os.path.basename(audio_path), f, "audio/flac")}
            data = {
                "model": GROQ_WHISPER_MODEL,
                "language": "en",
                "response_format": "json",
                "temperature": "0",
            }
            response = requests.post(
                GROQ_STT_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=300,
            )

        if response.ok:
            return response.json().get("text", "")

        # Rate limited -> wait and retry
        if response.status_code == 429 and attempt < GROQ_MAX_RETRIES:
            wait = float(response.headers.get("retry-after", 5 * attempt))
            print(f"  Groq rate limit hit, retrying in {wait:.0f}s "
                  f"(attempt {attempt}/{GROQ_MAX_RETRIES})...")
            time.sleep(wait)
            continue

        print(f"\n❌ Groq returned {response.status_code}")
        print(f"Response body: {response.text}\n")
        response.raise_for_status()

    return ""


def transcribe_chunk_whisper(chunk_path: str) -> str:
    """
    Transcribe one chunk with Whisper running on Groq (no local model needed).
    The chunk is converted to 16kHz mono FLAC first, which keeps a 10-minute
    chunk well under Groq's upload size limit.
    """
    audio = AudioSegment.from_file(chunk_path).set_frame_rate(16000).set_channels(1)
    compressed_path = f"{chunk_path}_groq.flac"
    audio.export(compressed_path, format="flac")

    try:
        return _send_to_groq(compressed_path).strip()
    finally:
        if os.path.exists(compressed_path):
            os.remove(compressed_path)


def _send_to_sarvam(piece_path: str) -> str:
    """Send one ≤30s WAV file to Sarvam and return the English transcript."""
    headers = {"api-subscription-key": SARVAM_API_KEY}

    with open(piece_path, "rb") as f:
        files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
        data = {"model": SARVAM_MODEL, "with_diarization": "false"}
        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

    if not response.ok:
        print(f"\n❌ Sarvam returned {response.status_code}")
        print(f"Response body: {response.text}\n")
        response.raise_for_status()

    return response.json().get("transcript", "")


def transcribe_chunk_sarvam(chunk_path: str) -> str:
    """
    Sarvam sync API only accepts ≤30s audio. We split this chunk into
    25-second pieces, send each separately, and join the transcripts.
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    audio = AudioSegment.from_wav(chunk_path)
    piece_ms = SARVAM_PIECE_SECONDS * 1000

    full_text = ""
    total_pieces = (len(audio) + piece_ms - 1) // piece_ms

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece = audio[start: start + piece_ms]
        piece_path = f"{chunk_path}_sv_{i}.wav"
        piece.export(piece_path, format="wav")

        try:
            print(f"  → Sarvam piece {i + 1}/{total_pieces} ...")
            full_text += _send_to_sarvam(piece_path) + " "
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()


def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    """
    Route one chunk to Groq Whisper or Sarvam depending on language choice.
    - english  → Whisper via Groq API
    - hinglish → Sarvam (translates to English while transcribing)
    """
    if language.lower() == "hinglish":
        return transcribe_chunk_sarvam(chunk_path)
    return transcribe_chunk_whisper(chunk_path)


def transcribe_all(chunks: list, language: str = "english") -> str:

    full_transcript = ""

    engine = "Sarvam AI" if language.lower() == "hinglish" else "Whisper (Groq API)"
    print(f"Using {engine} for transcription.")

    for i, chunk in enumerate(chunks):

        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

        text = transcribe_chunk(chunk, language=language)

        full_transcript += text + " "

    print("Transcription complete.")

    return full_transcript.strip()