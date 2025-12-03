import numpy as np
import time
import socket
import pickle
import threading
import os
import sys

# --- PARÂMETROS GLOBAIS ---
TAMANHO_GRADE = 100 
NUM_GERACOES = 200 
HOST = '127.0.0.1' 
PORT = 65432
GRID_FILE = "grade_distribuida_final.pickle" # Arquivo para salvar o estado final


# --- FUNÇÕES BÁSICAS ---
def inicializar_grade(tamanho):
    """Cria o tabuleiro inicial aleatório."""
    return np.random.randint(0, 2, size=(tamanho, tamanho), dtype=np.int8)

def salvar_tempo_em_arquivo(algoritmo, tempo):
    """Salva o tempo de execução no arquivo 'tempos_comparacao.txt'."""
    nome_arquivo = "tempos_comparacao.txt"
    linha = f"Tempo de execucao {algoritmo}: {tempo:.4f} segundos\n"
    
    # Adiciona a nova linha, sem limpar o arquivo (para manter histórico)
    try:
        with open(nome_arquivo, 'a') as f:
            f.write(linha)
        print(f"\n[INFO] ✅ Tempo salvo em '{nome_arquivo}'")
    except Exception as e:
        print(f"❌ ERRO ao salvar o tempo: {e}")


# --- FUNÇÃO DE COMUNICAÇÃO (Worker Handler para 1 Cliente) ---
# A função foi simplificada e os prints de comunicação removidos/comentados.
def handle_client(conn, addr, grade_atual, nova_grade, tamanho):
    """Lida com a conexão do cliente, envia o trabalho e recebe o resultado."""
    # print(f"\n[SERVIDOR] Conexão estabelecida com o Cliente em {addr}") # Silenciado
    
    # 1. PREPARAR E ENVIAR DADOS: Envia a grade inteira, pois é 1:1
    dados_para_enviar = {
        'grade_fatia': grade_atual, 
        'tamanho': tamanho,
        # O cliente calculará a grade inteira (0 a tamanho)
        'linha_inicio': 0, 
        'linha_fim': tamanho
    }
    
    data = pickle.dumps(dados_para_enviar)
    
    # Envia o tamanho dos dados e depois os dados
    conn.sendall(len(data).to_bytes(8, byteorder='big')) 
    conn.sendall(data) 
    
    # 2. RECEBER RESULTADO (A grade completa calculada pelo cliente)
    tamanho_resposta_bytes = conn.recv(8)
    tamanho_resposta = int.from_bytes(tamanho_resposta_bytes, byteorder='big')
    
    dados_recebidos = b''
    while len(dados_recebidos) < tamanho_resposta:
        pacote = conn.recv(tamanho_resposta - len(dados_recebidos))
        if not pacote: break
        dados_recebidos += pacote
    
    nova_grade_completa = pickle.loads(dados_recebidos)
    
    # 3. MENSAGEM DE COMUNICAÇÃO MANUAL SOLICITADA - BLOCO REMOVIDO/SILENCIADO
    
    return nova_grade_completa


# --- FUNÇÃO PRINCIPAL DO SERVIDOR (Loop de Gerações) ---
def simular_jogo_da_vida_servidor(tamanho, num_geracoes):
    start_time = time.time()
    grade_atual = inicializar_grade(tamanho)
    
    print(f"\n--- Servidor: Início da Simulação Distribuída (1 Cliente, {num_geracoes} gerações) ---")
    
    # 1. Configuração do Socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        s.bind((HOST, PORT))
        
        # Loop principal das gerações
        for geracao in range(num_geracoes):
            # Mantém apenas o print de progresso
            #print(f"Servidor: Geração {geracao + 1}/{num_geracoes}. Aguardando Cliente...")
            s.listen(1) # Espera 1 cliente
            
            # BLOQUEIA AQUI: Espera pela conexão do Cliente.
            conn, addr = s.accept() 
            
            # Cria a nova grade de destino
            nova_grade = np.zeros((tamanho, tamanho), dtype=np.int8)
            
            # Lida com a comunicação e obtém o resultado da nova geração
            grade_atual = handle_client(conn, addr, grade_atual, nova_grade, tamanho)
            
            conn.close() # Fecha a conexão após cada geração

    end_time = time.time()
    tempo_total = end_time - start_time
    
    # 2. Salva o tempo e a grade final
    salvar_tempo_em_arquivo("Distribuida (1:1 Socket)", tempo_total)
    
    with open(GRID_FILE, 'wb') as f:
        pickle.dump(grade_atual, f)
        
    print(f"\n[FIM] Servidor: Simulação concluída. Tempo: {tempo_total:.4f}s.")
    print(f"[FIM] Grade final salva em '{GRID_FILE}'. Execute o 'analisador_final.py'.")


if __name__ == "__main__":
    if os.path.exists(GRID_FILE):
        os.remove(GRID_FILE)
    
    # Garante que o arquivo de tempo exista para o analisador
    if not os.path.exists("tempos_comparacao.txt"):
        with open("tempos_comparacao.txt", 'w') as f:
            f.write("")
            
    simular_jogo_da_vida_servidor(TAMANHO_GRADE, NUM_GERACOES)
