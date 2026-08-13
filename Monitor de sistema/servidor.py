import socket
from datetime import datetime

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(('', 5000))
servidor.listen()

print("Servidor escutando...")

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

while True:
    dados = conexao.recv(1024)  
    if not dados:
        print("Cliente desconectou.")
        break
 
    mensagem = dados.decode()  
    print(f"Recebido do cliente: {mensagem!r}")
 
    if mensagem.strip() == "exit":
        print("Comando exit recebido. Encerrando.")
        break
 
    resposta = f"Servidor recebeu: {mensagem}"
    conexao.send(resposta.encode())
 
conexao.close()
servidor.close()