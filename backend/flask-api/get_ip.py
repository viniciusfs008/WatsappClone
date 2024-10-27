import socket
import os


def get_local_ip():
    try:
        # Conecta-se a um endereço IP externo para determinar o IP local
        # O endereço IP aqui não precisa ser acessível; é apenas uma forma de forçar a resolução do IP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))  # Usando o Google DNS como um exemplo
        local_ip = sock.getsockname()[0]  # Obtém o IP local

        host_ip = os.environ.get("HOST_IP")
        if host_ip:
            return host_ip
    except Exception as e:
        return f"Erro ao obter IP local: {e}"
    finally:
        sock.close()  # Fecha o socket

    return local_ip

