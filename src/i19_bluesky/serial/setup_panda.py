from ophyd_async.fastcs.panda._table import SeqTable, SeqTrigger


def generate_panda_seq_table(
    phi_start: float,
    phi_end: float,
    phi_steps: int,  # no. of images to take
    time_between_images: int,
) -> SeqTable:
    rows = SeqTable()  # type: ignore

    rows += SeqTable.row(
        trigger=SeqTrigger.POSA_GT,
        position=int(phi_start),
        repeats=phi_steps,
        time1=time_between_images,
        outa1=True,
    )

    rows += SeqTable.row(
        trigger=SeqTrigger.POSA_LT,
        position=int(phi_end),
        repeats=phi_steps,
        time1=time_between_images,
        outa1=True,
    )

    return rows
