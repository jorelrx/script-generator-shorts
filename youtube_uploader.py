from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class YouTubeUploader:
    """
    Classe responsável por autenticar com a API do YouTube e realizar upload de vídeos.

    A autenticação é feita usando OAuth 2.0 com credenciais fornecidas pelo Google Cloud Console.
    As credenciais são armazenadas em arquivo local (pickle) para reutilização sem reautenticação.

    Attributes:
        client_secrets_file (str): Caminho para o arquivo client_secret.json do Google Cloud.
        credentials_file (str): Caminho onde as credenciais autenticadas serão salvas e reutilizadas.
        youtube (googleapiclient.discovery.Resource): Objeto de serviço da API do YouTube autenticado.
    """

    def __init__(self, client_secrets_file: str, credentials_file: str):
        """
        Inicializa o uploader com os arquivos de autenticação.

        Args:
            client_secrets_file (str): Caminho para o arquivo client_secret.json.
            credentials_file (str): Caminho para salvar/recuperar as credenciais do usuário.
        """
        self.client_secrets_file = client_secrets_file
        self.credentials_file = credentials_file
        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.youtube = self.get_authenticated_service()

    def get_authenticated_service(self):
        """
        Autentica com a API do YouTube usando OAuth 2.0 e retorna o serviço autenticado.

        Se as credenciais já existirem e forem válidas, são reutilizadas. Caso contrário,
        será iniciado um novo fluxo de autenticação no navegador.

        Returns:
            googleapiclient.discovery.Resource: Objeto autenticado da API do YouTube.
        """
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        import os
        import pickle

        creds = None
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, "rb") as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, ["https://www.googleapis.com/auth/youtube.upload"]
                )
                creds = flow.run_local_server(port=0)
            with open(self.credentials_file, "wb") as token:
                pickle.dump(creds, token)
        
        return build(self.api_service_name, self.api_version, credentials=creds)

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list,
        category_id: str = "22",
        privacy_status: str = "unlisted"
    ):
        """
        Realiza o upload de um vídeo para o YouTube.

        Args:
            video_path (str): Caminho do arquivo de vídeo a ser enviado.
            title (str): Título do vídeo.
            description (str): Descrição do vídeo.
            tags (list): Lista de tags (palavras-chave) para o vídeo.
            category_id (str, optional): ID da categoria do vídeo (padrão: "22").
            privacy_status (str, optional): Status de privacidade: "public", "private", "unlisted".

        Returns:
            dict: Resposta da API com os dados do vídeo enviado, incluindo o vídeo ID.
        """
        request_body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status
            }
        }
        
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        
        request = self.youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media
        )
        response = request.execute()
        
        return response


if __name__ == "__main__":
    """
    Exemplo de uso da classe YouTubeUploader.
    Realiza o upload de um vídeo chamado 'meu_video.mp4'.
    """
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
        video_path=f"videos/legado_eterno/output/legado_eterno_with_subtitles.mp4",
        title=f"Deixe Sua Marca no Mundo. #motivacao #guia #filosofia #shorts",
        description=f"Inspirar as pessoas a encontrarem seu propósito e a construírem um legado significativo. #motivacao #inspiracao #guia #superacao #sociologia #filosofia #shorts #short",
        tags=tags,
        privacy_status="public",
    )

    print(f"✅ Vídeo enviado com sucesso! ID: {response['id']}")
    print(f"✅ Short Link: https://www.youtube.com/shorts/{response['id']}")