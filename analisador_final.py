import numpy as np
import pickle
import matplotlib.pyplot as plt
import os
import sys

# --- CONFIGURAÇÃO ---
GRID_FILE = "grade_distribuida_final.pickle" 
TEMPOS_FILE = "tempos_comparacao.txt"

# --- FUNÇÕES AUXILIARES ---

def carregar_tempos(nome_arquivo):
    """Carrega os tempos de execução do arquivo de texto."""
    tempos = {}
    try:
        with open(nome_arquivo, 'r') as f:
            linhas = f.readlines()
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo '{nome_arquivo}' não encontrado.")
        return None

    for linha in linhas:
        try:
            # Padrão: Tempo de execucao [ALGORITMO]: [VALOR] segundos
            partes = linha.split(':')
            if len(partes) > 2: # Lida com algoritmos que têm ":" no nome
                 algoritmo = ":".join(partes[:-1]).strip().replace("Tempo de execucao ", "")
            else:
                 algoritmo = partes[0].replace("Tempo de execucao ", "").strip()

            tempo_str = partes[-1].split('segundos')[0].strip()
            tempos[algoritmo] = float(tempo_str)
        except (ValueError, IndexError):
            # Ignora linhas que não seguem o padrão
            continue
            
    # Remove entradas duplicadas, mantendo apenas a última (mais recente)
    # Mas como o código só usa os valores finais, vamos checar a existência dos essenciais
    
    # Esta é a checagem crítica que falhava no seu script original:
    if 'Sequencial' not in tempos or 'Distribuida (1:1 Socket)' not in tempos:
        print("⚠️ AVISO: Não foram encontrados os tempos 'Sequencial' e 'Distribuida (1:1 Socket)' no arquivo.")
        print("Certifique-se de que todas as simulações foram executadas corretamente.")
        # Retornamos o dicionário parcial para que o gráfico seja gerado com o que tiver
    
    return tempos


def carregar_grade(nome_arquivo):
    """Carrega a grade final da simulação distribuída."""
    try:
        with open(nome_arquivo, 'rb') as f:
            grade = pickle.load(f)
        return grade
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo '{nome_arquivo}' (grade distribuída final) não encontrado. Rode o Servidor.")
        return None
    except Exception as e:
        print(f"❌ ERRO ao carregar grade pickle: {e}")
        return None

def gerar_imagem_grade(grade, titulo, nome_arquivo):
    """Gera e salva uma imagem PNG da grade."""
    if grade is None:
        return
        
    plt.figure(figsize=(10, 10))
    plt.imshow(grade, cmap='binary') 
    plt.title(titulo)
    plt.xticks([])
    plt.yticks([])
    plt.savefig(nome_arquivo)
    plt.close()
    print(f"IMAGEM SALVA: Verifique o arquivo '{nome_arquivo}'.")

def gerar_grafico_comparacao(tempos):
    """Gera um gráfico de barras comparando os tempos de execução."""
    if not tempos:
        print("❌ Não há dados de tempo suficientes para gerar o gráfico.")
        return

    # Filtra os tempos que serão comparados (apenas os encontrados)
    labels = []
    valores = []
    
    # Ordem de exibição no gráfico
    chaves_ordenadas = ['Sequencial', 'Paralela (Threads)', 'Distribuida (1:1 Socket)']
    
    for chave in chaves_ordenadas:
        if chave in tempos:
            labels.append(chave)
            valores.append(tempos[chave])
    
    if len(valores) < 2:
         print("❌ Pelo menos dois resultados de tempo são necessários para o gráfico de comparação.")
         return

    plt.figure(figsize=(12, 6))
    bars = plt.bar(labels, valores, color=['blue', 'green', 'orange'])
    
    plt.ylabel('Tempo de Execução (segundos)')
    plt.title('Comparação de Desempenho (Tempo Total)')
    
    # Adiciona os valores nas barras
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, f'{yval:.4f}s', ha='center', va='bottom')
        
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    nome_arquivo_grafico = 'comparacao_desempenho.png'
    plt.savefig(nome_arquivo_grafico)
    plt.close()
    print(f"GRÁFICO SALVO: Verifique o arquivo '{nome_arquivo_grafico}'.")


# --- FUNÇÃO PRINCIPAL ---
if __name__ == "__main__":
    
    # 1. Carregar Tempos
    tempos = carregar_tempos(TEMPOS_FILE)
    if tempos is None:
        sys.exit(1)

    print("\n--- Resultados de Tempo Carregados ---")
    for alg, tempo in tempos.items():
         print(f"Tempo de execucao {alg}: {tempo:.4f} segundos")
    print("--------------------------------------\n")


    # 2. Carregar e Visualizar Grade Distribuída Final
    grade_distribuida = carregar_grade(GRID_FILE)
    if grade_distribuida is not None:
        gerar_imagem_grade(
            grade_distribuida, 
            "Estado Final - Distribuída (1:1 Socket)", 
            'estado_final_jogo_da_vida_distribuida.png'
        )

    # 3. Gerar Gráfico de Comparação
    gerar_grafico_comparacao(tempos)

    print("\n[FIM] Análise concluída.")
