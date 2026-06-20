from cad_rigor_tripwire import evaluate


def test_fires_on_printed_without_version():
    assert evaluate("the part is printed, check the fit") is not None


def test_silent_when_version_present():
    assert evaluate("v15 is printed, check the fit") is None


def test_fires_on_rotate_the_part_without_version():
    assert evaluate("rotate the part up") is not None


def test_escape_suffix_suppresses():
    assert evaluate("how do mounts handle airflow ~loose") is None


def test_escape_prefix_suppresses():
    assert evaluate("[general] rotate concepts in CAD") is None


def test_silent_on_unrelated_prompt():
    assert evaluate("what time is it") is None


def test_silent_on_empty():
    assert evaluate("") is None


def test_fires_on_move_it_up():
    assert evaluate("move it up") is not None


def test_fires_on_position_without_version():
    assert evaluate("position the bracket against the wall") is not None
