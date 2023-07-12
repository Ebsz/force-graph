# force-graph 
Simple library for force-directed graph drawing in Python, using pygame as backend.

![graph](https://i.imgur.com/qb3fADk.png)

## Installation
Clone the repo, then run
```
pip install .
```
in the root directory.

## Minimal example
```python
N = 3
edges = [(0,1), (1,2), (2,0)]

GraphWindow.(N, edges).loop()
```

More examples can be found under `examples/`

## Keybinds
* __P__: pause simulation
* __R__: restart simulation
* __Q__: exit
* __G__: toggle gravity (default: disabled)
* __K__: zoom in
* __J__: zoom out
