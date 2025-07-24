import socket
import psutil
import webbrowser


class ServidorComandos:
    def __init__(self, host='0.0.0.0', porta=5551):
        self.host = host
        self.porta = porta
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ativo = True

    def iniciar(self):
        self.socket_servidor.bind((self.host, self.porta))
        self.socket_servidor.listen(5)
        print(f"Servidor ouvindo em {self.host}:{self.porta}")

        while self.ativo:
            try:
                cliente_socket, endereco = self.socket_servidor.accept()
                print(f"Conexão de {endereco} estabelecida.")
                self.tratar_comando(cliente_socket)
                cliente_socket.close()
            except Exception as e:
                print(f"Erro: {e}")
                continue

    def tratar_comando(self, cliente_socket):
        try:
            mensagem = cliente_socket.recv(64)  # aumentei o buffer por segurança
            comando = mensagem.decode("utf-8").strip()
            print(f"Comando recebido: {comando}")

            resposta = self.executar_comando(comando)
            cliente_socket.send(resposta.encode("utf-8"))

            if comando == "/off":
                self.encerrar()

        except Exception as e:
            cliente_socket.send(f"Erro ao processar comando: {e}".encode("utf-8"))

    def executar_comando(self, comando):
        if comando == "/help":
            return (
                "Ajuda Requisitada:\n"
                "\t /mem  - ver a memória\n"
                "\t /hd   - espaço em disco\n"
                "\t /google - abrir URL\n"
                "\t /off  - desligar o servidor"
            )
        elif comando == "/mem":
            return str(psutil.virtual_memory())
        elif comando == "/hd":
            return str(psutil.disk_usage("c:\\"))
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


if __name__ == "__main__":
    servidor = ServidorComandos()
    servidor.iniciar()
