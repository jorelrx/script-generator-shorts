from elevenlabs import ElevenLabs

class TextToSpeech:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def convert_text_to_speech(self, text: str, output_path: str, voice: str = "IKne3meq5aSn9XLyUdCD"):
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

            # Salvar áudio em arquivo
            with open(output_path, "wb") as f:
                for chunk in audio:
                    if chunk:
                        f.write(chunk)

            return output_path
        except Exception as e:
            return f"Erro na requisição: {e}"
