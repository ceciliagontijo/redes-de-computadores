import socket
from datetime import datetime
import threading
import psutil
import time

monitor_ligado = {"cpu": False, "memoria": False} #variáveis compartilhadas entre as threads

lock_envio = threading.Lock() #criação do mutex (pra gerar uma seção crítica)

def enviar(conexao, texto):
    lock_envio.acquire() 
    conexao.send(texto.encode())
    lock_envio.release()

def thread_cpu(conexao, intervalo):
    while monitor_ligado["cpu"]:
        uso = psutil.cpu_percent(interval=1)
        enviar(conexao, f"[CPU] uso atual: {uso}%\n")
        time.sleep(intervalo)
    print("Thread de CPU finalizada.")

def thread_memoria(conexao, intervalo):
    while monitor_ligado["memoria"]:
        uso = psutil.virtual_memory().percent
        enviar(conexao, f"[MEMORIA] uso atual: {uso}%\n")
        time.sleep(intervalo)

    print("Thread de MEMORIA finalizada")

def thread_leitura(conexao): # loop infinito pra monitorar oq o cliente esta digitando
    while True:
        dados = conexao.recv(1024).decode()  
        if not dados:
            print("Cliente desconectou")
            break
 
        comando = dados.strip()
        print(f"Comando recebido: {comando!r}")
 
        if comando == "exit":
            monitor_ligado["cpu"] = False
            monitor_ligado["memoria"] = False
            break
 
        elif comando == "quit-cpu":
            monitor_ligado["cpu"] = False
            enviar(conexao, "Monitor de CPU interrompido.\n")
 
        elif comando == "quit-memoria":
            monitor_ligado["memoria"] = False
            enviar(conexao, "Monitor de memoria interrompido.\n")

        elif comando.startswith("cpu-"):
            intervalo = int(comando.split("-")[1])
            if not monitor_ligado["cpu"]:
                monitor_ligado["cpu"] = True
                t = threading.Thread(target=thread_cpu, args=(conexao, intervalo))
                t.daemon = True
                t.start()
            enviar(conexao, f"Monitor de CPU iniciado a cada {intervalo}s.\n")  

        elif comando.startswith("memoria-"):
            intervalo = int(comando.split("-")[1])
            if not monitor_ligado["memoria"]:
                monitor_ligado["memoria"]  = True
                t = threading.Thread(target=thread_memoria, args=(conexao, intervalo))
                t.daemon = True
                t.start()
            enviar(conexao, f"Monitor de MEMORIA iniciado a cada {intervalo}s.\n")
        

        else:
            enviar(conexao, f"Comando nao reconhecido: {comando}\n")


def main():

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('', 5000))
    servidor.listen()

    conexao, endereco = servidor.accept()
    print(f"Cliente conectado: {endereco}")
    
    horario = datetime.now().strftime("%H:%M:%S")
    menu = (
        f"{horario}: CONECTADO!!\n"
        "Monitores disponíveis:\n"
        "  CPU-<segundos>\n"
        "  memoria-<segundos>\n"
        "  quit-<monitor>\n"
        "  exit\n"
    )
    conexao.send(menu.encode()) 

    thread_leitura(conexao) 
    
    conexao.close()
    servidor.close()

if __name__ == "__main__":
    main()