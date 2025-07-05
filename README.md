🚀 BF16 - Python Compiler  
🎮 Visual Brainfuck Runtime Engine

----------------------------------------

🔧 Requirements

🐍 Python 3.10 or later  
📦 Install dependencies:
    pip install -r requirements.txt

----------------------------------------

⚙️ Usage

🎨 RGB332 Mode:
    python bf16.py run examples/snake.b --color rgb332

🕶️ Grayscale Mode:
    python bf16.py run examples/badapple.b --color grayscale

----------------------------------------

🛠️ Compile BF16 Program

Convert `.b` source to `.bf16c` bytecode:
    python bf16.py compile examples/hello.b -o hello.bf16c --color rgb332 --appname "Hello App"

----------------------------------------

🧮 Launch Calculator
    python bf16.py --calc

----------------------------------------

💡 Notes

.b = raw Brainfuck source  
.bf16c = compiled bytecode (v1/v2 supported)  
Supports color modes, event hooks, and audio output