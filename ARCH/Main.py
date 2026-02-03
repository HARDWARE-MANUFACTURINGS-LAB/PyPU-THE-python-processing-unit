import sys
from ARCH.ARDUINO import PyPU_AVR
from ARCH.Esp32 import PyPU_ESP32
from ARCH.Stm32nucleo import PyPU_ARM
from ARCH.Amd64 import PyPU_X64
from ARCH.RISCV import PyPU_RISCV

class PyPU_Commander:
    def __init__(self, target, port=None):
        self.target = target.upper()
        self.port = port
        self.engines = {
            'AVR': PyPU_AVR,
            'ESP32': PyPU_ESP32,
            'ARM': PyPU_ARM,
            'X64': PyPU_X64,
            'RISCV': PyPU_RISCV
        }

    def deploy(self, source_code):
        if self.target not in self.engines:
            return
        
        engine = self.engines[self.target](self.port) if self.port else self.engines[self.target]()
        instructions = engine.compile(source_code)
        engine.execute_or_flash(instructions)

if __name__ == "__main__":
    
    target_arch = 'RISCV' 
    commander = PyPU_Commander(target_arch)
    commander.deploy("x10 = 5\nx11 = 10")
