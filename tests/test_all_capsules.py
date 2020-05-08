from pathlib import Path
from typing import List

import pytest

from vcap.testing import perform_capsule_tests

# Retrieve all of the capsule paths in a pytest parametrize friendly way
capsules_dir = Path("capsules")
capsule_paths = sorted([str(unpacked_capsule)
                        for unpacked_capsule in Path(capsules_dir).iterdir()
                        if unpacked_capsule.is_dir()])
capsule_paths_argvals = [(Path(path),) for path in capsule_paths]


@pytest.mark.parametrize(
    argnames=["unpackaged_capsule_dir"],
    argvalues=capsule_paths_argvals,
    ids=capsule_paths)
def test_capsules(unpackaged_capsule_dir: Path):
    """Test each capsules using the vcap provided test utilities."""

    image_paths = list(Path("tests/test_resources").glob("*"))
    perform_capsule_tests(
        unpackaged_capsule_dir=unpackaged_capsule_dir,
        image_paths=image_paths)


@pytest.mark.parametrize(
    argnames=["unpackaged_capsule_dir"],
    argvalues=capsule_paths_argvals,
    ids=capsule_paths)
def test_capsules_licensing(unpackaged_capsule_dir: Path):
    """Test that each capsule has a licenses/ directory, and at least has a
    code.LICENSE file. To catch mistakes, it also checks if there are common
    model formats (*.pb, *.bin, *.tflite) and requires that a model.LICENSE
    be included in the capsule as well.

    If we encounter a capsule that uses these file extensions but doesn't
    actually need them, we can whitelist it."""

    # Verify a licenses directory exists
    licenses_dir = unpackaged_capsule_dir / "licenses"
    assert licenses_dir.is_dir()

    # Verify there is a code license
    code_license = licenses_dir / "code.LICENSE"
    assert code_license.is_file()

    # Check if there are model files and verify there is a model license file
    filetypes = ("*.pb", "*.tflite", "*.bin", "*.h5")
    globs = [list(unpackaged_capsule_dir.glob(ftype)) for ftype in filetypes]
    model_files = sum(globs, [])
    if len(model_files):
        model_license = licenses_dir / "model.LICENSE"
        assert model_license.is_file()

