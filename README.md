# python-flatgeobuf

[![PyPI](https://img.shields.io/pypi/v/flatgeobuf.svg)](https://pypi.org/project/flatgeobuf/)
[![build](https://github.com/ozekik/python-flatgeobuf/actions/workflows/ci.yaml/badge.svg)](https://github.com/ozekik/python-flatgeobuf/actions/workflows/ci.yaml)

A Python library for reading [FlatGeobuf](https://flatgeobuf.org/).
Ported from the official [TypeScript implementation](https://github.com/flatgeobuf/flatgeobuf/tree/master/src/ts).

## Features

- Minimal dependencies
- Simple API
- Supports cloud-optimized bounding box filtering
- Works on [JupyterLite](https://github.com/jupyterlite/jupyterlite) ([Pyodide](https://pyodide.org/))

## Installation

```bash
pip install flatgeobuf
```

## Usage

- [Loaders](#loaders)
    - [`load()`](#load)
    - [`load_http()` (Async)](#load_http-async)
- [Readers](#readers)
    - [`Reader`](#reader)
    - [`HTTPReader` (Async)](#httpreader-async)
- [Running on JuptyerLite](#running-on-juptyerlite)

### Loaders

#### `load()`

```python
import flatgeobuf as fgb

# All features
with open("example.fgb", "rb") as f:
    data = fgb.load(f)

# ...or features within a bounding box
with open("example.fgb", "rb") as f:
    data = fgb.load(f, bbox=(-26.5699, 63.1191, -12.1087, 67.0137))

print(data)
# { "type": "FeatureCollection", "features": [...] }
```

#### `load_http()` (Async)

```python
import flatgeobuf as fgb

# All features
data = await fgb.load_http("https://raw.githubusercontent.com/flatgeobuf/flatgeobuf/master/test/data/countries.fgb")

# ...or features within a bounding box
data = await fgb.load_http(
    "https://raw.githubusercontent.com/flatgeobuf/flatgeobuf/master/test/data/countries.fgb",
    bbox=(-26.5699, 63.1191, -12.1087, 67.0137)
)

print(data)
# { "type": "FeatureCollection", "features": [...] }
```

### Readers

#### `Reader`

```python
import flatgeobuf as fgb

# All features
with open("example.fgb", "rb") as f:
    reader = fgb.Reader(f)
    for feature in reader:
        print(feature)
        # { "type": "Feature", "properties": {...}, "geometry": {...} }

# ...or features within a bounding box
with open("example.fgb", "rb") as f:
    reader = fgb.Reader(f, bbox=(-26.5699, 63.1191, -12.1087, 67.0137))
    for feature in reader:
        print(feature)
        # { "type": "Feature", "properties": {...}, "geometry": {...} }
```

#### `HTTPReader` (Async)

```python
import flatgeobuf as fgb

# All features
reader = fgb.HTTPReader("https://raw.githubusercontent.com/flatgeobuf/flatgeobuf/master/test/data/countries.fgb")
  async for feature in reader:
      print(feature)
      # { "type": "Feature", "properties": {...}, "geometry": {...} }

# ...or features within a bounding box
reader = fgb.HTTPReader(
    "https://raw.githubusercontent.com/flatgeobuf/flatgeobuf/master/test/data/countries.fgb",
    bbox=(-26.5699, 63.1191, -12.1087, 67.0137)
)
async for feature in reader:
    print(feature)
    # { "type": "Feature", "properties": {...}, "geometry": {...} }
```

### Running on JuptyerLite

1\. Install `flatgeobuf` on JupyterLite:

```python
%pip install flatgeobuf

# ...or
import micropip
await micropip.install("flatgeobuf")
```

2\. Enable HTTP requests in Pyodide via [`pyodide_http`](https://github.com/koenvo/pyodide-http)

```python
import pyodide_http
pyodide_http.patch_all()
```

3\. Run as usual!

```python
import flatgeobuf as fgb

data = await fgb.load_http(
    "https://raw.githubusercontent.com/flatgeobuf/flatgeobuf/master/test/data/countries.fgb",
    bbox=(-26.5699, 63.1191, -12.1087, 67.0137)
)

print(data)
# { "type": "FeatureCollection", "features": [...] }
```

## Roadmap

- [x] Read FlatGeobuf
  - [ ] Read top-level (`FeatureCollection`) properties
- [ ] Write FlatGeobuf
- [ ] Deploy JuptyerLite examples
- [ ] Rewrite some parts in Rust? (parcked R-tree, geometry intersection)

## License

MIT
