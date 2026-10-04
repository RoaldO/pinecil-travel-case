.PHONY: test build render clean

test:
	uv run pytest

build:
	uv run python -m cad.build

render:
	uv run python -m cad.render

clean:
	rm -rf build __pycache__ cad/__pycache__ tests/__pycache__ .pytest_cache
