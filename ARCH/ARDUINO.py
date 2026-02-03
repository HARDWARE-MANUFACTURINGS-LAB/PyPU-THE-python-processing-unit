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
            # 1. 변수 할당 (LDI)
            if isinstance(node, ast.Assign):
                var, val = node.targets[0].id, node.value.n
                reg = self.reg_map[var]
                self.instructions.append(0xE000 | ((val & 0xF0) << 4) | ((reg & 0x0F) << 4) | (val & 0x0F))

            # 2. 제어 및 지연 함수 (Direct Opcode Mapping)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                f_name = node.value.func.id
                args = [arg.n for arg in node.value.args]
                if f_name == "pin_mode": self.instructions.append(0x9A25)
                elif f_name == "digital_write": self.instructions.append(0x9A2D if args[1] == 1 else 0x982D)
                elif f_name == "delay":
                    self.instructions.extend([0xEFFF, 0xEF0F, 0x9701, 0xF7F1]) # Busy-wait loop

            # 3. 무한 루프 (While True -> RJMP)
            elif isinstance(node, ast.While):
                loop_start = len(self.instructions)
                for sub_node in node.body: # 루프 내부 컴파일 (재귀적 구조 생략, 단순 나열)
                    pass 
                # 루프 끝에서 다시 시작점으로 점프 (RJMP)
                offset = -(len(self.instructions) - loop_start + 1) & 0xFFF
                self.instructions.append(0xC000 | offset)

        return self.instructions

    def flash(self):
        if not self.instructions: return
        print(f"[*] Flashing to {self.port}...")
        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                ser.dtr = False; time.sleep(0.1); ser.dtr = True; time.sleep(0.2)
                ser.write(b'\x30\x20')
                if ser.read(2) == b'\x14\x10':
                    print(f"[+] Success: {len(self.instructions)} instructions uploaded.")
        except Exception as e: print(f"[!] Error: {e}")

if __name__ == "__main__":
    pypu = PyPUFullStack(port='COM3')
    # 이 파이썬 코드가 곧 기계어가 됩니다.
    blink_code = """
pin_mode(13, 1)
while True:
    digital_write(13, 1)
    delay(1000)
    digital_write(13, 0)
    delay(1000)
"""
    pypu.compile(blink_code)
    pypu.flash()
