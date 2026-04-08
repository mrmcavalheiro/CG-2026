# Fundamentos - Roteiro Teorico

## 1) Seno e Cosseno
Objetivo:
- Entender o circulo unitario e a relacao entre angulo e coordenadas.

Conceitos chave:
- Circulo unitario: raio 1, centro na origem.
- Coordenadas parametricas: x = cos(t), y = sen(t).
- Periodicidade: funcoes se repetem a cada 2*pi.

Formula base:
- sen^2(t) + cos^2(t) = 1

Aplicacoes:
- Movimento circular.
- Oscilacao (onda).
- Rotacao de pontos em 2D.

## 2) Circulo com sen/cos
Objetivo:
- Construir um circulo por amostragem angular.

Construcao:
- Para N pontos: t_i = 2*pi*i/N
- x_i = cx + R*cos(t_i)
- y_i = cy + R*sen(t_i)

Observacoes praticas:
- Quanto maior N, mais suave a curva.
- Em tela, o eixo Y cresce para baixo (ajustar sinal quando necessario).

Exercicio sugerido:
- Renderizar circulo e elipse alterando R_x e R_y.
