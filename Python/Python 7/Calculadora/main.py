from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from numexpr import evaluate

class CalculatorWidget(BoxLayout):
    # TODO: Implementar avaliador de expressão algébrica literal para deixar de usar módulo externo

    expression: str
    last_result: float | int # Poderá ser usado para implementar manipulações do resultado anterior futuramente
    displaying_error: bool

    def __init__(self):
        super().__init__()
        self.expression = ''
        self.last_result = ''
        self.displaying_error = False

    def insert_operator(self, op: str):
        if not self.expression or self.displaying_error: return

        if self.expression[-1] in ['+', '-', '/', '*', '**']:
            self.expression = self.expression[:-1] + op
        else: self.expression += op
        self.update_display()

    def insert(self, char: str | int):
        if type(char) is int or (type(char) is str and char == '.'):
            if self.displaying_error:
                self.expression = str(char)
                self.displaying_error = False
            else:
                self.expression += str(char)
            
            self.update_display()
        else: raise ValueError("Attempt to insert invalid character in current expression: " + str(char))

    def delete(self):
        if not self.expression: return

        if self.displaying_error:
            self.expression = ''
            self.displaying_error = False

        self.expression = self.expression[:-1]
        self.update_display()

    def clear(self):
        self.displaying_error = False

        self.expression = ''
        self.update_display()

    def compute(self):
        try:
            expression_value = evaluate(self.expression).item()
            self.last_result = expression_value
            self.expression = str(expression_value)
            self.displaying_error = False
        except:
            self.last_result = 'Invalid expression'
            self.displaying_error = True
        
        self.update_display()

    def update_display(self):
        # TODO: Mudar para usar Observer em __expression e __last_result
        self.ids['display'].text = str(self.last_result) if self.displaying_error else str(self.expression)


class MyWidget2(BoxLayout):
    pass

class CalculatorApp(App):
    def build(self):
        """
        Método para construção do aplicativo com base no widget criado
        """
        # Aquilo que é retornado nesse método torna-se o componente/widget raíz do app
        return CalculatorWidget() # MyWidget é o widget root do app
 
if __name__ == '__main__':
    Config.set('graphics','resizable',True)
    CalculatorApp().run()