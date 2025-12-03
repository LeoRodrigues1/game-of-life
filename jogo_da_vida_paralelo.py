import numpy as np
import time
import matplotlib.pyplot as plt 
from matplotlib.colors import ListedColormap
import threading # Módulo essencial para paralelismo com threads
import os        # Para descobrir o número de CPUs e manipular arquivos

# --- PARÂMETROS GLOBAIS DA SIMULAÇÃO ---
TAMANHO_GRADE = 100 
NUM_GERACOES = 200 
NOME_ARQUIVO_IMAGEM = "estado_final_jogo_da_vida_paralelo.png"

# Configuração do Paralelismo
# Determina o número de threads com base nos núcleos lógicos da CPU
NUM_THREADS = os.cpu_count() or 4 
print(f"Utilizando {NUM_THREADS} threads para paralelização.")


# FUNÇÃO 1: INICIALIZAÇÃO 
def inicializar_grade(tamanho):
    """Cria o tabuleiro inicial aleatório."""
    return np.random.randint(0, 2, size=(tamanho, tamanho), dtype=np.int8)

#  FUNÇÃO 2: CONTAGEM DE VIZINHOS
def contar_vizinhos_vivos(grade, i, j, tamanho):
    """Conta os 8 vizinhos vivos de uma célula (i, j)."""
    vizinhos_vivos = 0
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x == 0 and y == 0:
                continue
            vizinho_i = i + x
            vizinho_j = j + y
            if 0 <= vizinho_i < tamanho and 0 <= vizinho_j < tamanho:
                vizinhos_vivos += grade[vizinho_i, vizinho_j]
    return vizinhos_vivos

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

#  FUNÇÃO PARA SALVAR O TEMPO EM ARQUIVO
def salvar_tempo_em_arquivo(algoritmo, tempo):
    """Salva o tempo de execução no arquivo 'tempos_comparacao.txt'."""
    nome_arquivo = "tempos_comparacao.txt"
    linha = f"Tempo de execucao {algoritmo}: {tempo:.4f} segundos\n"
    
    try:
        with open(nome_arquivo, 'a') as f:
            f.write(linha)
        print(f"✅ Tempo salvo em '{nome_arquivo}'")
    except Exception as e:
        print(f"❌ ERRO ao salvar o tempo: {e}")


# --- FUNÇÃO CHAVE DO PARALELISMO (O TRABALHADOR) ---
def worker_calcular_linhas(grade_atual, nova_grade, tamanho, linha_inicio, linha_fim):
    """
    Função executada por cada thread. Calcula o novo estado para um intervalo de linhas.
    """
    # Itera apenas sobre as linhas que são responsabilidade desta thread
    for i in range(linha_inicio, linha_fim):
        for j in range(tamanho):
            
            # 1. Leitura: Conta vizinhos na grade ATUAL (imutável)
            vivos = contar_vizinhos_vivos(grade_atual, i, j, tamanho)
            
            # 2. Escrita: Aplica as regras na NOVA GRADE (área exclusiva da thread)
            if grade_atual[i, j] == 1: # VIVA
                if vivos == 2 or vivos == 3:
                    nova_grade[i, j] = 1 # Sobrevive
            else: # MORTA
                if vivos == 3:
                    nova_grade[i, j] = 1 # Reprodução
                    
    # Não há retorno, pois a thread modifica a matriz nova_grade diretamente.
    # Como as threads trabalham em fatias diferentes, não há conflito de escrita (Race Condition).


# --- FUNÇÃO DE COORDENAÇÃO (SUBSTITUI proxima_geracao) ---
def proxima_geracao_paralela(grade_atual, tamanho, num_threads):
    """
    Coordena a criação e sincronização das threads para calcular a próxima geração.
    """
    # Cria a nova grade de destino
    nova_grade = np.zeros((tamanho, tamanho), dtype=np.int8)
    threads = []
    
    # 1. Divisão do Trabalho
    linhas_por_thread = tamanho // num_threads  #Se a grade é 100x100 e num_threads é 4, cada fatia terá 25 linhas.

    # 2. Criação e Início das Threads
    for k in range(num_threads):
        linha_inicio = k * linhas_por_thread
        
        # O último thread pega o restante das linhas para garantir que tudo seja processado.
        if k == num_threads - 1:
            linha_fim = tamanho 
        else:
            linha_fim = linha_inicio + linhas_por_thread
            
        # Cria a thread e atribui a função worker e seus argumentos (o intervalo de linhas)
        thread = threading.Thread(
            target=worker_calcular_linhas, 
            args=(grade_atual, nova_grade, tamanho, linha_inicio, linha_fim)
        )
        threads.append(thread)
        thread.start() # Inicia a execução em paralelo
        
    # 3. Sincronização (Join)
    # O programa principal PAUSA aqui até que TODAS as threads terminem o seu trabalho.
    for thread in threads:
        thread.join() 
        
    return nova_grade


# --- FUNÇÃO PRINCIPAL DE SIMULAÇÃO ---

def simular_jogo_da_vida_paralelo(tamanho, num_geracoes, num_threads):
    """
    Controla o fluxo da simulação paralela e mede o tempo.
    """
    start_time = time.time()
    
    grade_atual = inicializar_grade(tamanho)
    
    print(f"--- Início da Simulação Paralela ({tamanho}x{tamanho}, {num_geracoes} gerações, {num_threads} threads) ---")
    
    # Loop principal das gerações, usando a função PARALELA
    for geracao in range(num_geracoes):
        grade_atual = proxima_geracao_paralela(grade_atual, tamanho, num_threads)
        
    end_time = time.time()
    tempo_total = end_time - start_time
    
    # Salva o tempo no arquivo de comparação
    salvar_tempo_em_arquivo("Paralela (Threads)", tempo_total)
    
    # Gera a visualização
    salvar_grade_como_imagem(grade_atual, NOME_ARQUIVO_IMAGEM)
    
    # 📊 Exibe os resultados e o tempo
    print(f"\n--- Fim da Simulação ---")
    print(f"Tempo total de execução PARALELA: {tempo_total:.4f} segundos")
    print(f"Células vivas restantes: {np.sum(grade_atual)}")
    print(f"IMAGEM SALVA: Verifique o arquivo '{NOME_ARQUIVO_IMAGEM}' na pasta do projeto.")
    
    return tempo_total

if __name__ == "__main__":
    # Remove a linha que limpa o arquivo para que possamos COMPARAR os tempos!
    simular_jogo_da_vida_paralelo(TAMANHO_GRADE, NUM_GERACOES, NUM_THREADS)
