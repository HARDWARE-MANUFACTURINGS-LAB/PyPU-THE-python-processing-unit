import ast
import serial
import time

class PyPUFullStack:
    def __init__(self, target='AVR', port='COM3', baudrate=115200):
        self.target = target
        self.port = port
        self.baudrate = baudrate
        self.config = {
            'AVR': {'reg': {'a': 16, 'b': 17}, 'base': 0x00},
            'ESP32': {'reg': {'a': 0x3FF44004}, 'base': 0x3FF44000},
            'NUCLEO': {'reg': {'a': 0x40020014}, 'base': 0x40020000}
        }
        self.instructions = []

    def compile(self, source_code):
        tree = ast.parse(source_code)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                var = node.targets[0].id
                val = node.value.n
                if self.target == 'AVR':
                    reg = self.config['AVR']['reg'][var]
                    self.instructions.append(0xE000 | ((val & 0xF0) << 4) | ((reg & 0x0F) << 4) | (val & 0x0F))
                elif self.target == 'NUCLEO':
                    self.instructions.append(0x2000 | (val & 0xFF))
                else:
                    self.instructions.append(('STORE_32', self.reg_map[var], val))

            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                f_name = node.value.func.id
                args = [arg.n for arg in node.value.args if isinstance(arg, (ast.Constant, ast.Num))]
                if f_name == "digital_write":
                    if self.target == 'AVR':
                        self.instructions.append(0x9A2D if args[1] == 1 else 0x982D)
                    elif self.target == 'NUCLEO':
                        self.instructions.append(0x6008)
                    else:
                        self.instructions.append(('GPIO_OUT', args[1]))
                elif f_name == "delay":
                    if self.target == 'AVR':
                        self.instructions.extend([0xEFFF, 0xEF0F, 0x9701, 0xF7F1])
                    else:
                        self.instructions.append(('DELAY', args[0]))

            elif isinstance(node, ast.While):
                start_addr = len(self.instructions)
                for sub_node in node.body: pass 
                if self.target == 'AVR':
                    offset = (-(len(self.instructions) - start_addr + 1)) & 0xFFF
                    self.instructions.append(0xC000 | offset)
                elif self.target == 'NUCLEO':
                    self.instructions.append(0xE7FE)

        return self.instructions

    def flash(self):
        if not self.instructions: return
        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                ser.dtr = False; time.sleep(0.1); ser.dtr = True; time.sleep(0.2)
                if self.target == 'AVR':
                    ser.write(b'\x30\x20')
                    if ser.read(2) == b'\x14\x10':
                        for i, op in enumerate(self.instructions):
                            low, high = op & 0xFF, (op >> 8) & 0xFF
                            ser.write(b'\x55' + i.to_bytes(2, 'little') + b'\x20')
                            ser.read(2)
                            ser.write(b'\x64\x00\x02\x46' + bytes([low, high]) + b'\x20')
                            ser.read(2)
                print(f"[*] {self.target} Territory Claimed.")
        except Exception as e:
            print(f"[!] {e}")

if __name__ == "__main__":
    pypu = PyPUFullStack(target='NUCLEO', port='COM4')
    code = "a = 1\ndigital_write(5, 1)\nwhile True: pass"
    pypu.compile(code)
    pypu.flash()
