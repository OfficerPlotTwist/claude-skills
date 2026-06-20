from cad_rigor_session_start import build_context, looks_like_cad_dir


def test_context_mentions_skill_and_rigor():
    ctx = build_context()
    assert "cad-reference-rigor" in ctx
    assert "hard-stop" in ctx.lower()


def test_looks_like_cad_dir_true_for_cad_markers(tmp_path):
    (tmp_path / "part.scad").write_text("// scad", encoding="utf-8")
    assert looks_like_cad_dir(str(tmp_path)) is True


def test_looks_like_cad_dir_true_for_step(tmp_path):
    (tmp_path / "widget.step").write_text("ISO-10303", encoding="utf-8")
    assert looks_like_cad_dir(str(tmp_path)) is True


def test_looks_like_cad_dir_false_for_plain_dir(tmp_path):
    (tmp_path / "notes.txt").write_text("hi", encoding="utf-8")
    assert looks_like_cad_dir(str(tmp_path)) is False
