import json
import os

from dotenv import load_dotenv
from google_genai import GoogleGenAI
from text_to_speech import TextToSpeech
from video_editor import VideoEditor

# Carregar variáveis de ambiente
load_dotenv()

# Definir os segredos e parâmetros
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Definir parâmetros
TOPIC = "superação e confiança"
STYLE = "cinematic"
IMAGE_COUNT = 3  # Número de imagens geradas para o vídeo
TAGS = ["motivação", "autoajuda", "superação"]
CATEGORY_ID = "22"  # Categoria do YouTube

def main():
    googleGenerator = GoogleGenAI(GOOGLE_API_KEY)

    # 1. Gerar o roteiro
    script_json = googleGenerator.generate_script()
    script = json.loads(script_json)
    print("Roteiro gerado:", script)

    # 3. Gerar imagens
    images = []
    for text in script['image_texts']:
        print("Gerando imagem para:", text)
        image_prompt = googleGenerator.generate_image_prompt(text)
        print("Prompt gerado:", image_prompt)
        image = googleGenerator.generate_image(image_prompt)
        if image:
            images.append(image)
            print(f"Imagem {len(images)} gerada.")

    # 2. Converter os textos em audios
    tts = TextToSpeech(ELEVENLABS_API_KEY)
    audio_paths = []
    for i, text in enumerate(script['scripts']):
        audio_path = f"audio_{i}.mp3"
        tts.convert_text_to_speech(text, audio_path)
        audio_paths.append(audio_path)
            
    # Baixar as imagens
    image_paths = []
    for i in range(len(images)):
        image_path = f"image_{i}.png"
        images[i].save(image_path)
        image_paths.append(image_path)

    # 4. Criar vídeo
    editor = VideoEditor()
    editor.create_video(image_paths, audio_paths)

if __name__ == "__main__":
    main()
