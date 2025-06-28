import math
import struct
import pygame
import numpy as np

WINDOW_SIZE = 512
PIXEL_SCALE = WINDOW_SIZE // 16
SAMPLE_RATE = 48000
AMPLITUDE = 28000
current_note = 0

pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, 512)
pygame.init()

def play_note(pitch):
    freq = 440.0 * (2.0 ** ((pitch - 69.0) / 12.0))
    duration = 0.166  # ประมาณ 166ms
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples, False)
    envelope = np.ones(samples)
    attack = int(SAMPLE_RATE * 0.02)
    release = int(SAMPLE_RATE * 0.02)
    envelope[:attack] = np.linspace(0, 1, attack)
    envelope[-release:] = np.linspace(1, 0, release)
    wave = AMPLITUDE * envelope * np.sin(2 * np.pi * freq * t)
    audio = wave.astype(np.int16)
    if len(audio.shape) == 1:
        audio = np.column_stack((audio, audio))  # make stereo
    sound = pygame.sndarray.make_sound(audio)
    sound.play()

program = []
memory = [0] * 30000
program_size = 0
cursor = 0
address = 0
last_key_state = 0

def run_program(screen):
    global cursor, address, last_key_state
    while cursor < program_size:
        cmd = program[cursor]
        cursor += 1
        if cmd == ord('>'):
            address += program[cursor]
            cursor += 1
        elif cmd == ord('<'):
            address -= program[cursor]
            cursor += 1
        elif cmd == ord('+'):
            memory[address] = (memory[address] + program[cursor]) % 256
            cursor += 1
        elif cmd == ord('-'):
            memory[address] = (memory[address] - program[cursor]) % 256
            cursor += 1
        elif cmd == ord('['):
            if memory[address] == 0:
                cursor += program[cursor]
            cursor += 1
        elif cmd == ord(']'):
            if memory[address] != 0:
                cursor -= program[cursor]
            cursor += 1
        elif cmd == ord('.'):
            cursor += 1
            for i in range(16):
                for j in range(16):
                    val = memory[i*16 + j]
                    r = ((val >> 5) & 0x07) * 255 // 7
                    g = ((val >> 2) & 0x07) * 255 // 7
                    b = (val & 0x03) * 255 // 3
                    color = (r, g, b)
                    pygame.draw.rect(screen, color, (j*PIXEL_SCALE, i*PIXEL_SCALE, PIXEL_SCALE, PIXEL_SCALE))
            pygame.display.flip()
            return
        elif cmd == ord(','):
            cursor += 1
            pygame.event.pump()
            keys = pygame.key.get_pressed()
            key = 0
            if keys[pygame.K_z]: key |= 0x80
            if keys[pygame.K_x]: key |= 0x40
            if keys[pygame.K_RETURN]: key |= 0x20
            if keys[pygame.K_SPACE]: key |= 0x10
            if keys[pygame.K_UP]: key |= 0x08
            if keys[pygame.K_DOWN]: key |= 0x04
            if keys[pygame.K_LEFT]: key |= 0x02
            if keys[pygame.K_RIGHT]: key |= 0x01
            memory[address] = key
            last_key_state = key
        elif cmd == ord('?'):
            cursor += 1
            print(f"memory[{address}]: {memory[address]}")
        else:
            print(f"unexpected char '{chr(cmd)}'")

def is_bf_char(a):
    return a in b'> < + - [ ] . , ?'

def main():
    import sys
    global program_size, current_note
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <filename>")
        return 1
    filename = sys.argv[1]
    try:
        with open(filename, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"Failed to open file: {filename}")
        return 1
    i = 0
    bracket_stack = []
    while i < len(data):
        ch = data[i]
        if ch in b'.?,[':
            program.append(ch)
            program.append(0)
            if ch == ord('['):
                bracket_stack.append(len(program) - 2)
            program_size += 2
            i += 1
        elif ch in b'><+-':
            program.append(ch)
            count = 1
            j = i + 1
            while j < len(data) and data[j] == ch:
                count += 1
                j += 1
            program.append(count)
            program_size += 2
            i = j
        elif ch == ord(']'):
            program.append(ch)
            program.append(0)
            if bracket_stack:
                open_idx = bracket_stack.pop()
                close_idx = len(program) - 2
                dist = close_idx - open_idx
                program[open_idx + 1] = dist
                program[close_idx + 1] = dist
            else:
                print('Error: unmatched ] at', i)
            program_size += 2
            i += 1
        else:
            i += 1
    if bracket_stack:
        print('Error: unmatched [ at', bracket_stack)
    with open('program.bin', 'wb') as out:
        for idx in range(0, program_size, 2):
            opcode = program[idx]
            arg = program[idx + 1]
            if not (0 <= opcode <= 255):
                print(f'Warning: opcode out of range at idx {idx}: {opcode}')
                opcode = 0
            out.write(struct.pack('B', opcode))
            out.write(struct.pack('<H', arg if 0 <= arg <= 65535 else 0))
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption('bf16')
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        run_program(screen)
        if memory[address] != current_note:
            current_note = memory[address]
            play_note(current_note)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == '__main__':
    main() 