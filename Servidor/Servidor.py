import socket
import threading
import psutil
import json
from cryptography.fernet import Fernet

CHAVE = b'6YlxNQwFwHPKsLDX7wYvWcHnB66ZZdq2Rfzklc_mnF0='  # Mesma chave usada no cliente
fernet = Fernet(CHAVE)

class ServidorTCP:
    def __init__(self, host='0.0.0.0', porta=5551):
        self.host = host
        self.porta = porta
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientes = {}

    def iniciar(self):
        self.servidor.bind((self.host, self.porta))
        self.servidor.listen()
        print(f"Servidor ouvindo em {self.host}:{self.porta}")

        while True:
            cliente_socket, endereco = self.servidor.accept()
            print(f"Cliente conectado: {endereco}")
            self.clientes[endereco] = cliente_socket
            threading.Thread(target=self.atender_cliente, args=(cliente_socket, endereco)).start()

    def atender_cliente(self, cliente_socket, endereco):
        while True:
            try:
                dados_cript = cliente_socket.recv(4096)
                if not dados_cript:
                    break
                comando = fernet.decrypt(dados_cript).decode('utf-8')
                print(f"Comando recebido de {endereco}: {comando}")
                resposta = self.processar_comando(comando, endereco)
                cliente_socket.send(fernet.encrypt(resposta.encode('utf-8')))
                if comando == "/off":
                    break
            except Exception as e:
                print(f"Erro com cliente {endereco}: {e}")
                break

        cliente_socket.close()
        del self.clientes[endereco]
        print(f"Cliente {endereco} desconectado.")

    def processar_comando(self, comando, endereco):
        try:
            if comando == "/cpu":
                return str(psutil.cpu_count(logical=True))
            elif comando == "/ram":
                return f"{psutil.virtual_memory().available // (1024**2)} MB livres"
            elif comando == "/disco":
                return f"{psutil.disk_usage('/').free // (1024**3)} GB livres"
            elif comando == "/ip":
                return json.dumps(psutil.net_if_addrs(), default=str)
            elif comando == "/off_interfaces":
                desligadas = [iface for iface, info in psutil.net_if_stats().items() if not info.isup]
                return "Desativadas: " + ", ".join(desligadas)
            elif comando == "/portas":
                conexoes = psutil.net_connections()
                portas_tcp = {c.laddr.port for c in conexoes if c.type == socket.SOCK_STREAM}
                portas_udp = {c.laddr.port for c in conexoes if c.type == socket.SOCK_DGRAM}
                return f"TCP: {sorted(portas_tcp)}\nUDP: {sorted(portas_udp)}"
            elif comando == "/media":
                cpu = psutil.cpu_count()
                ram = psutil.virtual_memory().available // (1024**2)
                disco = psutil.disk_usage('/').free // (1024**3)
                media = (cpu + ram + disco) // 3
                return f"Média (CPU + RAM + Disco): {media}"
            elif comando == "/clientes":
                return "\n".join([f"{i+1}. {ip[0]}:{ip[1]}" for i, ip in enumerate(self.clientes.keys())])
            elif comando.startswith("/detalhar"):
                partes = comando.split()
                if len(partes) != 2:
                    return "Uso: /detalhar <número do cliente>"
                try:
                    idx = int(partes[1]) - 1
                    cliente = list(self.clientes.keys())[idx]
                    return f"Cliente {idx+1}: {cliente[0]}:{cliente[1]}"
                except:
                    return "Cliente não encontrado."
            elif comando == "/help":
                return "\n".join([
                    "/cpu", "/ram", "/disco", "/ip", "/off_interfaces", 
                    "/portas", "/media", "/clientes", "/detalhar N", "/off"
                ])
            else:
                return "Comando desconhecido. Use /help."
        except Exception as e:
            return f"Erro ao processar comando: {e}"

if __name__ == "__main__":
    servidor = ServidorTCP()
    servidor.iniciar()
