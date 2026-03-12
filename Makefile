# Makefile
.PHONY: help install run-backend run-frontend run-admin test clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make install      - Instalar dependências"
	@echo "  make run-backend  - Rodar backend FastAPI"
	@echo "  make run-frontend - Rodar frontend Streamlit"
	@echo "  make run-admin    - Rodar painel admin"
	@echo "  make test         - Rodar testes"
	@echo "  make clean        - Limpar arquivos temporários"

install:
	pip install -r requirements.txt

run-backend:
	uvicorn src.presentation.api.main:app --reload --port 8000

run-frontend:
	streamlit run src/presentation/web/app.py --server.port 8501

run-admin:
	streamlit run src/presentation/web/pages/admin.py --server.port 8502

test:
	pytest tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete