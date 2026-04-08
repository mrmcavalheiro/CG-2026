# Aula 06 - Roteiro Teorico

## 1) Rotacao de Objetos
Objetivo:
- Expandir rotacao para 3D e eixos locais.

Conceitos:
- Rotacao em torno de X, Y, Z.
- Ordem das rotacoes importa (nao comutativa).
- Gimbal lock (introducao conceitual).

## 2) Exemplos Temporarios
Objetivo:
- Reservar espaco para experimentos de sala.

Sugestoes de mini-demos:
- Orbit camera simples.
- Rotacao automatica com velocidade angular.
- Comparacao entre Euler e matriz acumulada.

## 3) Camera Virtual e Perspectiva
Objetivo:
- Entender pipeline de visualizacao.

Topicos:
- View matrix (camera).
- Projection matrix (FOV, aspect, near, far).
- Conversoes de espaco: mundo -> camera -> clip -> NDC -> tela.

Formula-chave (perspectiva simplificada):
- x_proj = f * x / z
- y_proj = f * y / z

Observacao:
- Esta aula fica pronta para evoluir para Objetos 3D (Aula 08).
