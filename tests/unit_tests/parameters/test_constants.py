from i19_bluesky.parameters.constants import EigerConstants


def test_eiger_constants():
    const = EigerConstants()

    assert const.DET_DIST_LUT_PATH.name == "DetDistToBeamXYConverterE4M.txt"
    assert const.DET_SIZE_CONSTANTS.det_size_pixels.width == 2068
    assert const.DET_SIZE_CONSTANTS.det_size_pixels.height == 2162
    assert const.DET_SIZE_CONSTANTS.det_type_string == "EIGER2_X_4M"
