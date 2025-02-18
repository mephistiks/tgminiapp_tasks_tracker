update:
	venv\Scripts\activate && uv pip compile r.in -o r.txt

sync:
	venv\Scripts\activate && uv pip sync r.txt

dev:
	venv\Scripts\activate && python main.py

test:
	venv\Scripts\activate && pytest