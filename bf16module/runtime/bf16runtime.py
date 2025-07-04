# runtime.py

import pygame
import threading
from itertools import product

from bf16module.utilities.sound.bf16audio import bf16audio
from bf16module.utilities.input.bf16input import bf16input

MEMORY_SIZE = 30000
PIXEL_SCALE = 512 // 16

program = []
memory = [0] * MEMORY_SIZE
cursor = 0
address = 0
tick = 0
current_note = 0
last_key_state = 0

def reset_state():
    global memory, cursor, address, tick, current_note, last_key_state
    memory = [0] * MEMORY_SIZE
    cursor = 0
    address = 0
    tick = 0
    current_note = 0
    last_key_state = 0

def run_program(screen: pygame.Surface, color: callable):
    global cursor, address, last_key_state, tick

    while cursor < len(program):
        cmd = program[cursor]
        cursor += 1

        if cmd == ord('>'):
            address += program[cursor]; cursor += 1
            address = min(address, MEMORY_SIZE - 1)
        elif cmd == ord('<'):
            address -= program[cursor]; cursor += 1
            address = max(address, 0)
        elif cmd == ord('+'):
            memory[address] = (memory[address] + program[cursor]) % 256; cursor += 1
        elif cmd == ord('-'):
            memory[address] = (memory[address] - program[cursor]) % 256; cursor += 1
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
            for i, j in product(range(16), repeat=2):
                val = memory[i * 16 + j]
                pygame.draw.rect(screen, color(val), (j * PIXEL_SCALE, i * PIXEL_SCALE, PIXEL_SCALE, PIXEL_SCALE))
            return
        elif cmd == ord(','):
            cursor += 1
            memory[address] = last_key_state = bf16input.get_key_state()
        elif cmd == ord('?'):
            cursor += 1
            print(f"memory[{address}]: {memory[address]}")
        else:
            print(f"Unexpected instruction: '{chr(cmd)}'")

        tick += 1

def run_program_threaded(screen: pygame.Surface, color: callable):
    global current_note, memory, address
    thread = threading.Thread(target=run_program, args=(screen, color))
    thread.start()
    thread.join()
    if memory[address] != current_note:
        current_note = memory[address]
        bf16audio.play_note(current_note)

def draw_fps(screen, clock):
    font = pygame.font.SysFont("Arial", 18)
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255), (0, 0, 0))
    screen.blit(fps_text, (10, 10))
