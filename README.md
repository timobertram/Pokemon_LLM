# VGC AI Framework 2 1.0.4

[[_TOC_]]

## Installation

To use a clone of this project, install the dependencies using requirements.txt:

```
git clone https://gitlab.com/DracoStriker/pokemon-vgc-engine.git
cd pokemon-vgc-engine
pip install -r requirements.txt
```

To install vgc2 in your venv:

```
git clone https://gitlab.com/DracoStriker/pokemon-vgc-engine.git
cd pokemon-vgc-engine
pip install .
```

## Project Structure

* `/organization` contains multiple entry points to run the multiple tracks of the VGC AI Competition.

* `/template` contains a base schema to build a VGC AI Competitor.

* `/tutorial` contains multiple examples on how to use this framework.

* `/vgc2` module is the core implementation of the VGC AI Framework 2.

* `/visual_server` Godot Game Engine project with a visual server for battling simulations.

## Documentation

The full documentation from API, Framework architecture to the Competition Tracks and
Rules can be found in the [Wiki](https://gitlab.com/DracoStriker/pokemon-vgc-engine/-/wikis/home).

## Citation

The technical document can be found in the following link:

https://ieeexplore.ieee.org/document/9618985

Please cite this work if used.

```
@INPROCEEDINGS{9618985,

  author={Reis, Simão and Reis, Luís Paulo and Lau, Nuno},

  booktitle={2021 IEEE Conference on Games (CoG)}, 

  title={VGC AI Competition - A New Model of Meta-Game Balance AI Competition}, 

  year={2021},

  volume={},

  number={},

  pages={01-08},

  doi={10.1109/CoG52621.2021.9618985}}
```