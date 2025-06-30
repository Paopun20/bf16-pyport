import pygame
import sys
from itertools import product
from bf16module.bf16compile import bf16compile
from bf16module.bf16color import bf16color
from bf16module.bf16audio import bf16audio
from bf16module.bf16input import bf16input

WINDOW_SIZE = 512
PIXEL_SCALE = WINDOW_SIZE // 16
MEMORY_SIZE = 30000

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
            address += program[cursor]
            cursor += 1
            if address >= MEMORY_SIZE:
                address = MEMORY_SIZE - 1
        elif cmd == ord('<'):
            address -= program[cursor]
            cursor += 1
            if address < 0:
                address = 0
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

def main():
    global program, current_note, cursor, address, memory, tick, last_key_state
    if len(sys.argv) < 3:
        print(f"Usage:")
        print(f"  py bf16 run <filename> color=<color_arg>")
        print(f"  py bf16 compile <filename.b>")
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
        except Exception as e:
            print(f"Failed to open file '{filename}': {e}")
            return
        compiler.compile(source)
        bin_filename = filename.rsplit(".", 1)[0] + ".bin"
        compiler.write_bin(bin_filename)
        print(f"Compiled '{filename}' to '{bin_filename}' successfully.")
        return

    elif command == "run":
        if len(sys.argv) < 4:
            print("Usage: py bf16 run <filename> color=<color_arg> [showfps=0|1]")
            return
    
        filename = sys.argv[2]

        color_arg = None
        showfps_arg = None
    
        for arg in sys.argv[3:]:
            if arg.startswith("color="):
                color_arg = arg.split("=",1)[1].lower()
            elif arg.startswith("showfps="):
                showfps_arg = arg.split("=",1)[1].lower()
    
        if color_arg is None:
            print("Missing color= argument")
            return
    
        show_fps = showfps_arg == "1" or showfps_arg == "true" or showfps_arg == "yes" or showfps_arg == "on" or showfps_arg == "y"

        if color_arg == "rgb332":
            color = bf16color.rgb332
        elif color_arg == "grayscale":
            color = bf16color.grayscale
        elif color_arg == "binary_bw":
            color = bf16color.binary_bw
        elif color_arg == "redscale":
            color = bf16color.redscale
        elif color_arg == "greenscale":
            color = bf16color.greenscale
        elif color_arg == "bluescale":
            color = bf16color.bluescale
        elif color_arg == "rainbow":
            color = bf16color.rainbow
        else:
            print(f"Unknown color mode '{color_arg}', default to rgb332")
            color = bf16color.rgb332

        try:
            if filename.endswith(".b"):
                source = open(filename, "rb").read()
                program = compiler.compile(source)
                compiler.write_bin("program.bin")
            elif filename.endswith(".bin"):
                program = compiler.read_bin(filename)
            else:
                print("Unsupported file type for run command")
                return
        except Exception as e:
            print(f"Failed to open or process file '{filename}': {e}")
            return

    else:
        print(f"Unknown command: {command}")
        return

    # รีเซ็ตสถานะก่อนเริ่ม run
    memory = [0] * MEMORY_SIZE
    cursor = 0
    address = 0
    tick = 0
    current_note = 0
    last_key_state = 0

    # เริ่ม pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("BF16")
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        run_program(screen, color=color)
        draw_fps(screen, clock) if show_fps else None
        pygame.display.flip()

        if memory[address] != current_note:
            current_note = memory[address]
            bf16audio.play_note(current_note)

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        sys.exit(0)
    except pygame.error as e:
        print(f"Pygame error: {e}")
        sys.exit(1)
