import numpy as np
import time
import matplotlib.pyplot as plt # Importa a biblioteca para gerar imagens
from matplotlib.colors import ListedColormap
import os

# --- PARÂMETROS GLOBAIS DA SIMULAÇÃO ---
TAMANHO_GRADE = 100 # matriz(100x100)
NUM_GERACOES = 200  # Número de iterações
NOME_ARQUIVO_IMAGEM = "estado_final_jogo_da_vida_sequencial.png"


# FUNÇÃO 1: INICIALIZAÇÃO 
def inicializar_grade(tamanho):
    """
    Prepara o tabuleiro inicial (matriz).
    Células 'vivas' são 1, 'mortas' são 0.
    """
    # Cria uma matriz de 'tamanho x tamanho' preenchida aleatoriamente com 0s e 1s.
    # Isso garante um ponto de partida dinâmico para a simulação.
    grade = np.random.randint(0, 2, size=(tamanho, tamanho), dtype=np.int8)
    return grade

#  FUNÇÃO 2: CONTAGEM DE VIZINHOS
def contar_vizinhos_vivos(grade, i, j, tamanho):
    """
    Conta quantos dos 8 vizinhos (Vizinhança de Moore) da célula (i, j) estão vivos.
    """
    vizinhos_vivos = 0
    
    # Vamos 'varrer' ao redor da célula, variando as coordenadas x e y de -1 a 1.
    for x in range(-1, 2):
        for y in range(-1, 2):
            # Ignora o centro, pois estamos contando apenas os vizinhos!
            if x == 0 and y == 0:
                continue
 
            vizinho_i = i + x # Coordenada da linha do vizinho
            vizinho_j = j + y # Coordenada da coluna do vizinho
 
            # REGRA DE BORDA: Verifica se as coordenadas do vizinho estão DENTRO do tabuleiro.
            # Se estiverem fora, consideramos o vizinho como 'morto' (0) implicitamente.
            if 0 <= vizinho_i < tamanho and 0 <= vizinho_j < tamanho:
                vizinhos_vivos += grade[vizinho_i, vizinho_j]

    return vizinhos_vivos

#  FUNÇÃO 3: CÁLCULO DA NOVA GERAÇÃO
def proxima_geracao(grade_atual, tamanho):
    """
    Calcula o estado do tabuleiro no próximo instante de tempo (próxima iteração).
    """
    # Cria um novo tabuleiro (nova_grade), começando do zero (todo morto).
    # A nova grade deve ser calculada toda baseada apenas na grade_atual.
    nova_grade = np.zeros((tamanho, tamanho), dtype=np.int8)

    # Itera por CADA CÉLULA do tabuleiro
    for i in range(tamanho):
        for j in range(tamanho):
            
            vivos = contar_vizinhos_vivos(grade_atual, i, j, tamanho)
 
            # APLICAÇÃO DAS 4 REGRAS DO JOGO DA VIDA

            if grade_atual[i, j] == 1: # Célula VIVA
                if vivos < 2:
                    # REGRA 1: Solidão -> MORRE (nova_grade já é 0)
                    pass 
                elif vivos == 2 or vivos == 3:
                    # REGRA 2: Sobrevivência -> CONTINUA VIVA
                    nova_grade[i, j] = 1
                else: # vivos > 3
                    # REGRA 3: Superpopulação -> MORRE (nova_grade já é 0)
                    pass 

            else: # Célula MORTA (grade_atual[i, j] == 0)
                if vivos == 3:
                    # REGRA 4: Reprodução -> REVIVE
                    nova_grade[i, j] = 1
 
    return nova_grade

#  FUNÇÃO 4: VISUALIZAÇÃO
def salvar_grade_como_imagem(grade, nome_arquivo):
    """Converte o estado final da grade em uma imagem PNG customizada (Preto/Branco)."""
    
    # Define as cores: Preto (Morto, 0) e Branco (Vivo, 1)
    cores = ['black', 'white'] 
    cmap_personalizado = ListedColormap(cores)
    
    plt.imshow(grade, cmap=cmap_personalizado, interpolation='none')
    plt.axis('on') 
    plt.savefig(nome_arquivo, bbox_inches='tight', pad_inches=0)
    plt.close()

#   FUNÇÃO 5 PARA SALVAR O TEMPO EM ARQUIVO
def salvar_tempo_em_arquivo(algoritmo, tempo):
    """
    Salva o tempo de execução em um arquivo de texto 'tempos_comparacao.txt'.
    Adiciona a nova linha ao final do arquivo.
    """
    nome_arquivo = "tempos_comparacao.txt"
    linha = f"Tempo de execucao {algoritmo}: {tempo:.4f} segundos\n"
    
    try:
        with open(nome_arquivo, 'a') as f:
            f.write(linha)
        print(f"✅ Tempo salvo em '{nome_arquivo}'")
    except Exception as e:
        print(f"❌ ERRO ao salvar o tempo: {e}")

#  FUNÇÃO 6: EXECUÇÃO PRINCIPAL
def simular_jogo_da_vida_sequencial(tamanho, num_geracoes):
    """
    Controla o fluxo da simulação e registra o tempo.
    """
    start_time = time.time() # Inicia o cronômetro

    grade_atual = inicializar_grade(tamanho)

    print(f"--- Início da Simulação Sequencial ({tamanho}x{tamanho}, {num_geracoes} gerações) ---")

    # Loop principal das gerações
    for geracao in range(num_geracoes):
        grade_atual = proxima_geracao(grade_atual, tamanho)

    end_time = time.time() # Para o cronômetro
    tempo_total = end_time - start_time
    
    # Salva o tempo no arquivo de comparação
    salvar_tempo_em_arquivo("Sequencial", tempo_total)

    # Gera a visualização
    salvar_grade_como_imagem(grade_atual, NOME_ARQUIVO_IMAGEM)

    # Exibe os resultados
    print(f"\n--- Fim da Simulação ---")
    print(f"Tempo total de execucao sequencial: {tempo_total:.4f} segundos")
    print(f"Células vivas restantes: {np.sum(grade_atual)}")
    print(f"IMAGEM SALVA: Verifique o arquivo '{NOME_ARQUIVO_IMAGEM}'.")

    return tempo_total

if __name__ == "__main__":
    if os.path.exists("tempos_comparacao.txt"):
        print("\nArquivo de tempos limpo para novo teste.")

    simular_jogo_da_vida_sequencial(TAMANHO_GRADE, NUM_GERACOES)
