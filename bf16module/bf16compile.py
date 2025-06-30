import struct

class bf16compile:
    def __init__(self):
        self.program = []
        self.program_size = 0

    def compile(self, source: bytes) -> list[int]:
        self.program = []
        self.program_size = 0
        bracket_stack = []
        i = 0

        while i < len(source):
            ch = source[i]
            if ch in b'.?,[':
                self.program.append(ch)
                self.program.append(0)
                if ch == ord('['):
                    bracket_stack.append(len(self.program) - 2)
                self.program_size += 2
                i += 1
            elif ch in b'><+-':
                self.program.append(ch)
                count = 1
                j = i + 1
                while j < len(source) and source[j] == ch:
                    count += 1
                    j += 1
                self.program.append(count)
                self.program_size += 2
                i = j
            elif ch == ord(']'):
                self.program.append(ch)
                self.program.append(0)
                if bracket_stack:
                    open_idx = bracket_stack.pop()
                    close_idx = len(self.program) - 2
                    dist = close_idx - open_idx
                    self.program[open_idx + 1] = dist
                    self.program[close_idx + 1] = dist
                else:
                    print('Error: unmatched ] at byte', i)
                self.program_size += 2
                i += 1
            else:
                i += 1  # skip unrecognized characters/comments

        if bracket_stack:
            print('Error: unmatched [ at', bracket_stack)

        return self.program

    def write_bin(self, filename: str):
        with open(filename, 'wb') as out:
            for idx in range(0, self.program_size, 2):
                opcode = self.program[idx]
                arg = self.program[idx + 1]
                out.write(struct.pack('B', opcode))
                out.write(struct.pack('<H', arg))

    def read_bin(self, filename: str):
        self.program = []
        self.program_size = 0
        with open(filename, 'rb') as f:
            while True:
                opcode_byte = f.read(1)
                if not opcode_byte:
                    break
                opcode = struct.unpack('B', opcode_byte)[0]
                arg_bytes = f.read(2)
                if not arg_bytes:
                    break
                arg = struct.unpack('<H', arg_bytes)[0]
                self.program.append(opcode)
                self.program.append(arg)
                self.program_size += 2
        return self.program

    def uncompile(self, filename: str) -> list[int]:
        self.read_bin(filename)  # โหลดโปรแกรมจากไฟล์
    
        result = []
        i = 0
        while i < len(self.program):
            cmd = self.program[i]
            arg = self.program[i + 1]
    
            if cmd in (ord('.'), ord(','), ord('?'), ord('['), ord(']')):
                # คำสั่งเดี่ยว ๆ เก็บ opcode เข้า list
                result.append(cmd)
            elif cmd in (ord('>'), ord('<'), ord('+'), ord('-')):
                # ขยายคำสั่งซ้ำตาม arg แล้วเก็บ opcode ทีละตัว
                result.extend([cmd] * arg)
            else:
                print(f"Warning: Unknown opcode {cmd} encountered during uncompilation.")
            i += 2
    
        return result