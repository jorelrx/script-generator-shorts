## `TextClip` – `moviepy.video.VideoClip`

Cria um `ImageClip` com texto gerado via script. Ideal para sobrepor legendas ou títulos em vídeos.

### Exemplo de uso
```python
from moviepy.editor import TextClip

clip = TextClip(
    text="Hello, world!",
    font="Arial",
    font_size=50,
    color="white",
    bg_color="black",
    duration=5
)
```

### Parâmetros principais

- **`text`**: Texto a ser exibido (ou use `filename` para ler de arquivo).
- **`font`**: Caminho ou nome da fonte (formato OpenType).
- **`font_size`**: Tamanho da fonte em pontos.
- **`size`**: Tamanho do quadro (largura, altura). Necessário se `method='caption'`.
- **`margin`**: Margem ao redor do texto. Ex: `(10, 20)` ou `(10, 5, 10, 5)`.
- **`color`**: Cor do texto. Pode ser nome, RGB, RGBA ou hexadecimal.
- **`bg_color`**: Cor de fundo. `None` para fundo transparente.
- **`stroke_color` / `stroke_width`**: Contorno do texto e espessura.
- **`method`**:
  - `'label'` *(default)*: Tamanho automático baseado no texto.
  - `'caption'`: Quadro com tamanho fixo e texto ajustado.
- **`text_align`**: Alinhamento do texto: `left`, `center`, `right`.
- **`horizontal_align` / `vertical_align`**: Alinhamento do bloco de texto no quadro.
- **`interline`**: Espaçamento entre linhas.
- **`transparent`**: Ativa transparência. Default: `True`.
- **`duration`**: Duração do clipe de texto.

### Observações

- O tamanho final pode ser maior que o necessário por conta de caracteres com *ascent* (acentos) ou *descent* (ex: "g", "p", "y").
- Para controlar melhor o layout, ajuste `margin`, `size`, `aligns` e `interline`.