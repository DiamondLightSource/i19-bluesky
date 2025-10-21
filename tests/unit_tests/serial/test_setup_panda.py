import pytest
from ophyd_async.fastcs.panda import SeqTrigger

from i19_bluesky.serial.setup_panda import generate_panda_seq_table


async def test_tables_are_same():
    inputs = (5.6, 6.7, 10, 5)
    table_from_func = generate_panda_seq_table(*inputs)

    assert table_from_func.trigger == [SeqTrigger.POSA_GT, SeqTrigger.POSA_LT]
    assert table_from_func.repeats == pytest.approx([10, 10])
    assert table_from_func.position == pytest.approx([5600, 6700])
    assert table_from_func.time1 == pytest.approx([5, 5])
    assert table_from_func.outa1 == pytest.approx([True, True])
