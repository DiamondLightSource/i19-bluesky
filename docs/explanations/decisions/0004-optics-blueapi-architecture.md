# 4. Optics hutch BlueAPI architecture

## Status

Accepted

## Context

Beamline I19 is made up by two Experimental Hutches in series which use a shared Optics Hutch. This means that both hutches could potentially be trying to control hardware inside the optics hutch at the same time. Very often one hutch may be doing testing while the other one is active for beamtime; thus we need a way to allow for this without disrupting operations eg. by accidentally closing the hutch shutter during data collection.

## Decision

TODO Put this into better words


There is an EHStatus PV which records which hutch is currently in use for beamtime.
Hutch access device reading this PV in i19-optics.

For any device in the optics hutch:
- actual device + plan operating it (decorated with check_access) in i19-optics
- AccessControlledDevice inheriting the OpticsBlueAPIDevice implementation in i19-{1,2}
- This device has a rest call with the plan name and devices to i19-blueapi (optics)
- ch


```{raw} html
:file: ../../images/I19blueapiArchitecture.svg
```


TBD Add diagram with shutter example


### Example of an access controlled device: the experiment shutter

The device in i19-{1,2}-blueapi never uses directly the actual shutter device but implements an access controlled one that makes a rest call to the ``operate_shutter_plan`` in the optics blueapi.

```{raw} html
:file: ../../images/EHDevices.svg
```


The optics blueapi has a plan with uses the real shutter device if access is allowed.

```{raw} html
:file: ../../images/OpticsDevice.svg
```
