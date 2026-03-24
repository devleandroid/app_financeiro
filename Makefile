.PHONY: help install run-backend run-frontend run-admin test clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make install       - Instalar dependências"
	@echo "  make run-backend   - Rodar backend"
	@echo "  make run-frontend  - Rodar frontend"
	@echo "  make test          - Rodar testes"
	@echo "  make clean         - Limpar arquivos temporários"

install:
	pip install -r requirements.txt

run-backend:
	PYTHONPATH=. uvicorn src.presentation.api.main:app --reload --port 8000

run-frontend:
	PYTHONPATH=. streamlit run src/presentation/web/app.py --server.port 8501 --server.headless true

test:
	pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
