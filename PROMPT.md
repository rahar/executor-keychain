# How this was made

## Coding model

- **Model:** Claude Opus 5.5 (`claude-opus-5-5`, Anthropic), effort setting "high"
- **Harness:** [Nodecode](https://nodecode.ai), running as a Telegram bot on a Linux server, with shell access and a headless/real Chromium on a Raspberry Pi for fetching the video and checking the page plays
- **Human input:** the single instruction below. No hand-written code.

## Instruction given

Verbatim, as sent in Telegram:

> Create a purely html version of this toy that would simulate the sounds as closely as possible https://www.threads.com/share/__ATMgAT0/
> Research what achip actually was used and lets simulate the physics and get it doing the sounds precisely:)

Follow-up instruction, which produced this repository:

> Upload this to github from rahar account personal one, make it public, add the instructions used to create this and coding model in separate file in the repo.

## What the model did with it

1. Downloaded the video from the Threads post and extracted its audio (`post.wav`, not included in this repo).
2. Researched the chip. Toys like this use an unmarked chip-on-board blob with no part number, so the exact die can't be identified; the behaviour matches the Holtek HT2884 family of sound-effect ICs ([datasheet](https://www.metronix.cz/ht2884.pdf)), and that family was modelled.
3. Cut the recording into the 8 sounds and measured them (`analyze*.py`, `seg1.py`, `combN.py`, `combW*.py`, `noise.py`): a tone clock of about 32,335 Hz with integer dividers, 1/3 duty square wave, LFSR noise, and a ~9% oscillator speed-up at each press that decays over ~0.1 s (coin-cell sag).
4. Fitted a speaker/enclosure model to the recording's spectrum (`fitspk.py`, `fitmodal.py`, `speaker_fit.json`, `resp.npy`): voice-coil RL, cone mass-spring, Helmholtz cavity, rear leak, cone break-up mode and case-panel absorption.
5. Wrote the engine (`core.js`) and the page (`template.html`), joined by `build.py` into the single file `executor.html`.
6. Rendered the 8 sounds offline with Node (`render.js` -> `out/`) and compared spectrograms with the original (`compare.sh`, `bands.py` -> `cmp.png`, `cmp/`). Result: within about +-4 dB between 0.5 and 6 kHz.
7. Loaded the page in a real browser to check that the audio engine starts.
