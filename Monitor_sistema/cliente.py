import socket
import threading

def thread_teclado(conexao):
    while True:
        try:
            texto = input("> ")
        except (EOFError, KeyboardInterrupt):
            texto = "exit"
        try:
            conexao.send(texto.encode())
        except (BrokenPipeError, ConnectionResetError, OSError):
            print("Conexão com o servidor perdida.")
            break

        if texto.strip() == "exit":
            break

    try:
        conexao.close()
    except OSError:
        pass

def thread_receptor(conexao):
    while True:
        try:
            resposta = conexao.recv(1024).decode()
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            print("Conexão com o servidor perdida.")
            break

        if not resposta:
            print("Servidor encerrou a conexão.")
            break
        print(resposta)

    try:
        conexao.close()
    except OSError:
        pass


def main():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect(("127.0.0.1", 5000))
    except (ConnectionRefusedError, TimeoutError, OSError):
        print("Não foi possível conectar ao servidor: {e}")
        return

    try:
        msg1 = cliente.recv(1024).decode()
        print(msg1)
    except OSError as e:
        print("Erro ao receber mensagem do servidor:", {e})
        cliente.close()
        return
    
    t1 = threading.Thread(target=thread_teclado, args=(cliente,))
    t2 = threading.Thread(target=thread_receptor, args=(cliente,))

    t1.daemon = True
    t2.daemon = True

    t1.start()  
    t2.start()
        
    t1.join()

    cliente.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCliente encerrado pelo usuário.")