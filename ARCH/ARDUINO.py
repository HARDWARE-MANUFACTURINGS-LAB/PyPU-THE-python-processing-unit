import ast
import serial
import time

class PyPUFullStack:
    def __init__(self, port='COM3', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.reg_map = {'a': 16, 'b': 17, 'c': 18}
        self.instructions = []
        self.PORTB = 0x05
        self.DDRB = 0x04

    def compile(self, source_code):
        tree = ast.parse(source_code)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                var = node.targets[0].id
                val = node.value.n
                reg = self.reg_map[var]
                self.instructions.append(0xE000 | ((val & 0xF0) << 4) | ((reg & 0x0F) << 4) | (val & 0x0F))

            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                func_name = node.value.func.id
                args = [arg.n for arg in node.value.args]
                if func_name == "pin_mode":
                    self.instructions.append(0x9A25) 
                elif func_name == "digital_write":
                    self.instructions.append(0x9A2D if args[1] == 1 else 0x982D)

            elif isinstance(node, ast.If):
                reg = self.reg_map[node.test.left.id]
                val = node.test.comparators[0].n
                self.instructions.append(0x3000 | ((val & 0xF0) << 4) | ((reg & 0x0F) << 4) | (val & 0x0F))
                self.instructions.append(0xF001) 

        return self.instructions

    def flash(self):
        if not self.instructions: return
        with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
            ser.dtr = False
            time.sleep(0.1)
            ser.dtr = True
            time.sleep(0.2)
            ser.write(b'\x30\x20')
            if ser.read(2) == b'\x14\x10':
                for inst in self.instructions:
                    pass 

if __name__ == "__main__":
    pypu = PyPUFullStack(port='COM3')
    code = """
pin_mode(13, 1)
a = 10
if a == 10:
    digital_write(13, 1)
"""
    pypu.compile(code)
    pypu.flash()
