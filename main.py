import os
from dotenv import load_dotenv
from google_genai import GoogleGenAI
from text_to_speech import TextToSpeech
from image_creator import ImageCreator
from video_editor import VideoEditor
from youtube_uploader import YouTubeUploader

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
    script = googleGenerator.generate_script()
    print("Roteiro gerado:", script)

    # 2. Converter texto em audio
    tts = TextToSpeech(ELEVENLABS_API_KEY)
    audio_path = "audio.mp3"
    audio_file = tts.convert_text_to_speech(script, audio_path)

    # 3. Gerar imagens
    images = []
    while len(images) < IMAGE_COUNT:
        image_prompt = googleGenerator.generate_image_prompt()
        image = googleGenerator.generate_image(image_prompt)
        if image:
            images.append(image)
            print(f"Imagem {len(images)} gerada.")
            
    # Baixar as imagens
    image_paths = []
    for i in range(len(images)):
        image_path = f"image_{i}.png"
        images[i].save(image_path)
        image_paths.append(image_path)

    # 4. Criar vídeo
    editor = VideoEditor()
    editor.create_video(image_paths, audio_path)

if __name__ == "__main__":
    main()
