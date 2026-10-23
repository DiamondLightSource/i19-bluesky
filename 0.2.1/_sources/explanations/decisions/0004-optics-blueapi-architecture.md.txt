# 4. Optics hutch BlueAPI architecture

## Status

Accepted

## Context

Beamline I19 is made up by two Experimental Hutches in series which use a shared Optics Hutch. This means that both hutches could potentially be trying to control hardware inside the optics hutch at the same time. Very often one hutch may be doing testing while the other one is active for beamtime; thus we need a way to allow for this without disrupting operations eg. by accidentally closing the hutch shutter during data collection.

## Decision

On I19 each experimental hutch has its own control machine, activeMQ instance and GDA deployment. It follows that each hutch should have its own blueapi instance running on the i19 cluster, with ad-hoc plans and devices. However, the optics hutch is shared and the hardware can be controlled by both hutches, which needs to be considered when writing plans. In order to be able to control the access to the devices in the optics, a third blueAPI has been set up to run on the cluster.

For all hardware in the shared optics hutch, the architecture should follow this structure:

- There is an ``OpticsBlueAPIDevice`` in dodal that can send a REST call to the optics blueapi with the plan name and devices. The optics devices defined in ``i19-1-blueapi`` and ``i19-2-blueapi`` inherit from this device and set up the request parameters for the rest call. The actual devices for the optics should never be called directly by the single EH.

- The optics blueapi instance has a ``HutchAccessControl`` device that reads the EHStatus PV, which records which hutch is currently in use for beamtime. Every plan in the optics blueapi should be wrapped with the ``@check_access`` decorator defined in ``i19_bluesky.optics`` which checks the EHStatus PV against the EH making the request and only allows the plan to run if the values match.



```{raw} html
:file: ../../images/I19blueapiArchitectureSmall.svg
```



### Example of an access controlled device: the experiment shutter

The device in i19-{1,2}-blueapi never uses directly the actual shutter device but implements an access controlled one that makes a rest call to the ``operate_shutter_plan`` in the optics blueapi.

```{raw} html
:file: ../../images/EHDevices.svg
```


The optics blueapi has a plan with uses the real shutter device if access is allowed.

```{raw} html
:file: ../../images/OpticsDevice.svg
```
