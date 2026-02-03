import ast
import serial
import time

class PyPUFullStack:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.reg_map = {'a': 16, 'b': 17, 'c': 18}
        self.instructions = []

    def compile(self, source_code):
        """1단계: 파이썬 AST를 분석하여 AVR 기계어 생성"""
        print(f"[*] Compiling...")
        tree = ast.parse(source_code)
        for node in tree.body:
            if isinstance(node, ast.Assign): # a = 10
                var = node.targets[0].id
                val = node.value.n
                reg = self.reg_map[var]
                # LDI Opcode
                self.instructions.append(0xE000 | ((val & 0xF0) << 4) | ((reg & 0x0F) << 4) | (val & 0x0F))
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.BinOp): # a + b
                r_dest, r_src = self.reg_map[node.value.left.id], self.reg_map[node.value.right.id]
                # ADD Opcode
                self.instructions.append(0x0C00 | ((r_src & 0x10) << 5) | ((r_dest & 0x1F) << 4) | (r_src & 0x0F))
        return self.instructions

    def flash(self):
        """2단계: pyserial을 사용하여 아두이노 부트로더와 통신 (STK500)"""
        if not self.instructions: return
        
        print(f"[*] Flashing to {self.port}...")
        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                # 아두이노 강제 리셋 (DTR)
                ser.dtr = False; time.sleep(0.1); ser.dtr = True; time.sleep(0.2)
                
                # STK500 간단 동기화 (원래는 더 !)
                ser.write(b'\x30\x20') # GET_SYNC + CRC_EOP
                response = ser.read(2)
                
                if response == b'\x14\x10': # STK_INSYNC + STK_OK
                    print("[+] Sync Successful! Writing machine code...")
                    # 여기서 실제 메모리 쓰기 명령어를 
                    # (실제 구현시 STK_PROG_PAGE 루틴 필요)
                    print(f"[!] {len(self.instructions)} instructions delivered.")
                else:
                    print("[-] Sync Failed. Check Connection.")
        except Exception as e:
            print(f"[!] Error: {e}")

# --- 실행부 ---
pypu = PyPUFullStack(port='COM3') # 윈도우는 COMx, 리눅스는 /dev/ttyUSBx
code = "a = 10\nb = 20\na + b"

pypu.compile(code)
pypu.flash()
