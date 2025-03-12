from pyModbusTCP.server import DataBank, ModbusServer
from pyModbusTCP.utils import encode_ieee, long_list_to_word
from pymodbus.client.mixin import ModbusClientMixin
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import random, struct
from time import sleep

modbusDataTable: dict[dict[str, str|int]] = {
    "tipo_motor": { "addr": 708, "float": True, "multiplicador": 1, "valor": None, "unidade": ""},
    "temp_r": { "addr": 700, "float": True, "multiplicador": 10, "valor": None, "unidade": "°C"},
    "temp_s": { "addr": 702, "float": True, "multiplicador": 10, "valor": None, "unidade": "°C"},
    "temp_t": { "addr": 704, "float": True, "multiplicador": 10, "valor": None, "unidade": "°C"},
    "temp_carc": { "addr": 706, "float": True, "multiplicador": 10, "valor": None, "unidade": "°C"},
    "carga_est": { "addr": 710, "float": True, "multiplicador": 1, "valor": None, "unidade": "Kgf/cm²"},
    "vel_est": { "addr": 724, "float": True, "multiplicador": 1, "valor": None, "unidade": "m/min"},
    "curr_r": { "addr": 840, "float": False, "multiplicador": 100, "valor": None, "unidade": "A"},
    "curr_s": { "addr": 841, "float": False, "multiplicador": 100, "valor": None, "unidade": "A"},
    "curr_t": { "addr": 842, "float": False, "multiplicador": 100, "valor": None, "unidade": "A"},
    "curr_N": { "addr": 843, "float": False, "multiplicador": 100, "valor": None, "unidade": "A"},
    "curr_med": { "addr": 845, "float": False, "multiplicador": 100, "valor": None, "unidade": "A"},
    "tens_rs": { "addr": 847, "float": False, "multiplicador": 10, "valor": None, "unidade": "V"},
    "tens_st": { "addr": 848, "float": False, "multiplicador": 10, "valor": None, "unidade": "V"},
    "tens_tr": { "addr": 849, "float": False, "multiplicador": 10, "valor": None, "unidade": "V"},
    "pot_ativ_r": { "addr": 852, "float": False, "multiplicador": 1, "valor": None, "unidade": "W"},
    "pot_ativ_s": { "addr": 853, "float": False, "multiplicador": 1, "valor": None, "unidade": "W"},
    "pot_ativ_t": { "addr": 854, "float": False, "multiplicador": 1, "valor": None, "unidade": "W"},
    "pot_ativ_total": { "addr": 855, "float": False, "multiplicador": 1, "valor": None, "unidade": "W"},
    "pot_reativ_r": { "addr": 856, "float": False, "multiplicador": 1, "valor": None, "unidade": "VAr"},
    "pot_reativ_s": { "addr": 857, "float": False, "multiplicador": 1, "valor": None, "unidade": "VAr"},
    "pot_reativ_t": { "addr": 858, "float": False, "multiplicador": 1, "valor": None, "unidade": "VAr"},
    "pot_reativ_total": { "addr": 859, "float": False, "multiplicador": 1, "valor": None, "unidade": "VAr"},
    "pot_apar_r": { "addr": 860, "float": False, "multiplicador": 1, "valor": None, "unidade": "VA"},
    "pot_apar_s": { "addr": 861, "float": False, "multiplicador": 1, "valor": None, "unidade": "VA"},
    "pot_apar_t": { "addr": 862, "float": False, "multiplicador": 1, "valor": None, "unidade": "VA"},
    "pot_apar_total": { "addr": 863, "float": False, "multiplicador": 1, "valor": None, "unidade": "VA"},
    "rot_motor": { "addr": 884, "float": True, "multiplicador": 1, "valor": None, "unidade": "RPM"},
    "driver_partida": { "addr": 1216, "float": False, "multiplicador": 1, "valor": None, "unidade": ""},
    "ctrl_partida_inv": { "addr": 1312, "float": False, "multiplicador": 1, "valor": None, "ctrl": True}, # TODO: Definir valor inicial das variáveis de controle
    "freq_partida_inv": { "addr": 1313, "float": False, "multiplicador": 10, "valor": None, "ctrl": True},
    "tempo_rampa_partida_inv": { "addr": 1314, "float": False, "multiplicador": 10, "valor": None, "ctrl": True},
    "tempo_rampa_desacc_inv": { "addr": 1315, "float": False, "multiplicador": 10, "valor": None, "ctrl": True},
    "ctrl_partida_soft": { "addr": 1316, "float": False, "multiplicador": 1, "valor": None, "ctrl": True},
    "tempo_rampa_partida_soft": { "addr": 1317, "float": False, "multiplicador": 1, "valor": None, "ctrl": True},
    "tempo_rampa_desacc_soft": { "addr": 1318, "float": False, "multiplicador": 1, "valor": None, "ctrl": True},
    "ctrl_partida_dir": { "addr": 1319, "float": False, "multiplicador": 1, "valor": None, "ctrl": True},
    "ctrl_driver_partida": { "addr": 1324, "float": False, "multiplicador": 1, "valor": None, "ctrl": True},
    "ctrl_tipo_pid": { "addr": 1332, "float": False, "multiplicador": 1, "valor": None, "ctrl": True},
    "energ_ativ": { "addr": 1210, "float": False, "multiplicador": 1, "valor": None, "ctrl": True},
    "energ_reativ": { "addr": 1212, "float": False, "multiplicador": 1, "valor": None, "ctrl": True},
    "energ_apar": { "addr": 1214, "float": False, "multiplicador": 1, "valor": None, "ctrl": True},
    "status_mot": { "addr": 1330, "float": False, "multiplicador": 1, "bit": 0, "valor": None, "unidade": ""},
    "torque_mot": { "addr": 1420, "float": True, "multiplicador": 100, "valor": None, "unidade": "N*m"}
}

class ServidorMODBUS():
    """
    Classe Servidor Modbus
    """
    
    def __init__(self, host_ip, port):
        """
        Construtor
        """
        self._db:DataBank = DataBank()
        self._server:ModbusServer = ModbusServer(host=host_ip,port=port,no_block=True,data_bank=self._db)
       
    def __readFloat32FromHoldingRegisters(self, start_addr:int):
        read_result = self._db.get_holding_registers(start_addr, 2)

        decoder = BinaryPayloadDecoder(read_result, Endian.BIG)
        return decoder.decode_32bit_float()
        
    def run(self):
        """
        Execução do servidor Modbus
        """
        try:
            self._server.start()
            print("Servidor MODBUS em execução")
            while True:
                self._db.set_holding_registers(1000,[random.randrange(int(0.95*400),int(1.05*400))])
                self.__set_esteira_modbus_table_values()
                print('======================')
                print("Tabela MODBUS")
                print(f'Holding Register \r\n R1000: {self._db.get_holding_registers(1000)} \r\n R2000: {self._db.get_holding_registers(2000)}')
                print(f'Coil \r\n R1000: {self._db.get_coils(1000)}')
                sleep(1)
        except Exception as e:
            print("Erro: ",e.args)

    # Função para converter float para dois registradores de 16 bits
    def __float_to_registers(self, value):
        """Converte um float para dois inteiros de 16 bits."""
        float_bytes = struct.pack('<f', value)  # Converte para bytes (big-endian)
        high, low = struct.unpack('<HH', float_bytes)  # Divide em dois inteiros de 16 bits
        return [high, low]

    def __set_esteira_modbus_table_values(self):
        for info_valor in modbusDataTable.values():
            is_ctrl_var = info_valor.get("ctrl") is not None
            if is_ctrl_var: continue
            regs =\
                self.__float_to_registers(float(random.randrange(int(0.95*400),int(1.05*400))/10.24)) if info_valor["float"]\
                else [random.randrange(int(0.95*400),int(1.05*400))]

            self._db.set_holding_registers(\
                info_valor["addr"],\
                regs
            )