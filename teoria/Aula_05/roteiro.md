# Aula 05 - Roteiro Teorico

## 1) Animacao de Braco Robotico em 2D
Objetivo:
- Aplicar hierarquia de transformacoes em segmentos articulados.

Conceitos:
- Cinematica direta em cadeia (base -> elo 1 -> elo 2).
- Rotacoes locais acumuladas.
- Uso de push/pop de matriz (ou composicao matricial equivalente).

## 2) Relogio Analogico
Objetivo:
- Converter tempo em angulos e desenhar ponteiros com trigonometria.

Formulas:
- ang_seg = 2*pi*(seg/60)
- ang_min = 2*pi*((min + seg/60)/60)
- ang_hora = 2*pi*((hora + min/60)/12)

## 3) Exemplo Python
Objetivo:
- Fixar organizacao de codigo para demos graficas.

Boas praticas:
- Separar entrada, update e render.
- Isolar funcoes matematicas.
- Evitar logica de negocio dentro de draw.

## 4) Aspectos Matematicos
Topicos recomendados:
- Vetores 2D e 3D.
- Produto escalar (angulo/projecao).
- Sistemas de coordenadas (mundo, camera, tela).
- Matrizes de projecao ortogonal e perspectiva.

Ligacao com os exemplos da aula:
- Window-Viewport
- Proj. Ortogonal
- Proj. Perspectiva
- Clipping
