import struct
import ast

class PyPU_X64:
    def __init__(self, port=None):
        self.code_buffer = bytearray()
        self.regs = {'rax': 0, 'rcx': 1, 'rdx': 2, 'rbx': 3}

    def compile(self, source):
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                reg_name = node.targets[0].id
                val = node.value.n
                self.code_buffer += b'\x48\xC7' 
                self.code_buffer += bytes([0xC0 | self.regs[reg_name]])
                self.code_buffer += struct.pack('<I', val)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                if node.value.func.id == "syscall":
                    self.code_buffer += b'\x0F\x05'
        return self.code_buffer

    def execute_or_flash(self, code):
        print(f"HEX: {code.hex().upper()}")
