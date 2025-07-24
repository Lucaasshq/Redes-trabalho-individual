import socket

class ClienteTCP:
    def __init__(self, host='127.0.0.1', porta=5551):
        self.host = host
        self.porta = porta

    def conectar(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((self.host, self.porta))
                while True:
                    comando = input("Digite o comando (/help para ajuda, /off para sair): ").strip()
                    if not comando:
                        continue
                    s.send(comando.encode('utf-8'))
                    resposta = s.recv(4096).decode('utf-8')
                    print("Resposta do servidor:\n", resposta)
                    if comando == "/off":
                        print("Desconectando do servidor...")
                        break
            except ConnectionRefusedError:
                print(f"Não foi possível conectar ao servidor {self.host}:{self.porta}")
            except Exception as e:
                print(f"Erro: {e}")

if __name__ == "__main__":
    cliente = ClienteTCP()
    cliente.conectar()
