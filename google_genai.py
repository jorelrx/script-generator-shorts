from google import genai
from google.genai import types
from PIL import Image
from PIL import ImageFile
from io import BytesIO

class GoogleGenAI:
    """Class to interact with Google GenAI for generating motivational scripts."""
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_text = "gemini-2.0-flash"
        self.model_image = "gemini-2.0-flash-exp-image-generation"
    
    def generate_script(self, prompt: str = "Crie um texto motivacional.", max_tokens: int = 300) -> str:
        """Generate a motivational script using Google GenAI."""
        response = self.client.models.generate_content(
            model=self.model_text,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                system_instruction="Você é um assistente especializado em criar textos motivacionais e inspiradores."
            ),
            contents=prompt,
        )
        return response.text
    
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
        return None