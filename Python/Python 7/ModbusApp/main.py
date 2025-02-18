from kivy.app import App
from ModbusMenu.modbusmenuwidget import ModbusMenuWidget
from kivy.config import Config

class ModbusApp(App):
    def build(self):
        """
        Método para construção do aplicativo com base no widget criado
        """
        return ModbusMenuWidget()
    
     
if __name__ == '__main__':
    Config.set('graphics','resizable',True)
    ModbusApp().run()