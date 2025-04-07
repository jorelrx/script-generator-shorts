import json
import os

from dotenv import load_dotenv
from google_genai import GoogleGenAI
from text_to_speech import TextToSpeech
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
    script_json = googleGenerator.generate_script()
    script = json.loads(script_json)
    print("Roteiro gerado:", script)

    # Salvar o script na pasta 'script' usando o 'video_name' gerado no próprio script
    script_folder = f"videos/{script['video_name']}/input/script"
    os.makedirs(script_folder, exist_ok=True)
    script_path = os.path.join(script_folder, "script_short.json")
    with open(script_path, "w", encoding="utf-8") as script_file:
        json.dump(script, script_file, ensure_ascii=False, indent=4)
    print(f"Roteiro salvo em: {script_path}")

    # 3. Gerar imagens
    images = []
    for text in script['image_texts']:
        print("Gerando imagem para:", text)
        image_prompt = googleGenerator.generate_image_prompt(text)
        print("Prompt gerado:", image_prompt)
        image = googleGenerator.generate_image(image_prompt)
        if image:
            images.append(image)
            script_folder = f"videos/{script['video_name']}/input/script"
            os.makedirs(script_folder, exist_ok=True)
            script_path = os.path.join(script_folder, f"script_image{len(images)}.json")
            with open(script_path, "w", encoding="utf-8") as script_file:
                json.dump(script, script_file, ensure_ascii=False, indent=4)
            print(f"Roteiro salvo em: {script_path}")

            print(f"Imagem {len(images)} gerada.")

    # 2. Converter os textos em audios
    tts = TextToSpeech(ELEVENLABS_API_KEY)
    audio_paths = []
    audio_folder = f"videos/{script['video_name']}/input/audio"
    os.makedirs(audio_folder, exist_ok=True)
    
    for i, text in enumerate(script['scripts']):
        audio_path = os.path.join(audio_folder, f"audio_{i}.mp3")
        tts.convert_text_to_speech(text, audio_path)
        audio_paths.append(audio_path)
            
    # Baixar as imagens
    image_paths = []
    video_folder = f"videos/{script['video_name']}/input/image"
    os.makedirs(video_folder, exist_ok=True)
    
    for i in range(len(images)):
        image_path = os.path.join(video_folder, f"image_{i}.png")
        images[i].save(image_path)
        image_paths.append(image_path)

    # 4. Criar vídeo
    editor = VideoEditor()
    editor.create_video(script['video_name'], 30)

    uploader = YouTubeUploader(
        client_secrets_file="assets/client_secret.json",
        credentials_file="credentials_token.pickle"
    )

    tags = [
        "shorts",
        "#filosofia",
        "#sociologia",
        "#guia",
        "Autoestima",
        "Autoconhecimento",
        "Confiança",
        "Aceitação",
        "AmorPróprio",
        "CrescimentoPessoal",
        "Brilhe",
        "LuzInterior",
        "Autenticidade",
        "Empoderamento",
        "JornadaPessoal",
        "Reflexão",
        "Inspiração",
        "Motivação",
        "FelicidadeInterior",
        "Extraordinário",
        "DesenvolvimentoPessoal",
        "TransformaçãoPessoal"
    ]

    response = uploader.upload_video(
        video_path=f"videos/{script['video_name']}/output/{script['video_name']}_with_subtitles.mp4",
        title=f"{script['title']} #motivacao #guia #filosofia #shorts",
        description=f"{script['central_idea']} #motivacao #inspiracao #guia #superacao #sociologia #filosofia #shorts #short",
        tags=tags,
        privacy_status="public",
    )

    print(f"✅ Vídeo enviado com sucesso! ID: {response['id']}")

if __name__ == "__main__":
    main()
