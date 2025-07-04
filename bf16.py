# --- Standard Library ---
import os
import sys
import time
import threading
from itertools import product
import a

# --- Environment Setup ---
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"  # Hide "Hello from the pygame community"

# --- Third-Party Modules ---
import pygame

# --- Local Modules ---
from bf16module.utilities.compile.bf16compile import bf16compile
from bf16module.utilities.colors.bf16color import bf16color
from bf16module.utilities.sound.bf16audio import bf16audio
from bf16module.utilities.input.bf16input import bf16input

# --- Config ---
WINDOW_SIZE = 512
PIXEL_SCALE = WINDOW_SIZE // 16
MEMORY_SIZE = 30000

# --- State ---
program = []
memory = [0] * MEMORY_SIZE
cursor = 0
address = 0
tick = 0
current_note = 0
last_key_state = 0

def run_program(screen: pygame.Surface, color: callable = bf16color.rgb332):
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

def draw_fps(screen, clock):
    font = pygame.font.SysFont("Arial", 18)
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255), (0, 0, 0))
    screen.blit(fps_text, (10, 10))

def run_program_threaded(screen: pygame.Surface, color: callable):
    thread = threading.Thread(target=run_program, args=(screen, color))
    thread.start()
    while thread.is_alive():
        pass

def main():
    global program, current_note, cursor, address, memory, tick, last_key_state

    if len(sys.argv) < 3:
        print("Usage:")
        print("  py bf16 run <filename> color=<color_arg> [showfps=1] [record=1]")
        print("  py bf16 compile <filename.b> or <filename.bf16>")
        return

    command = sys.argv[1].lower()
    filename = sys.argv[2]
    compiler = bf16compile()

    if command == "compile":
        if not filename.endswith(".b"):
            print("Compile only supports .b files")
            return
        try:
            source = open(filename, "rb").read()
            compiler.compile(source)
            bin_filename = filename.rsplit(".", 1)[0] + ".bin"
            compiler.write_bin(bin_filename)
            print(f"Compiled '{filename}' to '{bin_filename}' successfully.")
        except Exception as e:
            print(f"Failed to compile '{filename}': {e}")
        return

    elif command == "run":
        color_arg = None
        showfps_arg = "0"

        for arg in sys.argv[3:]:
            if arg.startswith("color="):
                color_arg = arg[6:].lower()
            elif arg.startswith("showfps="):
                showfps_arg = arg[8:].lower()

        if not color_arg:
            print("Missing color= argument")
            return

        show_fps = showfps_arg in ["1", "true", "yes", "on", "y"]

        # Select color mode
        try:
            color = getattr(bf16color, color_arg)
            if not callable(color):
                raise AttributeError
        except AttributeError:
            print(f"Unknown color mode '{color_arg}', defaulting to rgb332.")
            color = bf16color.rgb332

        try:
            if filename.endswith((".b", ".bf16")):
                print("Compiling and running source file...")
                source = open(filename, "rb").read()
                program = compiler.compile(source)
            elif filename.endswith((".bin", ".bf16c")):
                print("Running compiled binary file...")
                program = compiler.read_bin(filename)
            else:
                print("Unsupported file type for run command.")
                return
        except Exception as e:
            print(f"Error loading file '{filename}': {e}")
            return

        # --- Run Pygame ---
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("BF16")
        clock = pygame.time.Clock()

        # Reset state
        memory = [0] * MEMORY_SIZE
        cursor = 0
        address = 0
        tick = 0
        current_note = 0
        last_key_state = 0
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            run_program_threaded(screen, color=color)

            if show_fps:
                draw_fps(screen, clock)

            pygame.display.flip()

            if memory[address] != current_note:
                current_note = memory[address]
                bf16audio.play_note(current_note)

            clock.tick(60)

        pygame.quit()

    else:
        print(f"Unknown command: {command}")
        return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        sys.exit(0)
    except pygame.error as e:
        print(f"Pygame error: {e}")
        sys.exit(1)
