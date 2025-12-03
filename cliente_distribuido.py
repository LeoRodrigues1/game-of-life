import time
import numpy as np
import socket
import pickle
import sys 

# --- PARÂMETROS GLOBAIS ---
HOST = '127.0.0.1' 
PORT = 65432
TAMANHO_GRADE = 100 


# --- FUNÇÃO ESSENCIAL: CONTAGEM DE VIZINHOS ---
def contar_vizinhos_vivos(grade, i, j, tamanho):
    """Conta os 8 vizinhos vivos de uma célula (i, j) na grade completa."""
    vizinhos_vivos = 0
    
    # O cliente está recebendo a grade completa, então a lógica é a mesma do sequencial
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x == 0 and y == 0:
                continue
            
            vizinho_i = i + x 
            vizinho_j = j + y
            
            # Condição de borda (Toroidal ou Borda Fixa, dependendo da sua preferência)
            # Para simplificar, vamos usar borda fixa (não olha para fora)
            if 0 <= vizinho_i < tamanho and 0 <= vizinho_j < tamanho:
                vizinhos_vivos += grade[vizinho_i, vizinho_j]

    return vizinhos_vivos


# --- FUNÇÃO CHAVE: LÓGICA DO JOGO DA VIDA ---
def calcular_proxima_geracao(grade_atual, tamanho):
    """Calcula o novo estado para a grade completa recebida."""
    nova_grade = np.zeros((tamanho, tamanho), dtype=np.int8)
    
    for i in range(tamanho):
        for j in range(tamanho):
            
            vivos = contar_vizinhos_vivos(grade_atual, i, j, tamanho) 
            
            # Aplica as 4 regras
            if grade_atual[i, j] == 1: 
                if vivos == 2 or vivos == 3:
                    nova_grade[i, j] = 1 
            else: 
                if vivos == 3:
                    nova_grade[i, j] = 1 
                    
    return nova_grade


# --- FUNÇÃO PRINCIPAL DO CLIENTE (Worker) ---
def cliente_worker(host, port):
    try:
        # 1. TENTA CONECTAR
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            print(f"[CLIENTE] Conectado ao Servidor. Aguardando trabalho...")
            
            # 2. RECEBER DADOS
            tamanho_dados_bytes = s.recv(8)
            if not tamanho_dados_bytes: return

            tamanho_dados = int.from_bytes(tamanho_dados_bytes, byteorder='big')
            
            dados_recebidos = b''
            while len(dados_recebidos) < tamanho_dados:
                pacote = s.recv(tamanho_dados - len(dados_recebidos))
                if not pacote: break
                dados_recebidos += pacote
            
            dados = pickle.loads(dados_recebidos)
            grade_fatia = dados['grade_fatia'] # Recebe a grade inteira
            tamanho = dados['tamanho']
            
            print(f"[CLIENTE] Recebeu {len(dados_recebidos) / 1024:.2f} KB. Calculando...")
            
            # 3. CALCULAR O TRABALHO
            nova_fatia = calcular_proxima_geracao(grade_fatia, tamanho)
            
            # 4. ENVIAR RESULTADO
            data_resposta = pickle.dumps(nova_fatia)
            s.sendall(len(data_resposta).to_bytes(8, byteorder='big'))
            s.sendall(data_resposta)
            
            print(f"[CLIENTE] Envio concluído. Desconectando...")
            
    except ConnectionRefusedError:
        print(f"[CLIENTE] ERRO: Servidor não está ativo ou porta incorreta.", file=sys.stderr)
    except Exception as e:
        print(f"[CLIENTE] ERRO durante a execução: {e}", file=sys.stderr)
        
if __name__ == "__main__":
    # O cliente rodará em loop AUTOMATICAMENTE, reconectando a cada geração.
    print("[CLIENTE] MODO AUTOMÁTICO ATIVADO. Aguardando o Servidor iniciar a Geração 1...")
    while True:
        cliente_worker(HOST, PORT)
        # se o servidor ainda não estiver ouvindo a próxima porta.
        time.sleep(0.1)
