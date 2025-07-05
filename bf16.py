import os, sys, pygame, argparse

from rich.console import Console
from rich.traceback import install as rich_traceback_install
from rich.pretty import install as pretty_install
from rich.panel import Panel
from rich import box

from bf16module.utilities.colors.bf16color import BF16color
from bf16module.utilities.compile.bf16compile import BF16compile
from bf16module.runtime.bf16runtime import BF16Runtime

# === Setup ===
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

rich_traceback_install()
pretty_install()

console = Console()
console.clear()

WINDOW_SIZE = 512
PROGRAM_END = False

def main():
    parser = argparse.ArgumentParser(
        prog="bf16",
        description="BF16 Interpreter and Compiler: Visual Brainfuck game runtime",
        epilog="Examples:\n"
               "  bf16 compile game.b\n"
               "  bf16 run game.b --color rgb332 --showfps\n"
               "  bf16 run demo.bf16c --color grayscale",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compile_parser = subparsers.add_parser("compile", help="Compile a .b source file to .bf16c")
    compile_parser.add_argument("filename")
    compile_parser.add_argument("--use_v2_compile", action="store_true")
    compile_parser.add_argument("--color", default="rgb332")
    compile_parser.add_argument("--appname", default="UNNAMED BF16")
    compile_parser.add_argument("-o", "--output", help="Output filename (default: auto .bf16c)")

    run_parser = subparsers.add_parser("run", help="Run a .b or .bf16c program")
    run_parser.add_argument("filename")
    run_parser.add_argument("--color", default="rgb332")
    run_parser.add_argument("--showfps", action="store_true")

    args = parser.parse_args()

    if args.debug:
        console.print("[bold blue]🛠 Debug mode enabled[/]")
        import logging
        logging.basicConfig(level=logging.DEBUG)

    compiler = BF16compile()
    runtime = BF16Runtime()

    def on_tick_hook():
        if args.debug and not PROGRAM_END:
            tol_memory = 0
            for x in runtime.memory:
                tol_memory += x
            console.log(f"[dim]Tick {runtime.tick} | memory size {tol_memory}[/] ({tol_memory / 1024 / 1024:.2f} MB)")
    
    def on_program_end_hook():
        global PROGRAM_END
        PROGRAM_END = True
        console.log(f"[bold green]✅ Program finished in {runtime.tick} ticks.[/]")

    runtime.register_event("tick", on_tick_hook)
    runtime.register_event("program_end", on_program_end_hook)

    if not os.path.isfile(args.filename):
        console.print(f"[bold red]❌ File not found:[/] {args.filename}")
        return

    if args.command == "compile":
        if not args.filename.endswith(".b"):
            console.print("[bold red]❌ Compile only supports .b files[/]")
            return
        try:
            with open(args.filename, "rb") as f:
                source = f.read()
            compiler.compile(source)
            bin_filename = args.output or args.filename.rsplit(".", 1)[0] + ".bf16c"
            if args.use_v2_compile:
                compiler.write_bin_v2(bin_filename, color_mode=args.color, app_name=args.appname)
            else:
                compiler.write_bin(bin_filename)
            console.print(Panel.fit(
                f"✅ Compiled [bold cyan]{args.filename}[/] → [green]{bin_filename}[/]",
                title="Compile Success", box=box.ROUNDED, style="green"))
        except Exception as e:
            console.print(Panel(str(e), title="💥 Compile Failed", style="red"))
        return

    if args.command == "run":
        try:
            color = getattr(BF16color, args.color.lower())
            if not callable(color):
                raise AttributeError
        except AttributeError:
            available = [m for m in dir(BF16color) if not m.startswith("_")]
            console.print(f"[bold red]❌ Unknown color mode:[/] {args.color}")
            console.print(f"[yellow]Available modes:[/] {', '.join(available)}")
            color = BF16color.rgb332

        pygame.init()
        screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("BF16")
        clock = pygame.time.Clock()
        
        try:
            if args.filename.endswith((".b", ".bf16")):
                console.print(f"🧠 [bold blue]Compiling source[/] '{args.filename}'")
                with open(args.filename, "rb") as f:
                    source = f.read()
                runtime.program = compiler.compile(source)
            elif args.filename.endswith((".bin", ".bf16c")):
                console.print(f"📦 [bold magenta]Loading binary[/] '{args.filename}'")
                if compiler.is_v2_bin(args.filename):
                    runtime.program, color_mode, app_name = compiler.read_bin_v2(args.filename)
                    console.print(f"📘 App: [green]{app_name}[/], Color: [cyan]{color_mode}[/]")
                    pygame.display.set_caption(f"BF16 - {app_name} | v2 compile runtime")
                    try:
                        color = getattr(BF16color, color_mode.lower())
                    except AttributeError:
                        color = BF16color.rgb332
                else:
                    runtime.program = compiler.read_bin(args.filename)
            else:
                console.print(f"[bold red]❌ Unsupported file type:[/] {args.filename}")
                return
        except Exception as e:
            console.print(Panel(str(e), title="💥 Load Error", style="red"))
            return

        runtime.reset()
        running = True
        while running:
            if PROGRAM_END:
                running = False
                break
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            runtime.emit_event("tick")
            runtime.run_program_threaded(screen, color=color)

            if args.showfps:
                runtime.draw_fps(screen, clock)

            runtime.graphic_engine.update()
            clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]👋 Program interrupted by user.[/]")
        sys.exit(0)
    except pygame.error as e:
        console.print(f"[bold red]💥 Pygame error:[/] {e}")
        sys.exit(1)
