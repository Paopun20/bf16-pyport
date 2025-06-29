import pygame
import sys
from bf16module.bf16compile import bf16compile
from bf16module.bf16color import bf16color
from bf16module.bf16audio import bf16audio
from bf16module.bf16input import bf16input

# Config
WINDOW_SIZE = 512
PIXEL_SCALE = WINDOW_SIZE // 16
MEMORY_SIZE = 30000

# State
program = []
memory = [0] * MEMORY_SIZE
cursor = 0
address = 0
current_note = 0
last_key_state = 0

def run_program(screen: pygame.Surface):
    global cursor, address, last_key_state

    while cursor < len(program):
        cmd = program[cursor]
        cursor += 1

        if cmd == ord('>'):
            address += program[cursor]; cursor += 1
        elif cmd == ord('<'):
            address -= program[cursor]; cursor += 1
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
            for i in range(16):
                for j in range(16):
                    val = memory[i * 16 + j]
                    pygame.draw.rect(screen, bf16color.grayscale(val), (j * PIXEL_SCALE, i * PIXEL_SCALE, PIXEL_SCALE, PIXEL_SCALE))
            pygame.display.flip()
            return
        elif cmd == ord(','):
            cursor += 1
            memory[address] = bf16input.get_key_state()
            last_key_state = bf16input.get_key_state()
        elif cmd == ord('?'):
            cursor += 1
            print(f"memory[{address}]: {memory[address]}")
        else:
            print(f"Unexpected instruction: '{chr(cmd)}'")

def main():
    global program, current_note
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <filename.b>")
        return

    filename = sys.argv[1]

    # Compile the .b program
    try:
        with open(filename, 'rb') as f:
            source = f.read()
    except Exception as e:
        print(f"Failed to open file '{filename}': {e}")
        return

    compiler = bf16compile()
    program = compiler.compile(source)
    compiler.write_bin("program.bin")

    # Setup Pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("BF16")
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        run_program(screen)

        # Audio
        if memory[address] != current_note:
            current_note = memory[address]
            bf16audio.play_note(current_note)

        print("FPS:", round(clock.get_fps(), 2), flush=True)
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()