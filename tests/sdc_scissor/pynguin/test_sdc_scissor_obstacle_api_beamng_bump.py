# Automatically generated by Pynguin.
import pytest

import sdc_scissor.obstacle_api.beamng_bump as module_0


def test_case_0():
    beamng_bump_0 = module_0.BeamngBump()
    assert (
        f"{type(beamng_bump_0).__module__}.{type(beamng_bump_0).__qualname__}"
        == "sdc_scissor.obstacle_api.beamng_bump.BeamngBump"
    )
    assert beamng_bump_0.x_pos is None
    assert beamng_bump_0.y_pos is None
    assert beamng_bump_0.z_pos is None
    assert beamng_bump_0.width == 6
    assert beamng_bump_0.length == 2
    assert beamng_bump_0.height == pytest.approx(0.2, abs=0.01, rel=0.01)
    assert beamng_bump_0.upper_length == 1
    assert beamng_bump_0.upper_width == 2
    assert beamng_bump_0.rot is None
    assert beamng_bump_0.rot_quat == (0, 0, 0, 1)
    assert beamng_bump_0.obstacle_type == "procedural"


def test_case_1():
    beamng_bump_0 = module_0.BeamngBump()
    assert (
        f"{type(beamng_bump_0).__module__}.{type(beamng_bump_0).__qualname__}"
        == "sdc_scissor.obstacle_api.beamng_bump.BeamngBump"
    )
    assert beamng_bump_0.x_pos is None
    assert beamng_bump_0.y_pos is None
    assert beamng_bump_0.z_pos is None
    assert beamng_bump_0.width == 6
    assert beamng_bump_0.length == 2
    assert beamng_bump_0.height == pytest.approx(0.2, abs=0.01, rel=0.01)
    assert beamng_bump_0.upper_length == 1
    assert beamng_bump_0.upper_width == 2
    assert beamng_bump_0.rot is None
    assert beamng_bump_0.rot_quat == (0, 0, 0, 1)
    assert beamng_bump_0.obstacle_type == "procedural"
    beamng_bump_1 = module_0.BeamngBump()
    assert beamng_bump_1.x_pos is None
    assert beamng_bump_1.y_pos is None
    assert beamng_bump_1.z_pos is None
    assert beamng_bump_1.width == 6
    assert beamng_bump_1.length == 2
    assert beamng_bump_1.height == pytest.approx(0.2, abs=0.01, rel=0.01)
    assert beamng_bump_1.upper_length == 1
    assert beamng_bump_1.upper_width == 2
    assert beamng_bump_1.rot is None
    assert beamng_bump_1.rot_quat == (0, 0, 0, 1)
    assert beamng_bump_1.obstacle_type == "procedural"
    var_0 = beamng_bump_0.get()
    assert f"{type(var_0).__module__}.{type(var_0).__qualname__}" == "beamngpy.scenario.ProceduralBump"
    assert var_0.id == "pybump"
    assert var_0.name == "pybump"
    assert var_0.type == "ProceduralMesh"
    assert var_0.pos == (None, None, None)
    assert var_0.rot == (0, 0, 0, 1)
    assert var_0.scale == (1, 1, 1)
    assert var_0.opts == {}
    assert var_0.children == []
    assert var_0.material is None
    assert var_0.width == 6
    assert var_0.length == 2
    assert var_0.height == pytest.approx(0.2, abs=0.01, rel=0.01)
    assert var_0.upper_length == 1
    assert var_0.upper_width == 2
    var_1 = beamng_bump_1.get()
    assert var_1.id == "pybump"
    assert var_1.name == "pybump"
