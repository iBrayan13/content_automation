from typing import Any, Optional, List, Dict, Literal, Iterator

from elevenlabs.client import ElevenLabs

from src.core.settings import Settings


class ElevenLabsService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = ElevenLabs(api_key=self.settings.ELEVENLABS_API_KEY)

        self.voices: Dict[str, str] = {
            "female": "Qvbf0AoA7UZSgJUp8Ba5",
            "male": "l1zE9xgNpUTaQCZzpNJa",
        }

    def text_to_speech(self, text: str, voice: Literal['female', 'male']) -> Optional[bytes]:
        try:
            return self.client.generate(
                text=text,
                voice=self.voices[voice]
            )
        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            return None
        
    def save_audio(self, audio: Iterator[bytes], filename: str) -> bool:
        try:
            with open(filename, "wb") as f:
                for chunk in audio:
                    f.write(chunk)

            return True
        
        except Exception as e:
            print(f"Error saving audio: {str(e)}")
            return False

    def get_speech_on_file(self, filename: str, text: str, voice: Literal['female', 'male']) -> Optional[str]:
        try:
            bytes_iterator = self.text_to_speech(text, voice)
            if bytes_iterator is None:
                raise Exception("Error generating audio")

            if self.save_audio(bytes_iterator, filename):
                return filename
            
            raise Exception("Error saving audio")
        
        except Exception as e:
            print(f"Error getting speech on file: {str(e)}")
            return None
