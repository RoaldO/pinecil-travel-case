.PHONY: test build coupons render sections viewer clean

test:
	uv run pytest

build:
	uv run python -m cad.build

coupons:
	uv run python -m cad.coupons

render:
	uv run python -m cad.render

sections:
	uv run python -m cad.sections

viewer:
	uv run python -m cad.viewer

clean:
	rm -rf build __pycache__ cad/__pycache__ tests/__pycache__ .pytest_cache
