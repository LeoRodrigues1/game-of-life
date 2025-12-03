# 🦠 Jogo da Vida (Conway's Game of Life) — Simulação Distribuída e Paralela

Este projeto implementa a simulação do **Jogo da Vida** (Conway's Game of Life) em três arquiteturas de computação distintas (Sequencial, Paralela e Distribuída) com o objetivo de **comparar o desempenho** e analisar os custos de *overhead* de comunicação e sincronização.

## 🌟 O Problema: Autômatos Celulares e Paralelismo

O Jogo da Vida é um **Autômato Celular (AC)** clássico. Sua principal característica, a **localidade de dependência** (o estado futuro de uma célula depende apenas de seus 8 vizinhos), o torna um problema ideal para técnicas de paralelização e distribuição.

A simulação é executada em uma grade de **100x100** células por **200 gerações**.

### 📐 Vizinhança e Regras

O modelo utiliza a **Vizinhança de Moore** (as 8 células adjacentes) e evolui com base em quatro regras simples:

1.  **Solidão (Morte):** Célula viva com menos de 2 vizinhos vivos morre.
2.  **Sobrevivência:** Célula viva com 2 ou 3 vizinhos vivos permanece viva.
3.  **Superpopulação (Morte):** Célula viva com mais de 3 vizinhos vivos morre.
4.  **Reprodução (Nascimento):** Célula morta com exatamente 3 vizinhos vivos se torna viva.

## 🚀 Abordagens de Implementação

O projeto está dividido em três implementações principais, todas focadas em resolver o mesmo problema:

| Abordagem | Arquitetura | Tecnologia Chave | Objetivo |
| :--- | :--- | :--- | :--- |
| **Sequencial** | Processo Único (Baseline) | Python padrão | Estabelecer o tempo de referência (T_seq). |
| **Paralela** | Memória Compartilhada | Módulo `threading` | Otimizar o tempo de execução usando múltiplos núcleos da CPU. |
| **Distribuída** | Memória Distribuída (Cliente/Servidor) | Sockets TCP e `pickle` | Analisar o *overhead* de rede e a comunicação Cliente/Servidor. |

## 🛠️ Tempo de comparação final
- Tempo de execucao Sequencial: 8.7995 segundos
- Tempo de execucao Paralela (Threads): 9.0714 segundos
- Tempo de execucao Distribuida (1:1 Socket): 19.4781 segundos


Autor: Leonardo Rodrigues de Souza 2313189
