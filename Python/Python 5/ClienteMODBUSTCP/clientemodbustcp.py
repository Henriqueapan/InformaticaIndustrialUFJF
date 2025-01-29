from pyModbusTCP.client import ModbusClient
from pymodbus.payload import BinaryPayloadBuilder
from time import sleep

class ClienteMODBUSTCP():
    """
    Classe Cliente MODBUS
    """
    def __init__(self, server_ip,porta,scan_time=1):
        """
        Construtor
        """
        self._cliente = ModbusClient(host=server_ip,port = porta)
        self._scan_time = scan_time

    def atendimento(self):
        """
        Método para atendimento do usuário
        """
        self._cliente.open()
        try:
            atendimento = True
            while atendimento:
                sel = input("Deseja realizar uma leitura, escrita ou configuração? (1- Leitura | 2- Escrita | 3- Configuração | 4- Sair): ")
                
                if sel == '1':
                    tipo = input("""Qual tipo de dado deseja ler? (1- Holding Register | 2- Coil | 3- Input Register | 4- Discrete Input) :""")
                    addr = input(f"Digite o endereço da tabela MODBUS: ")
                    nvezes = input("Digite o número de vezes que deseja ler: ")
                    for i in range(0,int(nvezes)):
                        print(f"Leitura {i+1}: {self.lerDado(int(tipo), int(addr))}")
                        sleep(self._scan_time)
                elif sel =='2':
                    tipo = input("""Qual tipo de dado deseja escrever? (1- Holding Register | 2- Coil) :""")
                    addr = input(f"Digite o endereço da tabela MODBUS: ")
                    valor = input(f"Digite o valor que deseja escrever: ")
                    self.escreveDado(int(tipo),int(addr),valor)

                elif sel=='3':
                    scant = input("Digite o tempo de varredura desejado [s]: ")
                    self._scan_time = float(scant)

                elif sel =='4':
                    self._cliente.close()
                    atendimento = False
                else:
                    print("Seleção inválida")
        except Exception as e:
            print('Erro no atendimento: ',e.args)

    def __identificarTipoDeDado(self, valor):
        """
        Método estático para identificar se o tipo de dado é str, int, ou float
        """
        tipo_valor = str

        if valor.isdigit():
            valor = int(valor)
            tipo_valor = int
        else:
            try:
                valor = float(valor)
                tipo_valor = float
            except ValueError:
                pass

        return tipo_valor

    def lerDado(self, tipo, addr):
        """
        Método para leitura de um dado da Tabela MODBUS
        """
        if tipo == 1:
            return self._cliente.read_holding_registers(addr,1)[0]

        if tipo == 2:
            return self._cliente.read_coils(addr,1)[0]

        if tipo == 3:
            return self._cliente.read_input_registers(addr,1)[0]

        if tipo == 4:
            return self._cliente.read_discrete_inputs(addr,1)[0]

    def escreveDado(self, tipo_addr, addr, valor:str):
        """
        Método para a escrita de dados na Tabela MODBUS
        """
        tipo_valor = self.__identificarTipoDeDado(valor)
        if tipo_valor is str: raise TypeError("Valor escrito não pode ser uma string")

        if tipo_addr == 1:
            return self._cliente.write_single_register(addr,tipo_valor(valor)) if tipo_valor is int else None


        if tipo_addr == 2:
            return self._cliente.write_single_coil(addr,valor) if tipo_valor is int else None