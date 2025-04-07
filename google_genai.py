import os
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
    
    def generate_script(self, prompt: str = "Crie um texto motivacional.", max_tokens: int = 8192) -> str:
        """Generate a motivational script using Google GenAI."""
        video_scripts = []
        for script_path in glob.glob("videos/*/input/script/script_short.txt"):
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
                system_instruction="""Você é um assistente especializado em criar Scripts para Shorts de Youtube com o nincho "textos motivacionais e inspiradores". O Script deve um Tópico, Título, Ideia Central, Roteiro do vídeo e textos para gerar imagens. 

- O video deve ter um roteiro de no máximo 50 segundos com o texto completo com uma narração completa.
- Os textos para as imagens deve ser uma lista que para cada item é uma descrição de imagem para um trecho do roteiro.
- Para cada item deve ter uma imagem que será utilizado enquanto o video está no trecho respectivo do roteiro.

- topic: Tópico do Short, 
- title: Título do Short, 
- video_name: Nome do vídeo, por exemplo, 'superacao_e_confianca',
- central_idea: Ideia central,
- scripts: Trechos do roteiro separados em uma lista,
- image_texts: Para cada item no 'scripts', deve ter um 'image_texts' com a descrição da imagem que vai aparecer durante o item do 'script' equivalente.

Deve retornar um json em formato string -> 
{
    "topic": "",
    "title": "",
    "video_name": "",
    "central_idea": "",
    "scripts":  ["Item descrecendo um trecho do roteiro"]
    "image_texts": ["Item descrevendo imagem que equivale ao item em 'script'"]
}

"""
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

Praia: Areia com textura fina, ondas quebrando na praia, coqueiros na orla"""
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
    
if __name__ == "__main__":
    load_dotenv()
    # Example usage
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    googleGenAI = GoogleGenAI(api_key=GOOGLE_API_KEY)
    script_json = googleGenAI.generate_script()
    script = json.loads(script_json)
    print("Roteiro gerado:", script)