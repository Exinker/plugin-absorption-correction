help:
	@echo "Tasks in \033[1;32mdemo\033[0m:"
	@cat Makefile

build: clean
	uv run build

clean:
	@rm -rf .mypy_cache/ .pytest_cache/ .vscode/
	@rm -rf build/ dist/ htmlcov/
	@find . -not -path "./.venv/*" -path "*/__pycache__*" -delete	
	@find . -not -path "./.venv*" -path "*/*.egg-info*" -delete
	@clear