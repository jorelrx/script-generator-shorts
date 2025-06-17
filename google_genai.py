import os
from time import sleep
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from PIL import ImageFile
from io import BytesIO
import glob
import json
import re

class GoogleGenAI:
    """Class to interact with Google GenAI for generating motivational scripts."""
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_text = "gemini-2.0-flash"
        self.model_image = "gemini-2.0-flash-exp-image-generation"

    def generate_resume_episode(self) -> str:
        """Generate a resume episode using Google GenAI."""
        system_instruction = """Você é um roteirista criativo para a série animada infantil "Aventuras da Turma Encantada". Sua tarefa é gerar um resumo conciso e envolvente para um episódio da série. O resumo deve conter:

1. **Título do Episódio:** Crie um título atrativo.
2. **Introdução:** Apresente o cenário mágico e os personagens principais: Luna (unicórnio curiosa), Toto (coelho sábio), Mimi (fada criativa) e Bruno (ursinho protetor).
3. **Desenvolvimento:** Descreva o surgimento de um problema ou mistério (por exemplo, a descoberta de um objeto mágico ou um enigma a ser desvendado) e como os personagens se unem para enfrentá-lo.
4. **Clímax e Resolução:** Mostre o ponto alto da aventura, a solução do problema e a evolução dos personagens durante a jornada.
5. **Moral ou Lição:** Inclua uma mensagem positiva ou lição aprendida, ressaltando valores como amizade, coragem ou criatividade.

Utilize linguagem simples, adequada ao público infantil, e insira elementos mágicos e de fantasia para manter a narrativa envolvente. O resultado deve ser um resumo que capture a essência do episódio e desperte o interesse das crianças.
"""
        response = self.client.models.generate_content(
            model=self.model_text,
            config=types.GenerateContentConfig(
                max_output_tokens=8192,
                system_instruction=system_instruction
            ),
            contents="Crie um resumo de episódio.",
        )
        return response.text
    
    def generate_video_theme(self, prompt: str = "Crie um tema único e marcante para um vídeo motivacional.") -> str:
        """
        Gera um tema para o vídeo motivacional utilizando a API GenAi.
        """
        system_instruction = (
            "Você é um especialista em criação de conteúdo para vídeos motivacionais. "
            "Crie um tema único, impactante e que ressoe com pessoas que buscam inspiração e superação."
        )

        video_scripts = []
        for script_path in glob.glob(f"videos/motivacional/*/input/script/script_short.json"):
            with open(script_path, "r", encoding="utf-8") as file:
                content = json.load(file)
            if "title" in content:
                video_scripts.append({"theme": content["title"]})

        # Formata o histórico como mensagens anteriores da IA
        for h in video_scripts:
            print("historico", h)
        history_messages = [
            types.Content(role="model", parts=[types.Part(text=json.dumps(h))]) for h in video_scripts
        ]

        # Mensagem atual do usuário
        user_prompt = types.Content(role="user", parts=[types.Part(text=prompt)])

        # Junta as mensagens do histórico + prompt atual
        full_conversation = history_messages + [user_prompt]

        response = self.client.models.generate_content(
            model=self.model_text,
            config=types.GenerateContentConfig(
                max_output_tokens=50,
                response_mime_type="application/json",
                response_schema=types.Schema(
                                type = types.Type.OBJECT,
                                required = ["theme"],
                                properties = {
                                    "theme": types.Schema(
                                        type = types.Type.STRING,
                                    ),
                                },
                            ),
                system_instruction=system_instruction
            ),
            contents=full_conversation,
        )
        theme = response.text.strip()
        return theme
    
    def generate_script_with_history(self, video_type: str, prompt:str = "Crie um novo script", max_tokens: int = 8192) -> str:
        """Generate a motivational script using Google GenAI."""
        if video_type == "motivacional":
            system_instruction = """Você é um criador de conteúdo especialista em vídeos motivacionais e inspiradores. Crie um conteúdo impactante no formato JSON com os seguintes campos obrigatórios:

- "title": título forte e chamativo que atraia a atenção no estilo motivacional.
- "description": uma descrição envolvente com palavras-chave relacionadas à motivação, superação, mindset, filosofia estoica e produtividade.
- "video_name": nome simples para ser usado no nome do arquivo, por exemplo video_name.
- "script": um array de objetos, cada um contendo:
   - "text": uma frase do discurso motivacional (deve ser profunda, impactante ou reflexiva).
   - "image_description": uma descrição visual correspondente à frase, no estilo cinematográfico e emocional (ex: um homem sozinho em frente ao mar ao pôr do sol, uma mulher correndo sozinha na chuva, uma estrada deserta simbolizando jornada interior).

O conteúdo deve combinar os estilos:
1. Filosofia estoica e reflexões sobre a vida.
2. Superação pessoal, força interior, resiliência e dor transformada em força.
3. Mindset de sucesso, hábitos diários, produtividade, disciplina e foco.

Evite frases genéricas. Use uma linguagem envolvente, profunda e com emoção. O tom deve ser inspirador, forte e que gere identificação imediata com quem está assistindo. Use metáforas e analogias visuais para enriquecer as descrições de imagem.
Nunca utilize descrições negativas ou que possam gerar desconforto. O foco deve ser sempre na superação e na força interior.
** Nunca utilize image_description negativa, insegurança ou que possa gerar desconforto.**

Retorne apenas o JSON formatado.

"""
        elif video_type == "infantil":
            system_instruction = """Você é um assistente especializado em criar Scripts para Shorts de Youtube com o nincho "textos infantis e inspiradores". A partir do resumo do episódio fornecido. O Script deve um Tópico, Título, Ideia Central, Roteiro do vídeo e textos para gerar imagens.

Personagens: Luna (unicórnio curiosa), Toto (coelho sábio), Mimi (fada criativa) e Bruno (ursinho protetor).

- O video deve ter um roteiro de no máximo 80 segundos com o texto completo com uma narração completa.
- Os textos para as imagens deve ser uma lista que para cada item é uma descrição de imagem para um trecho do roteiro.
- Para cada item deve ter uma imagem que será utilizado enquanto o video está no trecho respectivo do roteiro.

- topic: Tópico do Short, 
- title: Título do Short, 
- video_name: Nome do vídeo, por exemplo, 'descobrindo_o_mundo',
- central_idea: Ideia central,
- scripts: Um objeto com os trechos do roteiro separados em uma lista contendo o personagem, texto do personagem e descrição da imagem que vai aparecer enquanto o personagem fala.

Deve retornar um json em formato string -> 
{
    "topic": "",
    "title": "",
    "video_name": "",
    "central_idea": "",
    "scripts":  {
        "character": "Nome do personagem da fala atual",
        "text": "Texto do personagem",
        "description_image": "Descrição da imagem que vai aparecer enquanto o personagem fala"
    }
}

"""

        video_scripts = []
        for script_path in glob.glob(f"videos/{video_type}/*/input/script/script_short.json"):
            with open(script_path, "r", encoding="utf-8") as file:
                video_scripts.append(file.read().strip())

        # Formata o histórico como mensagens anteriores da IA
        history_messages = [
            types.Content(role="model", parts=[types.Part(text=h)]) for h in video_scripts
        ]

        # Mensagem atual do usuário
        user_prompt = types.Content(role="user", parts=[types.Part(text=prompt)])

        # Junta as mensagens do histórico + prompt atual
        full_conversation = history_messages + [user_prompt]
        
        response = self.client.models.generate_content(
            model=self.model_text,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                system_instruction=system_instruction
            ),
            contents=full_conversation,
        )

        json_string = re.sub(r"```json|```", "", response.text).strip()

        return json_string
    
    def generate_image_prompt(self, script: str = "Crie uma descrição.") -> str:
        """Generate a prompt for image generation."""
        response = self.client.models.generate_content(
            model=self.model_text,
            config=types.GenerateContentConfig(
                max_output_tokens=500,
                system_instruction="""Você é um especialista em fazer prompt para ser utilizado em um gerador de imagens. Quero um prompt que passe a ideia de uma imagem motivacional e inspiradora, como uma imagem de um cêu bonito, uma cachoeira, uma praia, um horizonte belo. 

Deve ser breve e direto com a resposta.

Exemplo ->
Estilo: Pintura digital com traços suaves e cores vibrantes, inspirada em paisagens oníricas e arte impressionista.

Assunto: Uma praia paradisíaca com areia branca e fofa banhada por um mar azul turquesa cristalino. Um horizonte amplo e sereno se estende até onde a vista alcança, com o sol nascendo e irradiando luz dourada sobre as ondas. Silhuetas de coqueiros balançam suavemente com a brisa, transmitindo uma sensação de paz e tranquilidade.

Detalhes:

Praia: Areia com textura fina, ondas quebrando na praia, coqueiros na orla
"""
            ),
            contents=script,
        )
        return response.text
    
    def generate_image(self, script: str) -> (ImageFile.ImageFile | None):
        """Generate an image prompt based on the script."""
        try:
            response = self.client.models.generate_content(
                model=self.model_image,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                ),
                contents=script,
            )

            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    print(part.text)
                elif part.inline_data is not None:
                    image = Image.open(BytesIO((part.inline_data.data)))
                    return image
        except Exception as e:
            print(f"An error occurred: {e}")
        return None

    def generate_video(self, prompt: str) -> None:
        """Generate a video based on the prompt."""
        # Implement video generation logic here
        operation = self.client.models.generate_videos(
            model="veo-2.0-generate-001",
            prompt=prompt,
            config=types.GenerateVideosConfig(
                person_generation="allow_adult",  # "dont_allow" or "allow_adult"
                aspect_ratio="9:16",  # "16:9" or "9:16"
            ),
        )

        while not operation.done:
            sleep(20)
            operation = self.client.operations.get(operation)

        for n, generated_video in enumerate(operation.response.generated_videos):
            self.client.files.download(file=generated_video.video)
            generated_video.video.save(f"video{n}.mp4")  # save the video

if __name__ == "__main__":
    load_dotenv()
    # Example usage
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    googleGenAI = GoogleGenAI(api_key=GOOGLE_API_KEY)
    # response_theme = googleGenAI.generate_video_theme()
    # theme = json.loads(response_theme)
    # print("Tema do vídeo:", theme.get("theme"))
    # script_json = googleGenAI.generate_script_with_history("motivacional", f"Crie um script motivacional baseado no título: {theme.get("theme")}")
    # script = json.loads(script_json)
    # print("Roteiro gerado:", script)

    googleGenAI.generate_video("Crie um vídeo motivacional com o tema: A força interior é a chave para a superação.")  # Example prompt for video generation