import json
import os
from time import sleep

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

CHARACTER_VOICES = {
    "Luna": "y9CNRBALdlEecGD3RnmT",
    "Toto": "tS45q0QcrDHqHoaWdCDR",
    "Mimi": "iScHbNW8K33gNo3lGgbo",
    "Bruno": "y3X5crcIDtFawPx7bcNq",
    "Narrador": "CstacWqMhJQlnfLPxRG4"
}

TAGS = [
    "shorts",
    "#guia",
    "#Motivacional",
    "#universo",
    "#leidaatração",
    "#motivacional",
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

def post_short(tipo_video: str, video_name: str, video_title: str, video_tags, video_description: str):
    if tipo_video == "motivacional":
        cred_path = "channels/canal_motivacional/client_secret_motivacional.json"
        pickle_path = "channels/canal_motivacional/credentials_token.pickle"
        video_path = f"videos/motivacional/{video_name}/output/{video_name}_with_subtitles.mp4"
        shorts_tags_title = "#fé #universo #motivacional #leidaatração"
        shorts_tags_description = "#universo #leidaatração #motivacional #motivacao #inspiracao #guia #superacao #sociologia #filosofia"
    elif tipo_video == "infantil":
        cred_path = "channels/canal_infantil/client_secret_infantil.json"
        pickle_path = "channels/canal_infantil/credentials_token.pickle"
        video_path = f"videos/infantil/{video_name}/output/{video_name}_with_subtitles.mp4"
        shorts_tags_title = "#infantil #desenhos"
        shorts_tags_description = "#infantil #desenhos animados #canal_infantil"
    else:
        raise ValueError("Tipo de vídeo inválido.")
    
    # Verificar se o título excede 100 caracteres
    full_title = f"{video_title} {shorts_tags_title} #shorts"
    while len(full_title) > 100:
        shorts_tags_title = " ".join(shorts_tags_title.split()[:-1])  # Remove a última tag
        full_title = f"{video_title} {shorts_tags_title} #shorts"
    print("Titulo do vídeo:", full_title)
    print("Descrição do vídeo:", video_description)
    print("Tags do vídeo:", video_tags)

    uploader = YouTubeUploader(
        client_secrets_file=cred_path,
        credentials_file=pickle_path
    )

    response = uploader.upload_video(
        video_path=video_path,
        title=full_title,
        description=f"{video_description} {shorts_tags_description} #shorts #short",
        tags=video_tags,
        privacy_status="public",
    )

    print(f"✅ Vídeo enviado com sucesso! ID: {response['id']}")
    print(f"✅ Link do vídeo: https://www.youtube.com/shorts/{response['id']}")

def geretate_motivacional_video():
    googleGenerator = GoogleGenAI(GOOGLE_API_KEY)

    # 0. Gerar o tema do vídeo
    theme = None
    count = 0
    while theme is None:
        try:
            response_theme = googleGenerator.generate_video_theme()
            print("Response theme:", response_theme)
            theme = json.loads(response_theme)
            print("Tema do vídeo:", theme.get("theme"))
        except Exception as e:
            print(f"Erro ao gerar tema: {e}")
            
            if count >= 3:
                raise Exception("Falha ao gerar tema após 3 tentativas.")
            count += 1
            
            continue
    # 1. Gerar o roteiro
    script_json = googleGenerator.generate_script_with_history("motivacional", f"Crie um script motivacional baseado no título: {theme.get("theme")}. \n Nunca utilize image_description negativa, que gere insegurança ou que possa gerar desconforto.")
    script_data = json.loads(script_json)
    print("Roteiro gerado:", script_data)
    title = script_data.get("title")
    description = script_data.get("description")
    video_name = script_data.get("video_name")
    script_segments = script_data.get("script", [])

    if not script_segments:
        raise ValueError("O script não contém nenhum segmento.")

    audio_files = []
    image_prompts = []

    # Salvar o script na pasta 'script' usando o 'video_name' gerado no próprio script
    script_folder = f"videos/motivacional/{video_name}/input/script"
    os.makedirs(script_folder, exist_ok=True)
    script_path = os.path.join(script_folder, "script_short.json")
    with open(script_path, "w", encoding="utf-8") as script_file:
        json.dump(script_data, script_file, ensure_ascii=False, indent=4)
    print(f"Roteiro salvo em: {script_path}")

    tts = TextToSpeech(ELEVENLABS_API_KEY)
    audio_paths = []
    audio_folder = f"videos/motivacional/{video_name}/input/audio"
    os.makedirs(audio_folder, exist_ok=True)
    image_paths = []
    for index, segment in enumerate(script_segments):
        text_segment = segment.get("text", "")
        img_desc = segment.get("image_description", "")
        image = None
        count = 0

        print("Gerando imagem para:", img_desc)
        image_prompt = googleGenerator.generate_image_prompt(img_desc)
        print("Prompt gerado:", image_prompt)

        while image is None and count < 5:
            image = googleGenerator.generate_image(image_prompt)
            if image:
                print(f"Imagem {len(image_paths) + 1} gerada.")
                script_folder = f"videos/motivacional/{video_name}/input/script"
                video_folder = f"videos/motivacional/{video_name}/input/image"
                os.makedirs(script_folder, exist_ok=True)
                os.makedirs(video_folder, exist_ok=True)
                script_path = os.path.join(script_folder, f"script_image{len(image_paths)}.json")
                with open(script_path, "w", encoding="utf-8") as script_file:
                    json.dump(image_prompt, script_file, ensure_ascii=False, indent=4)
                print(f"Roteiro salvo em: {script_path}")

                image_path = os.path.join(video_folder, f"image_{len(image_paths)}.png")
                image.save(image_path)
                image_paths.append(image_path)

                count = 0
                print(f"Imagem {len(image_paths)} salva.")
            else:
                print("Erro ao gerar imagem. Tentando novamente...")
                sleep(10)
                count += 1

            if count >= 5:
                print("Falha ao gerar imagem após 5 tentativas. Aguardando 1 minuto")
                sleep(60)
                count = 0

        audio_path = os.path.join(audio_folder, f"audio_{len(audio_paths)}.mp3")
        tts.convert_text_to_speech(text_segment, audio_path)
        audio_paths.append(audio_path)

    # # 2. Gerar imagens e salvar imagens
    # image_paths = []
    # for text in script['image_texts']:
    #     image = None
    #     count = 0

    #     print("Gerando imagem para:", text)
    #     image_prompt = googleGenerator.generate_image_prompt(text)
    #     print("Prompt gerado:", image_prompt)

    #     while image is None and count < 3:
    #         image = googleGenerator.generate_image(image_prompt)
    #         if image:
    #             print(f"Imagem {len(image_paths) + 1} gerada.")
    #             script_folder = f"videos/motivacional/{script['video_name']}/input/script"
    #             video_folder = f"videos/motivacional/{script['video_name']}/input/image"
    #             os.makedirs(script_folder, exist_ok=True)
    #             os.makedirs(video_folder, exist_ok=True)
    #             script_path = os.path.join(script_folder, f"script_image{len(image_paths)}.json")
    #             with open(script_path, "w", encoding="utf-8") as script_file:
    #                 json.dump(script, script_file, ensure_ascii=False, indent=4)
    #             print(f"Roteiro salvo em: {script_path}")

    #             image_path = os.path.join(video_folder, f"image_{len(image_paths)}.png")
    #             image.save(image_path)
    #             image_paths.append(image_path)

    #             count = 0
    #             print(f"Imagem {len(image_paths)} salva.")
    #         else:
    #             print("Erro ao gerar imagem. Tentando novamente...")
    #             sleep(10)
    #             count += 1

    #         if count >= 5:
    #             print("Falha ao gerar imagem após 5 tentativas. Aguardando 1 minuto")
    #             sleep(60)
    #             count = 0

    # # 3. Converter os textos em audios
    # tts = TextToSpeech(ELEVENLABS_API_KEY)
    # audio_paths = []
    # audio_folder = f"videos/motivacional/{script['video_name']}/input/audio"
    # os.makedirs(audio_folder, exist_ok=True)
    
    # for i, text in enumerate(script['scripts']):
    #     audio_path = os.path.join(audio_folder, f"audio_{i}.mp3")
    #     tts.convert_text_to_speech(text, audio_path)
    #     audio_paths.append(audio_path)

    # 4. Criar vídeo
    editor = VideoEditor()
    editor.create_video(video_name, "motivacional", 30)

    # 5. Postar video no YouTube
    post_short("motivacional", video_name, title, TAGS, description)

def get_voice_id(personagem: str) -> str:
    """
    Retorna o ID da voz com base no personagem informado.
    Se não encontrar, retorna um ID de voz padrão.
    """
    return CHARACTER_VOICES.get(personagem, "CstacWqMhJQlnfLPxRG4")

def geretate_infantil_video():
    googleGenerator = GoogleGenAI(GOOGLE_API_KEY)
    tts = TextToSpeech(ELEVENLABS_API_KEY)

    # 1. Gerar o roteiro
    resume_episode = googleGenerator.generate_resume_episode()
    script_json = googleGenerator.generate_script_with_history("infantil", resume_episode)
    script = json.loads(script_json)
    print("Roteiro gerado:", script)
    
    # Salvar o script na pasta 'script' usando o 'video_name' gerado no próprio script
    script_folder = f"videos/infantil/{script['video_name']}/input/script"
    os.makedirs(script_folder, exist_ok=True)
    script_path = os.path.join(script_folder, "script_short.json")
    with open(script_path, "w", encoding="utf-8") as script_file:
        json.dump(script, script_file, ensure_ascii=False, indent=4)
    print(f"Roteiro salvo em: {script_path}")

    # 2. Gerar imagens e audios
    
    image_paths = []
    audio_paths = []
    for scene in script['scripts']:
        print("Gerando imagem para:", scene['description_image'])
        image_prompt = scene['description_image']
        image_prompt_complete = f"Você é um gerador de imagens especializado em ilustrações no estilo cartoon. Sua tarefa é criar uma imagem que capture fielmente a seguinte descrição, garantindo que o resultado seja vibrante, colorido e adequado para o público infantil: \n {image_prompt}. \n Por favor, utilize o estilo cartoon, com traços suaves e expressivos, cores vibrantes e um toque de fantasia para tornar a cena encantadora e atrativa para crianças. Certifique-se de que a imagem represente claramente os personagens e o ambiente descritos na frase. \n Luna (unicórnio curiosa), Toto (coelho sábio), Mimi (fada criativa) e Bruno (ursinho protetor)."
        print("Prompt gerado:", image_prompt)

        image = None
        count = 0
        while image is None and count < 3:
            image = googleGenerator.generate_image(image_prompt_complete)
            if image:
                print(f"Imagem {len(image_paths) + 1} gerada.")
                script_folder = f"videos/infantil/{script['video_name']}/input/script"
                video_folder = f"videos/infantil/{script['video_name']}/input/image"
                os.makedirs(script_folder, exist_ok=True)
                os.makedirs(video_folder, exist_ok=True)
                script_path = os.path.join(script_folder, f"script_image{len(image_paths)}.json")
                with open(script_path, "w", encoding="utf-8") as script_file:
                    json.dump(script, script_file, ensure_ascii=False, indent=4)
                print(f"Roteiro salvo em: {script_path}")

                image_path = os.path.join(video_folder, f"image_{len(image_paths)}.png")
                image.save(image_path)
                image_paths.append(image_path)

                count = 0
                print(f"Imagem {len(image_paths)} salva.")
            else:
                count += 1

            if count >= 3:
                raise Exception("Falha ao gerar imagem após 3 tentativas.")
            
        audio_folder = f"videos/infantil/{script['video_name']}/input/audio"
        os.makedirs(audio_folder, exist_ok=True)

        audio_path = os.path.join(audio_folder, f"audio_{len(audio_paths)}.mp3")
        voice_id = get_voice_id(scene["character"])
        audio_path_generated = None
        while audio_path_generated is None:
            audio_path_generated = tts.convert_text_to_speech(scene['text'], audio_path, voice_id)
        audio_paths.append(audio_path)
        print(f"Áudio {len(audio_paths) + 1} gerado e salvo em: {audio_path}")

    # 4. Criar vídeo
    editor = VideoEditor()
    video_output_folder = f"videos/infantil/{script['video_name']}/output"
    os.makedirs(video_output_folder, exist_ok=True)
    video_path = os.path.join(video_output_folder, f"{script['video_name']}_with_subtitles.mp4")
    editor.create_video(script['video_name'], "infantil", 30)
    print(f"Vídeo gerado e salvo em: {video_path}")

    # 5. Postar vídeo no YouTube
    infantil_tags = [
        "desenhos animados", "canal infantil", "histórias infantis", "contos mágicos", "aventuras para crianças", 
        "vídeos educativos", "animação infantil", "personagens mágicos", "série infantil", "turma encantada", 
        "contos de fadas", "mundo encantado", "episódios infantis", "vídeos para crianças", "histórias com moral", 
        "diversão infantil", "conteúdo seguro para crianças", "amigos mágicos", "histórias animadas", "canal kids", "shorts"
    ]
    
    post_short("infantil", script['video_name'], script['title'], infantil_tags, script['central_idea'])

if __name__ == "__main__":
    print("Selecione uma opção:")
    print("1. Criar vídeo do início")
    print("2. Postar vídeo no YouTube")
    print("3. Compilar vídeo")
    opcao = input("Digite o número da opção desejada: ")

    if opcao == "1":
        print("Selecione o tipo do video:")
        print("1. Motivacional")
        print("2. Infantil")
        tipo_video = input("Digite o número do tipo de vídeo desejado: ")
        if tipo_video == "1":
            geretate_motivacional_video()
        elif tipo_video == "2":
            geretate_infantil_video()
    elif opcao == "2":
        print("Selecione o tipo do video:")
        print("1. Motivacional")
        print("2. Infantil")
        tipo_video = input("Digite o número do tipo de vídeo desejado: ")

        video_name = input("Informe o nome do vídeo: ")
        video_path = f"videos/{tipo_video}/{video_name}/output/{video_name}_with_subtitles.mp4"
        script_path = f"videos/{tipo_video}/{video_name}/input/script/script_short.json"

        if not os.path.exists(video_path):
            print(f"Erro: O arquivo de vídeo '{video_path}' não foi encontrado.")
            exit(1)

        if not os.path.exists(script_path):
            print(f"Erro: O arquivo de script '{script_path}' não foi encontrado.")
            exit(1)

        with open(script_path, "r", encoding="utf-8") as script_file:
            script = json.load(script_file)

        if tipo_video == "motivacional":
            post_short(tipo_video, script['video_name'], script['title'], TAGS, script['description'])
        elif tipo_video == "infantil":
            tags_infantil = [
                "desenhos animados", "canal infantil", "histórias infantis", "contos mágicos", "aventuras para crianças", 
                "vídeos educativos", "animação infantil", "personagens mágicos", "série infantil", "turma encantada", 
                "contos de fadas", "mundo encantado", "episódios infantis", "vídeos para crianças", "histórias com moral", 
                "diversão infantil", "conteúdo seguro para crianças", "amigos mágicos", "histórias animadas", "canal kids", "shorts"
            ]
            post_short(tipo_video, script['video_name'], script['title'], tags_infantil, script['description'])
    elif opcao == "3":
        print("Selecione o tipo do video:")
        print("1. Motivacional")
        print("2. Infantil")
        tipo_video = input("Digite o número do tipo de vídeo desejado: ")

        video_name = input("Informe o nome do vídeo: ")
        video_path = f"videos/{tipo_video}/{video_name}/output/{video_name}_with_subtitles.mp4"

        editor = VideoEditor()
        editor.create_video(video_name, tipo_video, 30)
        print(f"Vídeo compilado e salvo em: {video_path}")
    else:
        print("Opção inválida. Encerrando o programa.")
