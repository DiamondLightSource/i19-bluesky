# 3. i19-bluesky repository structure

## Status

Accepted

## Context

...

## Decision

```
    i19-bluesky/
    |--src/
    |   └-i19_bluesky/
    |       |--eh1/      # Plans only used by EH1, in i19-1-blueapi
    |       |--eh2/      # Plans only used by EH2, in i19-2-blueapi
    |       |--optics/   # Plans to control the optics, in i19-blueapi
    |       |--plans/    # Common plans and utilities
    |       |--serial/   # Common plans for serial crystallography on I19
    |--tests/
    |   |--unit_tests/
    |   |--system_tests/
    └--docs/
```
