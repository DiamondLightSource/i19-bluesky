# 3. Optics hutch BlueAPI architecture

## Status

Accepted

## Context

Beamline I19 is made up by two Experimental Hutches in series which use a shared Optics Hutch. This means that both hutches could potentially be trying to control hardware inside the optics hutch at the same time. Very often one hutch may be doing testing while the other one is active for beamtime; thus we need a way to allow for this without disrupting operations eg. by accidentally closing the hutch shutter during data collection.

## Decision

There is an EHStatus PV which records which hutch is currently in use for beamtime.
