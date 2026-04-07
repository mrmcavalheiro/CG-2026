# CG-2026

Projeto da disciplina de Computacao Grafica (UNIJUI) para demonstracao de exemplos de computacao grafica em Python.

## Preview do programa

![Preview do programa](assets/preview.gif)

Se preferir imagem estatica, use `assets/preview.png` e troque a extensao no link acima.

## Requisitos
- Python 3.10+
- Pygame
- NumPy

Instalacao das dependencias:
```bash
pip install pygame numpy
```

## Como executar
Na raiz do projeto (`Exemplos`):

```bash
python main.py
```

## Estrutura do projeto
- `main.py`: ponto de entrada da aplicacao e interface principal.
- `config.py`: configuracoes globais (layout, temas, cores e resolucoes).
- `exemplos/`: implementacoes dos exemplos de aula.
- `input/`: manipulacao de entrada de teclado/mouse.
- `interface/`: componentes visuais auxiliares.
- `teoria/`: materiais de apoio teorico.
- `assets/`: imagens e GIFs usados no README.

## Observacoes
- O projeto inicia com tema `UNIJUI` por padrao.
- A janela e redimensionavel e o layout e recalculado automaticamente.

## Git
Fluxo basico para salvar alteracoes:

```bash
git add .
git commit -m "Atualiza projeto"
git push
```

