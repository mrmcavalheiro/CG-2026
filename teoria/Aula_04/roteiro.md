# Aula 04 - Roteiro Teorico

## 1) Material de apoio (Transformacoes 2D)
Objetivo:
- Consolidar translacao, escala, rotacao e cisalhamento.

Resumo:
- Translacao: move o objeto sem deformar.
- Escala: aumenta/reduz (uniforme ou nao uniforme).
- Rotacao: gira em torno da origem ou ponto arbitrario.
- Cisalhamento: inclina o objeto (efeito de deformacao angular).

Matriz homogenea 3x3:
- Permite combinar transformacoes em uma unica multiplicacao.

## 2) Curvas de Bezier
Objetivo:
- Entender interpolacao por pontos de controle.

Bezier Quadratica:
- B(t) = (1-t)^2 P0 + 2(1-t)t P1 + t^2 P2

Bezier Cubica:
- B(t) = (1-t)^3 P0 + 3(1-t)^2 t P1 + 3(1-t)t^2 P2 + t^3 P3

Conceitos:
- P0 e Pn: pontos finais.
- P1..Pn-1: pontos de controle (direcao e curvatura).
- t em [0,1].

## 3) OpenGL introdutorio
Objetivo:
- Relacionar pipeline grafico com os exemplos OpenGL da aula.

Topicos:
- Buffer de cor e profundidade.
- Primitivos (triangulos, quads, linhas).
- Camera e projecao.
- Transformacoes de modelo (translate, rotate, scale).
