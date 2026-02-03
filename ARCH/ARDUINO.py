import ast
import serial
import time

class PyPUFullStack:
    def __init__(self, port='COM3', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.reg_map = {'a': 16, 'b': 17, 'c': 18}
        self.instructions = []

    def compile(self, source_code):
        tree = ast.parse(source_code)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                var = node.targets[0].id
                val = node.value.n
                reg = self.reg_map[var]
                self.instructions.append(0xE000 | ((val & 0xF0) << 4) | ((reg & 0x0F) << 4) | (val & 0x0F))

            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                f_name = node.value.func.id
                args = [arg.n for arg in node.value.args]
                if f_name == "pin_mode":
                    self.instructions.append(0x9A25) 
                elif f_name == "digital_write":
                    self.instructions.append(0x9A2D if args[1] == 1 else 0x982D)
                elif f_name == "delay":
                    self.instructions.extend([0xEFFF, 0xEF0F, 0x9701, 0xF7F1])

            elif isinstance(node, ast.While):
                start_addr = len(self.instructions)
                for sub_node in node.body:
                    pass 
                offset = (-(len(self.instructions) - start_addr + 1)) & 0xFFF
                self.instructions.append(0xC000 | offset)

        return self.instructions

    def flash(self):
        if not self.instructions: return
        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                ser.dtr = False
                time.sleep(0.1)
                ser.dtr = True
                time.sleep(0.2)
                
                ser.write(b'\x30\x20')
                if ser.read(2) == b'\x14\x10':
                    print("[*] Handshake Success")
                    for i, op in enumerate(self.instructions):
                        low, high = op & 0xFF, (op >> 8) & 0xFF
                        addr = i
                        ser.write(b'\x55' + addr.to_bytes(2, 'little') + b'\x20')
                        ser.read(2)
                        ser.write(b'\x64\x00\x02\x46' + bytes([low, high]) + b'\x20')
                        ser.read(2)
                    print(f"[*] Flashed {len(self.instructions)} instructions")
        except Exception as e:
            print(f"[!] Error: {e}")

if __name__ == "__main__":
    pypu = PyPUFullStack(port='COM3')
    code = """
pin_mode(13, 1)
while True:
    digital_write(13, 1)
    delay(1000)
    digital_write(13, 0)
    delay(1000)
"""
    pypu.compile(code)
    pypu.flash()
