from ophyd_async.fastcs.eiger import EigerDetector

# from dodal.devices.eiger import EigerDetector


# wavelength in A
# detector distance in m
# beam center x,y position

# 2 theta axis position

# omega, kappa positions
# phi and phi increment
# kappa increment, omega increment, chi, chi increment (all to 0)

# below is what i am reading from - no two_theta?
# class EigerDetectorIO(Device):
#     bit_depth_image: SignalR[int]
#     state: SignalR[str]
#     count_time: SignalRW[float]
#     frame_time: SignalRW[float]
#     nimages: SignalRW[int]
#     ntrigger: SignalRW[int]
#     nexpi: SignalRW[int] | None
#     trigger_mode: SignalRW[str]
#     roi_mode: SignalRW[str]
#     photon_energy: SignalRW[float]
#     beam_center_x: SignalRW[float]
#     beam_center_y: SignalRW[float]
#     detector_distance: SignalRW[float]
#     omega_start: SignalRW[float]
#     omega_increment: SignalRW[float]
#     arm: SignalX
#     disarm: SignalX
#     trigger: SignalX


# can't find kappa position or two-theta - will ask noemi when she is in
async def read_metadata_from_eiger(eiger: EigerDetector):
    energy = await eiger.drv.detector.photon_energy.get_value()
    wavelength = 12398.4193 / energy
    detector_distance = await eiger.drv.detector.detector_distance.get_value()
    beam_centre_x = await eiger.drv.detector.beam_center_x.get_value()
    beam_centre_y = await eiger.drv.detector.beam_center_y.get_value()
    omega_position = await eiger.drv.detector.omega_start.get_value()
    omega_increment, chi, chi_increment, kappa_increment, omega_position = 0, 0, 0, 0, 0
    return {
        "Wavelength": wavelength,
        "detector_distance": detector_distance,
        "beam_centre_x": beam_centre_x,
        "beam_centre_y": beam_centre_y,
        "omega_position": omega_position,
        "omega_increment": omega_increment,
        "chi": chi,
        "chi_increment": chi_increment,
        "kappa_increment": kappa_increment,
    }
