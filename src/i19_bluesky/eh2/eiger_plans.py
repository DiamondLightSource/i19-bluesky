import bluesky.plan_stubs as bps
from dodal.devices.eiger import (
    DetectorParams,
    EigerDetector,
    EigerTimeouts,
    InternalEigerTriggerMode,
)

# class DetectorParams(BaseModel):
#     """Holds parameters for the detector. Provides access to a list of Dectris detecto
# r
#     sizes and a converter for distance to beam centre.
#     """

#     # https://github.com/pydantic/pydantic/issues/8379
#     # Must use model_dump(by_alias=True) if serialising!

#     expected_energy_ev: float | None = None
#     exposure_time_s: float
#     directory: str  # : Path https://github.com/DiamondLightSource/dodal/issues/774
#     prefix: str
#     detector_distance: float
#     omega_start: float
#     omega_increment: float
#     num_images_per_trigger: int
#     num_triggers: int
#     use_roi_mode: bool
#     det_dist_to_beam_converter_path: str
#     override_run_number: int | None = Field(default=None, alias="run_number")
#     trigger_mode: TriggerMode = TriggerMode.SET_FRAMES
#     detector_size_constants: DetectorSizeConstants = EIGER2_X_16M_SIZE
#     enable_dev_shm: bool = (
#         False  # Remove in https://github.com/DiamondLightSource/hyperion/issues/1395
#     )


def setup_eiger(detector_params: DetectorParams, eiger: EigerDetector):
    eiger.set_detector_parameters(detector_params)
    eiger.do_arming_chain()
    eiger.odin.check_and_wait_for_odin_state(timeout=EigerTimeouts)
    # make sure is actually 'ready'


def run_eiger(detector_params: DetectorParams, eiger: EigerDetector):
    # TODO make sure the manual trigger is set
    match detector_params.trigger_mode:
        case InternalEigerTriggerMode.INTERNAL_SERIES:
            # make sure we only do this when manual is on, and then, when manual is trig
            # gered
            yield from bps.trigger(eiger.drv.detector.arm)
            # is this even the right trigger?
        case InternalEigerTriggerMode.EXTERNAL_SERIES:
            # make sure this only works when recieving a TTL signal from Panda
            yield from bps.trigger(eiger.drv.detector.arm)

            # extra stuff - frame_count = exp images * num_images
            # "rising edge" stuff


# Exp: 0.2
# Period: 0.2
# # Exp/Image: 1
# # images: 20
# Image mode: multiple
# Trigger mode: Internal Series
# Ancillary Data: Manual trigger to Yes
#     Change Odin file directory:  caput -S BL19I-EA-EIGER-01:OD:FilePath /dls/i19-2/dat
# a/2026/cm44169-2/eiger_testing/test3/
#     Change file name:  caput -S BL19I-EA-EIGER-01:OD:FileName test3
#     Odin Frame count:  20 (match to number set in Eiger TOP)
#     Odin Start (caput BL19I-EA-EIGER-01:OD:Capture 1)

# generate files ready for collection: test3_000001.h5  test3_meta.h5
# 5. Eiger Top: Start (caput BL19I-EA-EIGER-01:CAM:Acquire 1)
# waiting for manual trigger
# 6. Eiger Top → Ancillary Data: Trigger
# will take 4 s to collect (0.2 x 20)
# can see image current acquisition increase
