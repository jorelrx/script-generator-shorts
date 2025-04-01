import requests
import time

class ImageCreator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://cloud.leonardo.ai/api/rest/v1/generations"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def generate_image(self, prompt: str, model_id: str = "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3", width: int = 1024, height: int = 1024, num_images: int = 1, contrast: float = 3.5, alchemy: bool = True, style_uuid: str = "111dc692-d470-4eec-b791-3475abac4c46", enhance_prompt: bool = False):
        payload = {
            "modelId": model_id,
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_images": num_images,
            "contrast": contrast,
            "alchemy": alchemy,
            "enhancePrompt": enhance_prompt
        }
        if style_uuid:
            payload["styleUUID"] = style_uuid

        response = requests.post(self.api_url, headers=self.headers, json=payload)
        if response.status_code == 200:
            generation_id = response.json().get("sdGenerationJob", {}).get("generationId")
            if generation_id:
                return self._wait_for_images(generation_id)
            else:
                raise Exception("Falha ao obter o ID da geração.")
        else:
            raise Exception(f"Erro na solicitação: {response.status_code} - {response.text}")

    def _wait_for_images(self, generation_id: str, timeout: int = 60, interval: int = 5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = requests.get(f"{self.api_url}/{generation_id}", headers=self.headers)
            if response.status_code == 200:
                data = response.json().get("generations_by_pk", {})
                status = data.get("status")
                if status == "COMPLETE":
                    return [img["url"] for img in data.get("generated_images", [])]
                elif status == "FAILED":
                    raise Exception("A geração da imagem falhou.")
            time.sleep(interval)
        raise TimeoutError("Tempo limite excedido ao aguardar a geração da imagem.")