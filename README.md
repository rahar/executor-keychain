# EXECUTOR keychain (1989) emulator

`executor.html` is a single self-contained file: no samples, no dependencies. It is built from `template.html` + `core.js` with `python3 build.py`.

- `core.js`: the chip model (tone divider at f = 32335/N with 1/3 duty, a 15-bit LFSR noise source, the ROM sequences for the 8 sounds, and battery sag) driving the speaker physics (RL voice coil, cone mass-spring, Helmholtz cavity, rear leak, break-up mode, case-panel absorption). It runs at 4x oversampling.
- `render.js`: renders the 8 sounds offline with Node into `out/`. `compare.sh` builds `cmp.png`, the original spectrograms (`seg/`, cut from the Threads video `post.mp4`) next to the synth.
- The analysis scripts (`analyze*.py`, `combW.py`, `noise.py`, `bands.py`) run in `.venv` (numpy/scipy).

Open `executor.html` in any modern browser and press the buttons. Source of the original sounds: [this Threads post](https://www.threads.com/share/__ATMgAT0/). The original video and audio are not included here. How this was built, the instruction given and the coding model are in [PROMPT.md](PROMPT.md).

Measured from the recording: tick K = 32335 Hz (about 129 kHz osc / 4), integer dividers, about 9% oscillator speed-up at each press, decaying over ~0.1 s (battery).
