# main.py

import os
import sys
import time
import pygame
import argparse
from rich.traceback import install
install()

# --- Setup ---
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from bf16module.utilities.colors.bf16color import bf16color
from bf16module.utilities.compile.bf16compile import bf16compile
from bf16module.runtime.bf16runtime import *

# --- Config ---
WINDOW_SIZE = 512

def main():
    global program

    parser = argparse.ArgumentParser(
        prog="bf16",
        description="BF16 Interpreter and Compiler: Visual Brainfuck game runtime",
        epilog="Examples:\n"
               "  bf16 compile game.b\n"
               "  bf16 run game.b --color rgb332 --showfps\n"
               "  bf16 run demo.bin --color grayscale",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Compile command
    compile_parser = subparsers.add_parser("compile", help="Compile a .b source file to .bin")
    compile_parser.add_argument("filename")
    compile_parser.add_argument("--use_v2_compile", action="store_true")
    compile_parser.add_argument("--color", default="rgb332")
    compile_parser.add_argument("--appname", default="UNNAMED BF16")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a .b or .bin program")
    run_parser.add_argument("filename")
    run_parser.add_argument("--color", default="rgb332")
    run_parser.add_argument("--showfps", action="store_true")

    args = parser.parse_args()
    compiler = bf16compile()

    if args.command == "compile":
        if not args.filename.endswith(".b"):
            print("Error: Compile only supports .b files")
            return
        try:
            source = open(args.filename, "rb").read()
            compiler.compile(source)
            bin_filename = args.filename.rsplit(".", 1)[0] + ".bf16c"
            if args.use_v2_compile:
                compiler.write_bin_v2(bin_filename, color_mode=args.color, app_name=args.appname)
            else:
                compiler.write_bin(bin_filename)
            print(f"Compiled '{args.filename}' to '{bin_filename}' successfully.")
        except Exception as e:
            print(f"Failed to compile '{args.filename}': {e}")
        return

    if args.command == "run":
        try:
            color = getattr(bf16color, args.color.lower())
            if not callable(color):
                raise AttributeError
        except AttributeError:
            print(f"Unknown color mode '{args.color}', defaulting to rgb332.")
            color = bf16color.rgb332

        pygame.init()
        screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("BF16")
        clock = pygame.time.Clock()

        print("Loading...")
        screen.fill((0, 0, 0))
        loading_font = pygame.font.SysFont("Arial", 30)
        loading_text = loading_font.render("Loading...", True, (255, 255, 255))
        screen.blit(loading_text, loading_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2)))
        pygame.display.flip()

        try:
            if args.filename.endswith((".b", ".bf16")):
                print("Compiling and running source file...")
                source = open(args.filename, "rb").read()
                program[:] = compiler.compile(source)
            elif args.filename.endswith((".bin", ".bf16c")):
                print("Running compiled binary file...")
                if compiler.is_v2_bin(args.filename):
                    program[:], color_mode, app_name = compiler.read_bin_v2(args.filename)
                    print(f" - App Name : {app_name}")
                    print(f" - Color    : {color_mode}")
                    try:
                        color = getattr(bf16color, color_mode.lower())
                    except AttributeError:
                        color = bf16color.rgb332
                    pygame.display.set_caption(f"BF16 - {app_name} | v2 compile runtime")
                else:
                    program[:] = compiler.read_bin(args.filename)
            else:
                print("Unsupported file type.")
                return
        except Exception as e:
            print(f"Error loading file '{args.filename}': {e}")
            return

        reset_state()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            run_program_threaded(screen, color=color)

            if args.showfps:
                draw_fps(screen, clock)

            pygame.display.flip()
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
