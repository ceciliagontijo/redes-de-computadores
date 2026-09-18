import socket
from datetime import datetime
import threading
import psutil
import time
import sys

clientes_conectados = 0

lock_cont = threading.Lock()

lock_envio = threading.Lock()

def enviar(conexao, texto):
    lock_envio.acquire()
    try:
        conexao.send(texto.encode())
        return True
    except (BrokenPipeError, ConnectionResetError, OSError):
        return False
    finally:
        lock_envio.release()

def thread_cpu(conexao, intervalo, monitor_ligado):
    while monitor_ligado["cpu"]:
        uso = psutil.cpu_percent(interval=1)
        if not enviar(conexao, f"[CPU] uso atual: {uso}%\n"):
            monitor_ligado["cpu"] = False
            break
        time.sleep(intervalo)

def thread_memoria(conexao, intervalo, monitor_ligado):
    while monitor_ligado["memoria"]:
        uso = psutil.virtual_memory().percent
        enviar(conexao, f"[MEMORIA] uso atual: {uso}%\n")
        time.sleep(intervalo)

    print("Thread de MEMORIA finalizada")

def thread_leitura(conexao, monitor_ligado):
    while True:
        try:
            dados = conexao.recv(1024).decode()
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            print("Cliente desconectou sem aviso")
            break

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
                t = threading.Thread(target=thread_cpu, args=(conexao, intervalo, monitor_ligado))
                t.daemon = True
                t.start()
            enviar(conexao, f"Monitor de CPU iniciado a cada {intervalo}s.\n")  

        elif comando.startswith("memoria-"):
            intervalo = int(comando.split("-")[1])
            if not monitor_ligado["memoria"]:
                monitor_ligado["memoria"]  = True
                t = threading.Thread(target=thread_memoria, args=(conexao, intervalo, monitor_ligado))
                t.daemon = True
                t.start()
            enviar(conexao, f"Monitor de MEMORIA iniciado a cada {intervalo}s.\n")
        

        else:
            enviar(conexao, f"Comando nao reconhecido: {comando}\n")

        monitor_ligado["cpu"] = False
        monitor_ligado["memoria"] = False


def atender_cliente(conexao, limite_clientes): #mudar

        global clientes_conectados

        with lock_cont:
            if clientes_conectados >= limite_clientes:
                conexao.send("Não foi possível conectar, limite de clientes atingido\n".encode())
                conexao.close()
                return 
            clientes_conectados += 1
        

        monitor_ligado = {"cpu": False, "memoria": False}

        try:
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

            thread_leitura(conexao, monitor_ligado)

        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
            print("Erro de conexão:", {e})

        finally:
            monitor_ligado["cpu"] = False
            monitor_ligado["memoria"] = False

            with lock_cont:
                clientes_conectados -= 1

            try:
                conexao.close()
            except OSError:
                pass

            print("Conexão encerrada. Clientes conectados:", {clientes_conectados})


def main():
    limite_clientes = int(sys.argv[1])

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(('', 5000))
    servidor.listen()

    while True:
        try:
            conexao, endereco = servidor.accept()
        except OSError as e:
            print("Erro ao aceitar conexão:", {e})
            continue

        print(f"Cliente conectado: {endereco}")
        t = threading.Thread(target=atender_cliente, args=(conexao, limite_clientes))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuário.")