"""Structure-aware Markdown templates.

A template takes a parsed document and renders it as opinionated Markdown,
bypassing the generic recursive converter. Selected via the ``template=``
option on ``convert()`` (``--template`` on the CLI).
"""

from ..exceptions import UnsupportedFormatError
from .openapi import OpenApiTemplate

TEMPLATES = {
    "openapi": OpenApiTemplate,
}

__all__ = ["TEMPLATES", "OpenApiTemplate", "get_template"]


def get_template(name: str):
    """Return the template class for ``name`` or raise UnsupportedFormatError."""
    try:
        return TEMPLATES[name]
    except KeyError:
        raise UnsupportedFormatError(
            f"Unknown template: {name!r}. Available templates: {sorted(TEMPLATES)}"
        )
