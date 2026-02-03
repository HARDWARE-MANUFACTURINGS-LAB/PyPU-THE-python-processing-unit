import struct
import ast

class PyPU_X86:
    def __init__(self, port=None):
        self.code_buffer = bytearray()
        self.regs = {'eax': 0, 'ecx': 1, 'edx': 2, 'ebx': 3}

    def compile(self, source):
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                reg_name = node.targets[0].id
                val = node.value.n
                self.code_buffer += b'\xB8' if reg_name == 'eax' else bytes([0xB8 + self.regs[reg_name]])
                self.code_buffer += struct.pack('<I', val)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                if node.value.func.id == "syscall":
                    self.code_buffer += b'\xCD\x80'
        return self.code_buffer

    def execute_or_flash(self, code):
        print(f"x86 HEX: {code.hex().upper()}")
