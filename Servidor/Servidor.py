import socket
import psutil
import webbrowser
import threading

class ServidorComandos:
    def __init__(self, host='0.0.0.0', porta=5551):
        self.host = host
        self.porta = porta
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ativo = True
        self.clientes = {}  # armazena dados recebidos {endereco: dados}

    def iniciar(self):
        self.socket_servidor.bind((self.host, self.porta))
        self.socket_servidor.listen(5)
        print(f"Servidor ouvindo em {self.host}:{self.porta}")

        while self.ativo:
            try:
                cliente_socket, endereco = self.socket_servidor.accept()
                print(f"Conexão de {endereco} estabelecida.")
                thread = threading.Thread(target=self.tratar_comando, args=(cliente_socket, endereco))
                thread.start()
            except Exception as e:
                print(f"Erro: {e}")
                continue

    def tratar_comando(self, cliente_socket, endereco):
        try:
            mensagem = cliente_socket.recv(1024)
            comando = mensagem.decode("utf-8").strip()
            print(f"Comando recebido de {endereco}: {comando}")

            resposta = self.executar_comando(comando, endereco)
            cliente_socket.send(resposta.encode("utf-8"))

            if comando == "/off":
                self.encerrar()

        except Exception as e:
            cliente_socket.send(f"Erro ao processar comando: {e}".encode("utf-8"))
        finally:
            cliente_socket.close()

    def executar_comando(self, comando, endereco):
        if comando == "/help":
            return (
                "Ajuda Requisitada:\n"
                "\t /proc - quantidade de processadores\n"
                "\t /mem  - memória RAM livre\n"
                "\t /hd   - espaço em disco livre\n"
                "\t /ip   - endereços IP das interfaces\n"
                "\t /iface_off - interfaces desativadas\n"
                "\t /ports - portas TCP e UDP abertas\n"
                "\t /media - média simples dos dados (proc, mem, hd)\n"
                "\t /listar - listar clientes conectados\n"
                "\t /detalhar <ip> - detalhes de um cliente\n"
                "\t /google - abrir URL\n"
                "\t /off  - desligar servidor"
            )
        elif comando == "/proc":
            n = psutil.cpu_count(logical=True)
            self.armazenar_cliente(endereco, {'processadores': n})
            return f"Quantidade de processadores: {n}"
        elif comando == "/mem":
            mem = psutil.virtual_memory()
            livre_gb = mem.available / (1024**3)
            self.armazenar_cliente(endereco, {'memoria_livre_gb': livre_gb})
            return f"Memória RAM livre: {livre_gb:.2f} GB"
        elif comando == "/hd":
            disco_path = "c:\\" if psutil.WINDOWS else "/"
            disco = psutil.disk_usage(disco_path)
            livre_gb = disco.free / (1024**3)
            self.armazenar_cliente(endereco, {'disco_livre_gb': livre_gb})
            return f"Espaço em disco livre: {livre_gb:.2f} GB"
        elif comando == "/ip":
            interfaces = psutil.net_if_addrs()
            resultado = []
            for iface, addrs in interfaces.items():
                ips = [addr.address for addr in addrs if addr.family == socket.AF_INET]
                resultado.append(f"{iface}: {', '.join(ips) if ips else 'Sem IP IPv4'}")
            return "\n".join(resultado)
        elif comando == "/iface_off":
            stats = psutil.net_if_stats()
            desativadas = [iface for iface, st in stats.items() if not st.isup]
            if not desativadas:
                return "Todas as interfaces estão ativas."
            return "Interfaces desativadas:\n" + "\n".join(desativadas)
        elif comando == "/ports":
            conexoes = psutil.net_connections()
            portas_tcp = set()
            portas_udp = set()
            for c in conexoes:
                if c.status == psutil.CONN_LISTEN:
                    if c.type == socket.SOCK_STREAM:
                        portas_tcp.add(c.laddr.port)
                    elif c.type == socket.SOCK_DGRAM:
                        portas_udp.add(c.laddr.port)
            resposta = (
                f"Portas TCP abertas: {sorted(portas_tcp)}\n"
                f"Portas UDP abertas: {sorted(portas_udp)}"
            )
            return resposta
        elif comando == "/media":
            # média simples dos dados armazenados para este cliente
            dados = self.clientes.get(endereco[0])
            if not dados:
                return "Nenhum dado registrado deste cliente para calcular média."
            campos = ['processadores', 'memoria_livre_gb', 'disco_livre_gb']
            soma = 0
            count = 0
            for campo in campos:
                if campo in dados:
                    soma += dados[campo]
                    count += 1
            if count == 0:
                return "Dados insuficientes para cálculo de média."
            media = soma / count
            return f"Média simples dos dados: {media:.2f}"
        elif comando == "/listar":
            if not self.clientes:
                return "Nenhum cliente conectado."
            lista = "\n".join(self.clientes.keys())
            return f"Clientes conectados:\n{lista}"
        elif comando.startswith("/detalhar"):
            parts = comando.split()
            if len(parts) != 2:
                return "Uso correto: /detalhar <ip>"
            ip = parts[1]
            dados = self.clientes.get(ip)
            if not dados:
                return f"Nenhum dado encontrado para o cliente {ip}"
            detalhes = "\n".join(f"{k}: {v}" for k, v in dados.items())
            return f"Detalhes do cliente {ip}:\n{detalhes}"
        elif comando == "/google":
            self.abrir_url("https://laica.ifrn.edu.br/")
            return "Abrindo URL no navegador."
        elif comando == "/off":
            return "Desligando o servidor."
        else:
            return "Comando Inválido. Use /help para ajuda."

    def abrir_url(self, url):
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
        webbrowser.get('chrome').open_new_tab(url)

    def encerrar(self):
        print("Encerrando servidor...")
        self.ativo = False
        self.socket_servidor.close()

    def armazenar_cliente(self, endereco, dados):
        ip = endereco[0]
        if ip not in self.clientes:
            self.clientes[ip] = {}
        self.clientes[ip].update(dados)


if __name__ == "__main__":
    servidor = ServidorComandos()
    servidor.iniciar()
