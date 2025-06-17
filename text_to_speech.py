import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

class TextToSpeech:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def convert_text_to_speech(self, text: str, output_path: str, voice: str = "y3X5crcIDtFawPx7bcNq", language: str = "pt"):
        try:
            client = ElevenLabs(
                api_key=self.api_key,
            )
            audio = client.text_to_speech.convert(
                voice_id=voice,
                output_format="mp3_44100_128",
                text=text,
                model_id="eleven_multilingual_v2",
            )

            if audio is None:
                return None

            # Salvar áudio em arquivo
            with open(output_path, "wb") as f:
                for chunk in audio:
                    if chunk:
                        f.write(chunk)

            return output_path
        except Exception as e:
            return None

if __name__ == "__main__":
    load_dotenv()

    # Definir os segredos e parâmetros
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    # Exemplo de uso
    tts = TextToSpeech(api_key=ELEVENLABS_API_KEY)
    audio_path = tts.convert_text_to_speech("Vamos decifrar os símbolos misteriosos!", "output.mp3", "tS45q0QcrDHqHoaWdCDR")
    print(f"Áudio salvo em: {audio_path}")