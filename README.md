# GoogleHashCode2019

Sample to solve Hashcode 2019 contest using Python

## Setup
Install libraries

```bash
pip install networkx
```

algo:
graph
compute edges
sort edges by weight (minimum function)
loop:
    collect heavier edge as first segment
    for all extra siblings edges:
        remove if node has 2 visited edge
