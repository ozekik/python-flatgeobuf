# python-flatgeobuf

A Python library for [FlatGeobuf](https://flatgeobuf.org/).
Ported from the official [TypeScript implementation](https://github.com/flatgeobuf/flatgeobuf/tree/master/src/ts).

## Installation

```bash
pip install flatgeobuf
```

## Usage

```python
import flatgeobuf as fgb

with open('example.fgb', 'rb') as f:
    data = fgb.load(f)
    print(data)
    # { "type": "FeatureCollection", "features": [...] }
```

```python
import flatgeobuf as fgb

data = fgb.load("https://raw.githubusercontent.com/flatgeobuf/flatgeobuf/master/test/data/countries.fgb")
print(data)
```

## Roadmap

- [x] Read FlatGeobuf
  - [ ] Read top-level (`FeatureCollection`) properties
- [ ] Write FlatGeobuf
- [ ] Rewrite some parts in Rust (parcked R-tree, geometry intersection)
