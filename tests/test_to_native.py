import json
import os

from gxformat2._scripts import ensure_format2_from_path
from gxformat2._yaml import ordered_dump
from gxformat2.converter import main
from gxformat2.lint import lint_ga_path
from gxformat2.linting import LintContext
from ._helpers import TEST_PATH, to_example_path
from .example_wfs import (
    INT_INPUT,
)

EXAMPLES_DIR_NAME = "native"


def test_double_convert_sars_wf():
    sars_example = os.path.join(TEST_PATH, "sars-cov-2-variant-calling.ga")
    workflow_dict = ensure_format2_from_path(sars_example)
    format2_path = to_example_path(sars_example, EXAMPLES_DIR_NAME, "gxwf.yml")
    with open(format2_path, "w") as f:
        ordered_dump(workflow_dict, f)

    out = _run_example_path(format2_path)
    lint_context = LintContext()
    lint_ga_path(lint_context, out)


def test_int_input():
    format2_path = to_example_path("int_example", EXAMPLES_DIR_NAME, "gxwf.yml")
    with open(format2_path, "w") as f:
        f.write(INT_INPUT)
    out = _run_example_path(format2_path)
    with open(out, "r") as f:
        as_native = json.load(f)

    int_step = as_native["steps"]["1"]
    assert int_step["type"] == "parameter_input"
    assert json.loads(int_step["tool_state"])["parameter_type"] == "integer"


def _run_example_path(path):
    out = _examples_path_for(path)
    main(argv=[path, out])
    return out


def _examples_path_for(workflow_path):
    return to_example_path(workflow_path, EXAMPLES_DIR_NAME, "ga")
