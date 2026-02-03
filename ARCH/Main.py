import sys
from ARCH.ARDUINO import PyPU_AVR
from ARCH.Esp32 import PyPU_ESP32
from ARCH.Stm32nucleo import PyPU_NUCLEO

class PyPU_Commander:
    def __init__(self, target, port):
        self.target = target.upper()
        self.port = port
        self.engines = {
            'AVR': PyPU_AVR,
            'ESP32': PyPU_ESP32,
            'NUCLEO': PyPU_NUCLEO
        }

    def deploy(self, source_code):
        if self.target not in self.engines:
            print(f"[!] Target {self.target} not supported.")
            return

        print(f"[*] Deploying to {self.target} via {self.port}...")
        engine = self.engines[self.target](self.port)
        instructions = engine.compile(source_code)
        engine.flash(instructions)
        print(f"[*] {self.target} synchronized successfully.")

if __name__ == "__main__":
    target_board = 'NUCLEO'
    comm_port = 'COM4'
    
    logic = """
pin_mode(13, 1)
while True:
    digital_write(13, 1)
    delay(500)
    digital_write(13, 0)
    delay(500)
"""
    
    commander = PyPU_Commander(target_board, comm_port)
    commander.deploy(logic)
