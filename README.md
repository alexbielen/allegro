# Allegro

![](https://github.com/alexbielen/allegro/workflows/CI/badge.svg)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg)](code-of-conduct.md)

Note: Allegro is a work-in-progress and the APIs are unstable.

### Introduction

Allegro is an algorithmic music composition toolbox. It includes utilities that are common when composing
computer music.

### Goals

Allegro aims to explore new types of musical transformation and structure that lead to compelling and rich sonic results. In general, Allegro is interested in complexity science and in particular the musical potential of ["swarmalators"](https://www.complexity-explorables.org/explorables/swarmalators/).

Allegro aims to integrate with other tools in the algorithmic music composition ecosystem. This includes tools for sound synthesis, sheet music engraving, etc.

### Development Setup

Requirements:

- `python 3.8`
- `pyenv 1.2.15`
- `poetry 1.0.0`
- `pyright`

#### pyenv

Allegro uses `pyenv` for python version control. On Mac OS X you can use `brew` to install `pyenv`

```bash
$ brew update
$ brew install pyenv
```

Be sure to add `pyenv init` to your "rc" file. Read more [here.](https://github.com/pyenv/pyenv#basic-github-checkout)

Next, you'll need to install python 3.8 using `pyenv` and set it as your global interpreter.

```bash
$ pyenv install 3.8.0
$ pyenv global 3.8.0
```

#### poetry

Allegro uses `poetry` for dependency management. `poetry` is inspired by similar tools like Rust's `cargo` which generate reproducible builds and implement dependency solvers.

`poetry` requires a special installation process so review the installation documentation [here.](https://github.com/python-poetry/poetry#installation)

Configure `poetry` to create virutalenvs in the project directory and install dependencies.

```bash
$ poetry config virtualenvs.in-project true
$ poetry install
```

#### pyright

Allegro uses Microsoft's `pyright` for static type analysis. Currently Allegro is using the VS Code implementation but this can also be run locally. `pyright` is a Node/TypeScript project so `npm` is required to install.

```
$ sudo npm install -g pyright
$ pyright <options>
```

#### Run Tests

`poetry` is used for dependency management so we need to open a virtual env to run test. This is accomplished with `poetry shell`.

```
$ poetry shell
$ pytest --cov=allegro tests/
```

### Midi Setup

Allegro is currently capable of sending MIDI out messages. Allegro does not have its own synthesizer so a third-party MIDI synth should be used. On MacOSX, SimpleSynth is recommended.

Follow the steps below to test MIDI output:

Open SimpleSynth and select "SimpleSynth virtual input" as the input source.

In a `poetry` shell, run open a Python REPL.

```python
>>> from allegro import midi
>>> ports = midi.get_available_ports() # you should see "SimpleSynth virtual input" listed here.
[MidiPort(port_id=0, port_name='SimpleSynth virtual input')]
>>> m = midi.MidiOut(0)
>>> m.test() # plays a short and random composition.
```
