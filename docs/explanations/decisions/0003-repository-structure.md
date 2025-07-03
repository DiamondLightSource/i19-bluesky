# 3. i19-bluesky repository structure

## Status

Accepted

## Context

The two experiment hutches (EH) on I19 have completely separates hardware and collection/setup routines, meaning they need their own modules.
Additionally, the optics hutch is common to the two hutches and use of it needs to be safe guarded against interference between EH1 and EH2. Specific code to control the optics and check that only the active hutch is using it should have its own module.

## Decision

We should stick to a structure that clearly separates the plans for each of the experiment hutches and the optics hutch on the beamline.


```
    i19-bluesky/
    |--src/
    |   └-i19_bluesky/
    |       |--eh1/      # Plans only used by EH1, in i19-1-blueapi
    |       |--eh2/      # Plans only used by EH2, in i19-2-blueapi
    |       |--optics/   # Plans to control the optics, in i19-blueapi
    |       |--plans/    # Common plans to the EHs and utilities
    |       |--serial/   # Common plans specific to serial crystallography on I19
    |--tests/
    |   |--unit_tests/
    |   |--system_tests/
    └--docs/
```

Plans that we want included in blueapi should be in the relevant hutch module:
    - i19-1-blueapi looks for plans in `i19_bluesky.eh1`
    - i19-2-blueapi looks for plans in `i19_bluesky.eh2`
    - i19-blueapi (optics) looks for plans in `i19_bluesky.optics`

Code from a specific EH may import from `i19_bluesky.plans` or `i19_bluesky.serial` in order to make it available to blueapi.
Under any circumstances should the experiment hutches import plans directly from the optics hutch module, or from each other's modules. This should be enforced in CI.
