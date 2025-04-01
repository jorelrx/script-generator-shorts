import os
import cv2
import moviepy as mp
from urllib.request import urlopen
from mutagen.mp3 import MP3

class VideoEditor:
    def __init__(self, output_path: str = "output.mp4"):
        self.output_path = output_path

    def get_audio_duration(self, audio_path: str) -> float:
        """ Retorna a duração do áudio em segundos """
        audio = MP3(audio_path)
        return audio.info.length
    
    def create_video(self, image_paths: list, audio_path: str, duration: int | None = None, fps: int = 30):
        if duration is None:
            audio_duration = self.get_audio_duration(audio_path)
            print(f"Duração do áudio: {audio_duration} segundos")
            if audio_duration is not None:
                duration = int(audio_duration)
            
        frames = []
        for img_path in image_paths:
            img = cv2.imread(img_path)
            img = cv2.resize(img, (1080, 1920))  # Ajusta para formato vertical
            frames.extend([img] * (fps * duration // len(image_paths)))
        
        height, width, layers = frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(self.output_path, fourcc, fps, (width, height))
        
        for frame in frames:
            video.write(frame)
        
        video.release()
        
        self.add_audio(audio_path)
    
    def add_audio(self, audio_path: str):
        video = mp.VideoFileClip(self.output_path)
        audio = mp.AudioFileClip(audio_path)
        audio = audio.with_duration(video.duration)
        final_video = video.with_audio(audio)
        final_video.write_videofile("final_" + self.output_path, codec="libx264", fps=30)
        os.remove(self.output_path)
