"""Test exporting Galaxy workflow to abstract CWL syntax."""
from cwltool.context import (
    getdefault,
    LoadingContext,
)
from cwltool.main import (
    default_loader,
    fetch_document,
    resolve_and_validate_document,
    tool_resolver,
)

from gxformat2._yaml import ordered_dump, ordered_load
from gxformat2.abstract import CWL_VERSION, from_dict
from .example_wfs import (
    BASIC_WORKFLOW,
    NESTED_WORKFLOW,
    OPTIONAL_INPUT,
    PJA_1,
    RULES_TOOL,
    RUNTIME_INPUTS,
    WORKFLOW_WITH_REPEAT,
)
from .test_normalize import _both_formats

# double converting nested workflow doesn't work right, bug in gxformat2
# unrelated to abstract I think.
EXAMPLES = [
    BASIC_WORKFLOW,
    # NESTED_WORKFLOW,
    OPTIONAL_INPUT,
    PJA_1,
    RULES_TOOL,
    RUNTIME_INPUTS,
    WORKFLOW_WITH_REPEAT,
]

# TODO:
# - Ensure when reading native format - output information is included,
#   not needed for concise format2 but would make the CWL more authentic
# - Fix bug in converted nested workflow that results in the following tests
#   breaking.
# - Write test around RUNTIME_INPUTs - translate it to string input.
# - Write test and handle $links embedded in Format2 workflows


def test_abstract_export():
    for example in EXAMPLES:
        for as_dict in _both_formats(example):
            _run_example(as_dict)


def test_to_cwl_optional():
    for as_dict in _both_formats(OPTIONAL_INPUT):
        abstract_as_dict = from_dict(as_dict)
        assert abstract_as_dict["inputs"]["the_input"]["type"] == "File?"


def test_to_cwl_array():
    for as_dict in _both_formats(RULES_TOOL):
        abstract_as_dict = from_dict(as_dict)
        assert abstract_as_dict["inputs"]["input_c"]["type"] == "File[]"


def test_nested_workflow():
    _run_example(ordered_load(NESTED_WORKFLOW))


def _run_example(as_dict):
    abstract_as_dict = from_dict(as_dict)
    with open("test.cwl", "w") as f:
        ordered_dump(abstract_as_dict, f)

    check_abstract_def(abstract_as_dict)

    # validate format2 workflows
    enable_dev = "dev" in CWL_VERSION
    loadingContext = LoadingContext()
    loadingContext.enable_dev = enable_dev
    loadingContext.loader = default_loader(
        loadingContext.fetcher_constructor,
        enable_dev=enable_dev,
    )
    loadingContext.resolver = getdefault(loadingContext.resolver, tool_resolver)
    loadingContext, workflowobj, uri = fetch_document("./test.cwl", loadingContext)
    loadingContext, uri = resolve_and_validate_document(
        loadingContext,
        workflowobj,
        uri,
    )


def check_abstract_def(abstract_as_dict):
    assert abstract_as_dict["class"] == "Workflow"
    assert abstract_as_dict["cwlVersion"] == CWL_VERSION
    for step_id, step_def in abstract_as_dict["steps"].items():
        assert "run" in step_def
        run = step_def["run"]
        assert "in" in step_def
        assert isinstance(step_def["in"], (dict, list))
        assert run["class"] in ["Operation", "Workflow"]
        assert "out" in step_def
        assert isinstance(step_def["out"], list)
