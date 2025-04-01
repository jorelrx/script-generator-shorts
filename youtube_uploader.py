from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json

class YouTubeUploader:
    def __init__(self, client_secrets_file: str, credentials_file: str):
        self.client_secrets_file = client_secrets_file
        self.credentials_file = credentials_file
        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.youtube = self.get_authenticated_service()

    def get_authenticated_service(self):
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

    def upload_video(self, video_path: str, title: str, description: str, tags: list, category_id: str = "22", privacy_status: str = "public"):
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
