"""
This module contains utility functions for the Hydrogen Supply Chain Environment.
"""

from yaml import safe_load
from importlib import util
from pathlib import Path


def add_constants(node, data):
    if "constants" in data[node.get_id()]:
        for constant, value in data[node.get_id()]["constants"].items():
            node["variables"].add(constant, value)
        node["variables"].collection(
            "constants", list(data[node.get_id()]["constants"].keys())
        )


def add_equations(node, data, module):
    if "equations" in data[node.get_id()]:
        for _, value in data[node.get_id()]["equations"].items():
            node["functions"].add(
                getattr(module, value["name"]),
                value["name"],
                value["target_node"],
                value["var_name"],
            )
        node["functions"].collection(
            "equations",
            [item["name"] for item in data[node.get_id()]["equations"].values()],
        )


def add_constraints(node, data, module):
    if "constraints" in data[node.get_id()]:
        for _, constraint in data[node.get_id()]["constraints"].items():
            node["functions"].add(
                value=getattr(module, constraint["name"]),
                key=constraint["name"],
                targ=constraint["target_node"],
                varname=constraint["var_name"],
            )
            node["variables"].add(
                key=constraint["var_name"],
                value=0,
                range=None,
            )
        node["functions"].collection(
            "constraints",
            [item["name"] for item in data[node.get_id()]["constraints"].values()],
        )
        node["variables"].collection(
            "constraints",
            [item["var_name"] for item in data[node.get_id()]["constraints"].values()],
        )


def add_inlets(node, data):
    if "inlets" in data[node.get_id()]:
        for _, value in data[node.get_id()]["inlets"].items():
            node["variables"].add(
                key=value["name"],
                value=(value["rng"][0] + value["rng"][1]) / 2,
                range=value["rng"],
            )
        node["variables"].collection(
            "inlets", [item["name"] for item in data[node.get_id()]["inlets"].values()]
        )


def add_controls(node, data):
    if "controls" in data[node.get_id()]:
        for _, value in data[node.get_id()]["controls"].items():
            node["variables"].add(
                key=value["name"],
                value=(value["rng"][0] + value["rng"][1]) / 2,
                range=value["rng"],
            )
        node["variables"].collection(
            "controls",
            [item["name"] for item in data[node.get_id()]["controls"].values()],
        )


def module_loader(current_path, folder_name) -> None:
    data = {}
    for file in Path(current_path / folder_name).glob("*.yml"):
        with open(file, "r") as f:
            data.update(safe_load(f))

    # Load the module from file

    functions = data["function_file"]
    spec = util.spec_from_file_location(
        "node_functions", current_path / folder_name / functions
    )
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return data, module
