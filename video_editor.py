import os
import cv2
import speech_recognition as sr
import whisper
from moviepy import VideoFileClip, CompositeVideoClip, ImageClip, AudioFileClip, CompositeAudioClip, TextClip
from moviepy import vfx, afx
from mutagen.mp3 import MP3

class VideoEditor:
    def __init__(self, output_path: str = "output.mp4"):
        self.output_path = output_path

    def get_audio_duration(self, audio_path: str) -> float:
        """ Retorna a duração do áudio em segundos """
        audio = MP3(audio_path)
        return audio.info.length

    def create_video(self, video_name: str, video_type: str, fps: int = 30):
        """
        Cria um vídeo com base em imagens e áudios encontrados nos diretórios especificados.
        Adiciona um áudio de fundo, transições entre os vídeos gerados e legendas.

        :param video_name: Nome do vídeo (usado para localizar os arquivos)
        :param fps: Frames por segundo do vídeo
        """
        base_dir = f"videos/{video_type}/{video_name}"
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
        # Cria a pasta para salvar os vídeos gerados, se não existir
        video_output_dir = f"{base_dir}/input/"
        os.makedirs(f"{video_output_dir}/video", exist_ok=True)

        for img_path, audio_path in zip(img_paths, audio_paths):
            audio_duration = self.get_audio_duration(audio_path)
            img = cv2.imread(img_path)

            # Ajusta a imagem para o formato vertical (9:16) do YouTube Shorts
            target_width = 1080
            target_height = 1920
            img = cv2.resize(img, (target_width, target_height))

            # Cria um vídeo para a imagem com a duração do áudio
            clip_name = img_path.split('/')[-1].rsplit('.', 1)[0] + ".mp4"
            clip_name = clip_name.replace("image", "video")
            video_path = os.path.join(video_output_dir, clip_name)
            print(f"Gerando vídeo: {video_path}")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(video_path, fourcc, fps, (target_width, target_height))

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
        self.add_audio(audio_paths, backsong_path, combined_video, video_name, video_type)

        # Gera legendas automaticamente
        subtitles = self.generate_subtitles(f"videos/{video_type}/{video_name}/output/{video_name}.mp4")

        # Adiciona legendas ao vídeo final
        self.add_subtitles(
            video_path=f"videos/{video_type}/{video_name}/output/{video_name}.mp4",
            subtitles=subtitles,
            output_path=f"videos/{video_type}/{video_name}/output/{video_name}_with_subtitles.mp4"
        )

        print(f"Vídeo com legendas salvo em 'videos/{video_name}/output/{video_name}_with_subtitles.mp4'")

    def add_audio(self, audio_paths: list[str], backsong_path: str, video: CompositeVideoClip, video_name: str, video_type: str):
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

        # Define o áudio combinado no vídeo
        if video_type == "motivacional":
            # Adiciona o áudio de fundo (backsong) para toda a duração do vídeo
            backsong = AudioFileClip(backsong_path).with_volume_scaled(0.4).subclipped(0, video.duration)

            # Combina o backsong com os áudios individuais
            final_audio = CompositeAudioClip([backsong] + audio_clips)
            final_video = video.with_audio(final_audio)
        elif video_type == "infantil":
            final_audio = CompositeAudioClip(audio_clips)
            final_video = video.with_audio(final_audio)
            
        # Cria o diretório de saída, se não existir
        output_dir = os.path.dirname(f"videos/{video_type}/{video_name}/output/")
        os.makedirs(output_dir, exist_ok=True)
        final_video.write_videofile(f"videos/{video_type}/{video_name}/output/{video_name}.mp4", codec="libx264", fps=30)

    def add_subtitles(self, video_path: str, subtitles: list[tuple[str, float, float]], output_path: str = None):
        """
        Adiciona legendas a um vídeo existente.

        :param video_path: Caminho do vídeo ao qual as legendas serão adicionadas.
        :param subtitles: Lista de tuplas contendo o texto da legenda, o tempo de início e o tempo de fim.
                          Exemplo: [("Legenda 1", 0, 5), ("Legenda 2", 6, 10)]
        :param output_path: Caminho de saída para o vídeo com legendas. Se não fornecido, sobrescreve o vídeo original.
        """
        video = VideoFileClip(video_path)
        subtitle_clips = []

        for text, start, end in subtitles:
            subtitle = (TextClip(
                    font="./assets/OpenSans.ttf", 
                    text=text, 
                    size=(864, None), 
                    font_size=48, 
                    color='#fff',
                    method='caption',
                    margin=(0, 10),
                    horizontal_align='center',
                    vertical_align='center')
                .with_position(lambda t: ('center', 1536+t))
                .with_start(start)
                .with_duration(end - start))
            subtitle_clips.append(subtitle)

        # Combina o vídeo original com as legendas
        final_video = CompositeVideoClip([video] + subtitle_clips)

        # Define o caminho de saída
        output_path = output_path or video_path
        final_video.write_videofile(output_path, codec="libx264", fps=30)

    def generate_subtitles(self, video_path: str, max_words: int = 3, output_path: str = None) -> list[tuple[str, float, float]]:
        """
        Gera legendas automaticamente a partir do áudio de um vídeo usando OpenAI Whisper,
        com limite de palavras por segmento e usando word_timestamps para precisão.

        :param video_path: Caminho do vídeo.
        :param max_words: Número máximo de palavras por segmento.
        :param output_path: Caminho para salvar o arquivo de legendas (opcional).
        :return: Lista de tuplas (texto, start_time, end_time).
        """
        # Extrai o áudio do vídeo
        audio_path = "temp_audio.wav"
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, logger=None)

        # Carrega o modelo
        model = whisper.load_model("base") # Use "tiny", "base", "small", "medium", ou "large"

        # Transcrição com timestamps por palavra
        result = model.transcribe(audio_path, word_timestamps=True, language="pt", task="transcribe", fp16=False)

        subtitles = []

        for segment in result["segments"]:
            words = segment.get("words", [])
            for i in range(0, len(words), max_words):
                group = words[i:i + max_words]

                if not group:
                    continue

                start = group[0]["start"]
                end = group[-1]["end"]
                text = " ".join([w["word"].strip() for w in group])
                print(f"Texto: {text}, Início: {start:.2f}, Fim: {end:.2f}")

                subtitles.append((text, start, end))

        # Salvar como arquivo simples de legendas (SRT-like)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                for idx, (text, start, end) in enumerate(subtitles, 1):
                    f.write(f"{idx}\n")
                    f.write(f"{self.format_time(start)} --> {self.format_time(end)}\n")
                    f.write(f"{text}\n\n")

        os.remove(audio_path)
        return subtitles

    def format_time(self, seconds: float) -> str:
        """Converte segundos para formato SRT hh:mm:ss,ms"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

if __name__ == "__main__":
    editor = VideoEditor()
    video_name = "liberte_se"
    editor.create_video(video_name, "motivacional")
    print(f"Vídeo '{video_name}' criado com sucesso!")