import socket
import threading

def thread_teclado(conexao):
     while True:
        texto = input("> ")  
        conexao.send(texto.encode())  
    
        if texto.strip() == "exit":
            print("Conexão encerrada")
            break

def thread_receptor(conexao):
    while True:
        resposta = conexao.recv(1024).decode() 

        if not resposta:
            break

        print(resposta)


def main():
        
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(("127.0.0.1", 5000))

    msg1 = cliente.recv(1024).decode()
    print(msg1)
    
    t1 = threading.Thread(target=thread_teclado, args=(cliente,))
    t2 = threading.Thread(target=thread_receptor, args=(cliente,))

    t1.daemon = True
    t2.daemon = True

    t1.start()  
    t2.start()
        
    t1.join()

    cliente.close()

if __name__ == "__main__":
    main()