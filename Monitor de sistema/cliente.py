import socket

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(("127.0.0.1", 5000))

print("Conectado ao servidor")

# 3) Recebe a MSG1 (o menu que o servidor manda assim que aceita a conexão)
msg1 = cliente.recv(1024).decode()
print(msg1)
 
# 4) Loop simples: digita algo, manda, recebe resposta, imprime
#    (na próxima etapa isso vira DUAS threads separadas)
while True:
    texto = input("> ")  # lê do teclado
    cliente.send(texto.encode())  # manda pro servidor
 
    if texto.strip() == "exit":
        print("Encerrando cliente.")
        break
 
    resposta = cliente.recv(1024).decode()
    print(resposta)
 
cliente.close()