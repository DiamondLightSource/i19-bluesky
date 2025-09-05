import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.i19.pin_col_stages import (
    CollimatorStage,
    PinColControl,
    PinColRequest,
    PinholeStage,
)

from i19_bluesky.log import LOGGER


def move_pin_col_out_of_beam(
    pincol: PinColControl, group: str = "pincol_out", wait: bool = True
) -> MsgGenerator:
    pinx_out = yield from bps.rd(pincol.config.pin_x_out)
    colx_out = yield from bps.rd(pincol.config.col_x_out)

    # TODO check is move can be used, as long as it moves motors in the right order
    LOGGER.info(f"Moving colx to out position {colx_out}")
    yield from bps.mv(pincol.collimator.x, colx_out, group=group)
    LOGGER.info(f"Moving pinx to out position {pinx_out}")
    yield from bps.mv(pincol.pinhole.x, pinx_out, group=group)

    if wait:
        yield from bps.wait(group=group)


def move_pinhole_motors_to_in_position(
    pinhole: PinholeStage,
    request: dict[str, float],
) -> MsgGenerator:
    LOGGER.info(f"Moving pinhole stage to positions {request}")
    yield from bps.abs_set(pinhole, request)


def move_collimator_motors_to_out_position(
    collimator: CollimatorStage, request: dict[str, float]
) -> MsgGenerator:
    LOGGER.info(f"Move collimator stage to positions {request}")
    yield from bps.abs_set(collimator, request)


def move_pin_col_to_requested_in_position(
    pincol: PinColControl,
    requested_aperture: PinColRequest,
) -> MsgGenerator:
    if requested_aperture in [PinColRequest.PINOUT, PinColRequest.COLOUT]:
        raise ValueError(
            """To move the pinhole and colliator stages out.
            Please use the `move_pin_col_out_of_beam` plan."""
        )
    pinhole_pos = yield from pincol.get_pinhole_motor_positions_for_requested_aperture(
        requested_aperture
    )
    collimator_pos = yield from pincol.get_collimator_motor_positions_for_requested_aperture(  # noqa E501
        requested_aperture
    )

    yield from move_pinhole_motors_to_in_position(pincol.pinhole, pinhole_pos)
    yield from move_collimator_motors_to_out_position(pincol.collimator, collimator_pos)
