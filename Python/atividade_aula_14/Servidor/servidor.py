import socket
import cv2
import numpy as np
import os


_MAX_BUFSIZE = 2**14

class Servidor():
    """
    Classe Servidor - API Socket
    """

    def __init__(self, host, port):
        """
        Construtor da classe servidor
        """
        self._host = host
        self._port = port
        self.__tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def start(self):
        """
        Método que inicializa a execução do servidor
        """
        endpoint = (self._host, self._port)
        try:
            self.__tcp.bind(endpoint)
            self.__tcp.listen(1)
            print("Servidor iniciado em ", self._host, ": ", self._port)
            while True:
                con, client = self.__tcp.accept() # Comando bloqueante. O código bloqueia aqui e aguarda conexão de um client
                self._service(con, client)
        except Exception as e:
            print("Erro ao inicializar o servidor", e.args)

    def _service(self, con: socket.socket, client):
        """
        Método que implementa o serviço de calculadora
        :param con: objeto socket utilizado para enviar e receber dados
        :param client: é o endereço do cliente
        """
        print("Atendendo cliente ", client)
        while True:
            try:
                bytes_tam_img = con.recv(4) # Lê os 4 bytes representando o int de tamanho da imagem
                tam_img = int.from_bytes(bytes_tam_img, 'big')

                # Loop para ler a imagem inteira em partes
                bytes_read = 0
                bytes_img = b''
                while bytes_read < tam_img:
                    if (bytes_read + _MAX_BUFSIZE) > tam_img:
                        bytes_img += con.recv(tam_img - bytes_read)
                        bytes_read = tam_img
                    else:
                        bytes_img += con.recv(_MAX_BUFSIZE)
                        bytes_read += _MAX_BUFSIZE

                # Decodificando imagen
                img = cv2.imdecode(np.frombuffer(bytes_img, np.uint8), cv2.IMREAD_COLOR)

                # Processando imagem
                xml_classificador = os.path.join(
                    os.path.relpath(cv2.__file__).replace('__init__.py', ''),
                    'data\haarcascade_frontalface_default.xml'
                )
                face_cascade = cv2.CascadeClassifier(xml_classificador)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                # Desenhando retângulos nas áreas onde as faces foram detectadas
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

                # Codificando imagem com retângulos desenhados
                status, drawn_img_ndarray = cv2.imencode('.jpg', img)
                # TODO: utilizar status

                bytes_drawn_img = bytes(drawn_img_ndarray)
                bytes_tam_drawn_img = len(bytes_drawn_img).to_bytes(4, 'big')

                # Enviando de volta tamanho e em seguida imagem
                con.send(bytes_tam_drawn_img)
                con.send(bytes_drawn_img)

                print(client, " -> requisição atendida")
            except OSError as e:
                print("Erro de conexão ", client, ": ", e.args)
                return
            except Exception as e:
                print("Erro nos dados recebidos pelo cliente ", client, ": ", e.args)
                con.send(bytes("Erro", 'ascii'))
                return
