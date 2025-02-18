from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock, ClockEvent
from pyModbusTCP.client import ModbusClient
import re

class ModbusMenuWidget(BoxLayout):
    __ip: str
    __port: int
    __modbusClient: ModbusClient
    __modbusClientReadEvent: ClockEvent

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__ip = 'localhost'
        self.__port = 502
        self.__modbusClient = None
        self.__modbusAddr = 1000 # TODO: Adaptar

    def modbus_client_read_registers(self, dt):
        self.ids['result_label'].text = str(self.__modbusClient.read_holding_registers(self.__modbusAddr, 1)[0])

    def toggle_connect(self):
        if self.__modbusClient is not None and self.__modbusClient.is_open:
            self.__modbusClient.close()
            self.ids['result_label'].text = 'Awaiting Connection'
            self.ids['conn_btn'].text = 'Connect'
            self.ids['conn_btn'].color = [0, 0, 0, 1]

            self.ids['ip_input'].disabled = False
            self.ids['port_input'].disabled = False

            self.__modbusClientReadEvent.cancel()
        else:
            self.__ip = self.ids['ip_input'].text
            self.__port = int(self.ids['port_input'].text)
            self.__modbusClient = ModbusClient(self.__ip, self.__port)

            self.__modbusClient.open()
            self.ids['result_label'].text = '...'
            self.ids['conn_btn'].text = 'Disconnect'
            self.ids['conn_btn'].color = [1, 0, 0, 1]
            self.ids['ip_input'].disabled = True
            self.ids['port_input'].disabled = True

            self.__modbusClientReadEvent = Clock.schedule_interval(self.modbus_client_read_registers, 1)
            
    

class IntInput(TextInput):
    def __init(self, **kwargs):
        super().__init__(**kwargs)

    def insert_text(self, substring:str, from_undo=False):
        int_substring = ''.join(re.findall(r'\d', substring))
        return super().insert_text(int_substring, from_undo)