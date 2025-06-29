# BF16 - Python Port

A **Python port** of [p2r3's bf16](https://github.com/p2r3/bf16) — The first ever visual Brainfuck runtime built for running interactive games.

---

## Requirements

- **Python** 3.10+
- **Pip packages**:
  ```bash
  pip install pygame numpy
  ```

## Usage

RGB332 color:
```bash
python -m bf16.py examples/snake.b
```
Grayscale color:
```bash
python -m bf16_grayscale.py examples/badapple.b
```