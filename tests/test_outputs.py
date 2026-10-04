"""Smoke tests for the generated outputs: exports, section render, viewer."""

from cad import params as p
from cad.build import case_parts
from cad.sections import render


def test_case_parts_are_the_four_printables():
    assert set(case_parts()) == {"shell-a", "shell-b", "insert-a", "insert-b"}


def test_sections_render_draws_every_part():
    svg = render().read_text()
    for colour in ("#222222", "#444444", "#e91e63", "#f06292", "#1e88e5", "#2e7d32"):
        assert colour in svg
