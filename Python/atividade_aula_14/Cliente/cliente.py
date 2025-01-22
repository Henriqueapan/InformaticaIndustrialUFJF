import socket
import cv2
import numpy as np

class Cliente():
    """
    Classe Cliente - API Socket
    """
    def __init__(self, server_ip, port):
        """
        Construtor da classe Cliente
        """
        self.__server_ip = server_ip
        self.__port = port
        self.__tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    
    def start(self):
        """
        Método que inicializa a execução do Cliente
        """
        endpoint = (self.__server_ip,self.__port)
        try:
            self.__tcp.connect(endpoint)
            print("Conexão realizada com sucesso!")
            self.__method()
        except:
            print("Servidor não disponível")

    
    def __method(self):
        """
        Método que implementa as requisições do cliente
        """
        __MAX_BUFSIZE = 2**14

        try:
            # Obtendo imagem
            caminho_imagem = 'faces/face_scott.jpg'
            img = cv2.imread(caminho_imagem)

            # Convertendo para bytes
            status, img_ndarray = cv2.imencode('.jpg', img)
            bytes_img = bytes(img_ndarray)

            bytes_tam_img = len(bytes_img).to_bytes(4, 'big')

            self.__tcp.send(bytes_tam_img)
            self.__tcp.send(bytes_img)

            bytes_tam_img_drawn = self.__tcp.recv(4)
            tam_img_drawn = int.from_bytes(bytes_tam_img_drawn, 'big')

            
            # Loop para ler a imagem processada inteira em partes
            bytes_read = 0
            bytes_img_drawn = b''
            while bytes_read < tam_img_drawn:
                if (bytes_read + __MAX_BUFSIZE) > tam_img_drawn:
                    bytes_img_drawn += self.__tcp.recv(tam_img_drawn - bytes_read)
                    bytes_read = tam_img_drawn
                else:
                    bytes_img_drawn += self.__tcp.recv(__MAX_BUFSIZE)
                    bytes_read += __MAX_BUFSIZE

            img_drawn = cv2.imdecode(np.frombuffer(bytes_img_drawn, np.uint8), cv2.IMREAD_COLOR)

            cv2.imshow('Imagem Processada', img_drawn)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            self.__tcp.close()
        except Exception as e:
            print("Erro ao realizar comunicação com o servidor", e.args)
            return
