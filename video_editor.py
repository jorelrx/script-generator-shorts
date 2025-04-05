import os
import cv2
from moviepy import VideoFileClip, CompositeVideoClip, ImageClip, AudioFileClip, CompositeAudioClip
from moviepy import vfx, afx
from mutagen.mp3 import MP3

class VideoEditor:
    def __init__(self, output_path: str = "output.mp4"):
        self.output_path = output_path

    def get_audio_duration(self, audio_path: str) -> float:
        """ Retorna a duração do áudio em segundos """
        audio = MP3(audio_path)
        return audio.info.length

    def create_video(self, video_name: str, fps: int = 30):
        """
        Cria um vídeo com base em imagens e áudios encontrados nos diretórios especificados.
        Adiciona um áudio de fundo e transições entre os vídeos gerados.

        :param video_name: Nome do vídeo (usado para localizar os arquivos)
        :param fps: Frames por segundo do vídeo
        """
        base_dir = f"videos/{video_name}"
        img_dir = f"{base_dir}/input/image"
        audio_dir = f"{base_dir}/input/audio"
        backsong_path = "assets/backsong.mp3"

        img_paths = sorted([os.path.join(img_dir, f) for f in os.listdir(img_dir)
                            if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        audio_paths = sorted([os.path.join(audio_dir, f) for f in os.listdir(audio_dir)
                              if f.lower().endswith('.mp3')])

        if len(img_paths) != len(audio_paths):
            raise ValueError("O número de imagens deve ser igual ao número de áudios.")

        # Criação de vídeos individuais para cada imagem
        video_clips = []
        for img_path, audio_path in zip(img_paths, audio_paths):
            audio_duration = self.get_audio_duration(audio_path)
            img = cv2.imread(img_path)
            height, width, _ = img.shape

            # Cria um vídeo para a imagem com a duração do áudio
            video_path = img_path.replace('.jpg', '.mp4').replace('.png', '.mp4')
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

            for _ in range(int(fps * audio_duration)):
                video_writer.write(img)
            video_writer.release()

            # Adiciona o vídeo gerado à lista de clipes
            video_clip = VideoFileClip(video_path).with_duration(audio_duration)
            video_clips.append(video_clip)
            
        # Aplica fade-in e fade-out entre os vídeos
        final_clips = []
        current_time = 1
        for i, clip in enumerate(video_clips):
            if i == len(video_clips) - 1:
                clip = clip.with_start(current_time).with_duration(clip.duration + 1.5)
                clip = clip.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])
            else:
                clip = clip.with_start(current_time).with_duration(clip.duration)
                clip = clip.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])

            current_time += clip.duration

            final_clips.append(clip)
            
        # Combina todos os clipes em um único vídeo
        combined_video = CompositeVideoClip(final_clips)

        # Adiciona o áudio ao vídeo final
        self.add_audio(audio_paths, backsong_path, combined_video, video_name)

    def add_audio(self, audio_paths: list[str], backsong_path: str, video: CompositeVideoClip, video_name: str):
        """
        Adiciona os áudios ao vídeo final, sobrepondo-os ao áudio de fundo (backsong).
        O backsong continua tocando enquanto os áudios individuais são reproduzidos.

        :param audio_paths: Lista de caminhos dos arquivos de áudio
        :param backsong_path: Caminho do áudio de fundo
        :param video: Objeto do vídeo combinado
        """
        audio_clips = []
        start_time = 1  # Inicia após 1 segundo do backsong

        # Adiciona os áudios individuais com seus tempos de início
        for audio_path in audio_paths:
            audio_duration = self.get_audio_duration(audio_path)
            audio_clip = AudioFileClip(audio_path).with_start(start_time)
            audio_clips.append(audio_clip)
            start_time += audio_duration

        # Adiciona o áudio de fundo (backsong) para toda a duração do vídeo
        backsong = AudioFileClip(backsong_path).with_volume_scaled(0.4).subclipped(0, video.duration)

        # Combina o backsong com os áudios individuais
        final_audio = CompositeAudioClip([backsong] + audio_clips)

        # Define o áudio combinado no vídeo
        final_video = video.with_audio(final_audio)
        final_video.write_videofile(f"videos/{video_name}/output/{video_name}.mp4", codec="libx264", fps=30)

if __name__ == "__main__":
    editor = VideoEditor()
    video_name = "example_video"  # Nome do vídeo a ser editado
    editor.create_video(video_name)
    print(f"Vídeo '{video_name}' criado com sucesso!")