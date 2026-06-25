"""Jupyter widget control surface for FABLE scenario parameters."""

from __future__ import annotations

from typing import Any

from fable_pyculator.spec import FableCalculatorSpec, ScenarioParameter


class ScenarioControlSurface:
    """Small ipywidgets-backed control surface for a FABLE scenario spec."""

    def __init__(self, spec: FableCalculatorSpec) -> None:
        self.spec = spec
        widgets = _load_widgets()
        self._controls = {
            **{parameter.name: _parameter_widget(widgets, parameter) for parameter in spec.parameters},
            **{control.name: _selection_widget(widgets, control) for control in spec.selection_controls},
        }
        self.widget = widgets.VBox(list(self._controls.values()))

    def values(self) -> dict[str, object]:
        """Return current parameter values keyed by scenario parameter name."""

        return {name: control.value for name, control in self._controls.items()}

    def set_values(self, values: dict[str, object]) -> None:
        """Set current parameter widget values by scenario parameter name."""

        unknown = sorted(set(values) - set(self._controls))
        if unknown:
            raise KeyError(f"unknown scenario parameter(s): {', '.join(unknown)}")
        for name, value in values.items():
            self._controls[name].value = value

    def _ipython_display_(self) -> None:
        display = _load_display()
        display(self.widget)


def _parameter_widget(widgets: Any, parameter: ScenarioParameter) -> Any:
    description = parameter.label
    if parameter.choices:
        return widgets.Dropdown(
            options=list(parameter.choices),
            value=parameter.default if parameter.default is not None else parameter.choices[0],
            description=description,
        )
    if parameter.kind == "boolean":
        return widgets.Checkbox(value=bool(parameter.default), description=description)
    if parameter.kind == "number":
        value = 0 if parameter.default is None else parameter.default
        return widgets.FloatText(value=value, description=description)
    return widgets.Text(value="" if parameter.default is None else str(parameter.default), description=description)


def _selection_widget(widgets: Any, control: Any) -> Any:
    return widgets.Dropdown(
        options=[(option.label or option.value, option.value) for option in control.options],
        value=control.default,
        description=control.label,
    )


def _load_widgets() -> Any:
    try:
        import ipywidgets as widgets
    except ImportError as error:
        raise RuntimeError("Install fable-pyculator[notebook] to use ScenarioControlSurface.") from error
    return widgets


def _load_display() -> Any:
    try:
        from IPython.display import display
    except ImportError as error:
        raise RuntimeError("Install fable-pyculator[notebook] to display ScenarioControlSurface.") from error
    return display
