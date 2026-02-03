import struct
import ast

class PyPU_RISCV:
    def __init__(self, port=None):
        self.code_buffer = bytearray()
        self.regs = {'x0': 0, 'x1': 1, 'x10': 10, 'x11': 11}

    def compile(self, source):
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                reg_name = node.targets[0].id
                val = node.value.n
                # ADDI rd, x0, immediate (RISC-V의 전형적인 값 로드 방식)
                imm = val & 0xFFF
                rd = self.regs[reg_name]
                inst = (imm << 20) | (0 << 15) | (0 << 12) | (rd << 7) | 0x13
                self.code_buffer += struct.pack('<I', inst)
        return self.code_buffer

    def execute_or_flash(self, code):
        print(f"RISC-V BIN: {code.hex().upper()}")
