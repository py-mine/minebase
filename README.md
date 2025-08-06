# <img src="https://i.imgur.com/nPCcxts.png" style="height: 25px"> minebase

[![discord chat](https://img.shields.io/discord/936788458939224094.svg?logo=Discord)](https://discord.gg/C2wX7zduxC)
![supported python versions](https://img.shields.io/pypi/pyversions/minebase.svg)
[![current PyPI version](https://img.shields.io/pypi/v/minebase.svg)](https://pypi.org/project/mcproto/)
[![CI](https://github.com/py-mine/minebase/actions/workflows/main.yml/badge.svg)](https://github.com/py-mine/minebase/actions/workflows/main.yml)
[![Docs](https://github.com/py-mine/minebase/actions/workflows/docs.yml/badge.svg)](https://github.com/py-mine/minebase/actions/workflows/docs.yml)

Minebase is a python wrapper around [`PrismarineJS/minecraft-data`](https://github.com/PrismarineJS/minecraft-data). It
provides python bindings to access minecraft data useful for custom minecraft clients, servers and libraries.

## Installation

From PyPI (stable):

```bash
pip install minebase
```

From repo (latest):

```bash
pip install git+htps://github.com/py-mine/minebase
```

## Usage

```python
from minebase import load_version, load_common_data, Edition

common_data = load_common_data(Edition.PC)
version_info = load_version("1.21.6", Edition.PC)

status_server_bound_packets = version_info["protocol"]["status"]["toServer"]["types"]["packet"]
print(status_server_bound_packets)
```
