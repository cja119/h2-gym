"""
Implements the node class
"""

from __future__ import annotations
from typing import Union, Optional
from .props import Functions, Variables
from .utils import pt_func


class Node:
    def __init__(self, node_id=Optional[Union[float, str, int]]) -> None:
        """
        Initializes the node class
        """
        self._id = node_id
        self._inputs = []
        self._outputs = set()
        self._params = {}
        self._metadata = {}
        self._props = ["functions", "variables"]
        self._funcs = None
        self._vars = None
        self._name = None

    def __enter__(self) -> Node:
        """
        Enters the node context
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exits the node context
        """
        pass

    def __setitem__(self, key: str, value: Union[str, int]) -> None:
        """
        Sets the value of the node
        """

        if key == "inputs":
            self.set_input(value)
        elif key == "outputs":
            self.set_output(value)
        elif key == "name":
            self.set_name(value)
        else:
            raise KeyError(f"Key {key} not found in node")

    def __getitem__(self, key: str) -> Union[str, int]:
        """
        Gets the value of the node
        """
        if key == "variables":
            if self._vars is None:
                self._vars = Variables(self._id, self._outputs)
            return self._vars
        elif key == "functions":
            if self._funcs is None:
                self._funcs = Functions(self._id, self._outputs)
            return self._funcs
        else:
            raise KeyError(f"Key {key} not found in node")

    def add_vars(self, key: str, value: Union[str, int]) -> None:
        """
        Adds a variable to the node
        """
        self._vars[key] = value

    def add_funcs(self, f: function, target: tuple[str, str]) -> None:
        """
        Adds a function to the node
        """
        if target[0] not in self._graph.nodes:
            raise ValueError(f"Node {target[0]} not found in graph")

        if target[1] not in self._graph.nodes[target[0]]._vars:
            raise ValueError(f"Variable {target[1]} not found in node {target[0]}")

        self._funcs.append(
            {"function": f, "target_node": target[0], "target_var": target[1]}
        )
        return None

    def get_id(self) -> str:
        """
        Returns the id of the node
        """
        return self._id

    def set_id(self, id: str) -> None:
        """
        Sets the id of the node
        """
        self._id = id

    def set_input(self, input: list) -> None:
        """
        Sets the inputs of the node
        """
        self._inputs.append(input)

    def get_inputs(self) -> list:
        """
        Returns the inputs of the node
        """
        return self._inputs

    def set_output(self, outputs: Union[list, str, float, int]) -> None:
        """
        Sets the outputs of the node
        """

        if not isinstance(outputs, list):
            self._outputs.add(outputs)
        else:
            self._outputs.update(outputs)

    def get_outputs(self) -> dict:
        """
        Returns the outputs of the node
        """
        return self._outputs

    def set_name(self, name: Union[str, int]) -> None:
        """
        Sets the name of the node
        """
        self._name = name

    def get_name(self) -> Union[str, int]:
        """
        Returns the name of the node
        """
        return self._name

    def evaluate(self) -> None:
        """
        Synchronizes the node
        """
        if self._funcs is not None:
            outs = self._funcs.evaluate(self._vars.get_vars())
        else:
            outs = None
            # if self._vars is None:
            #    outs = None
            # else:
            #    outs = self._vars.get_vars()
        return outs

    def set_var(self, vars: dict) -> None:
        """
        Sets the variable of the node
        """
        for key, value in vars.items():
            if key not in self._vars and key[-3:] != "_pt":
                raise KeyError(f"Key {key} not found in variables")
            else:
                self._vars[key] = value
        return None

    def linearise(self, targ, new_fns, new_rngs) -> None:
        """
        Linearizes the node
        """

        # The node now only outputs to the 'target' node
        self._outputs = {targ}

        # If we have functions, linearise their outputs
        if self._funcs is not None:
            new_vars = self._funcs.linearise(targ)
        else:
            new_vars = None

        # If we are being passed some functions (variables)
        # to bypass do so
        if new_fns is not None:
            _dels = []
            for output in new_fns:

                # If this node is  the destination of this variable, we delete it from
                #  the bypass function dictouanry
                if output == self._id:
                    _dels.append(output)

                # pt_func adds a function that 'carries' a variable through the
                # node. We add this as a variable and a function.
                else:
                    for (name, var), rng in zip(
                        new_fns[output].items(), new_rngs[output].values()
                    ):
                        self["variables"].add(key=name + "_pt", value=var, range=rng)
                        self["functions"].add(
                            value=pt_func(name + "_pt"), key=name + "_pt", targ=targ
                        )

            # Delete  the variables from the bypass
            for key in _dels:
                new_fns.pop(key, None)

            # Handling the edge cases.

            if new_vars is not None:
                new_fns.update(new_vars)
            return new_fns
        # Handling the edge cases.
        else:
            return new_vars
