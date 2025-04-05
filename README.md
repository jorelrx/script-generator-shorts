# Projeto Short Youtube

Este projeto é um editor de vídeo simples que permite criar vídeos a partir de imagens e arquivos de áudio. Abaixo está a estrutura do projeto e instruções sobre como utilizá-lo.

## Estrutura do Projeto

```
Projeto Short Youtube
├── videos
│   └── example_video
│       ├── input
│       │   ├── images
│       │   └── audios
│       └── output
│           ├── output.mp4
│           └── final_output.mp4
├── video_editor.py
└── README.md
```

### Descrição dos Diretórios e Arquivos

- **videos/example_video/input/images**: Este diretório contém os arquivos de imagem que serão usados para criar o vídeo.
  
- **videos/example_video/input/audios**: Este diretório contém os arquivos de áudio que serão usados para o vídeo.

- **videos/example_video/output/output.mp4**: Este arquivo é o vídeo inicial gerado pelo editor de vídeo, que contém apenas as imagens.

- **videos/example_video/output/final_output.mp4**: Este arquivo é o vídeo final que inclui as faixas de áudio.

- **video_editor.py**: Este arquivo contém a classe `VideoEditor`, que é responsável por criar vídeos a partir de imagens e arquivos de áudio. Inclui métodos para obter a duração do áudio, criar vídeos e adicionar áudio ao vídeo final.

## Como Usar

1. Coloque suas imagens no diretório `videos/example_video/input/images`.
2. Coloque seus arquivos de áudio no diretório `videos/example_video/input/audios`.
3. Execute o script `video_editor.py` para gerar o vídeo.
4. O vídeo inicial será salvo em `videos/example_video/output/output.mp4`.
5. O vídeo final, com áudio, será salvo em `videos/example_video/output/final_output.mp4`.

Sinta-se à vontade para modificar o código e adaptar o projeto às suas necessidades!
