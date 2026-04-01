.PHONY: help install run-backend run-frontend run-admin test clean deploy

help:
	@echo "🚀 Comandos disponíveis:"
	@echo "  make install       - Instalar dependências"
	@echo "  make run-backend   - Rodar backend FastAPI"
	@echo "  make run-frontend  - Rodar frontend Streamlit"
	@echo "  make run-admin     - Rodar painel admin (local)"
	@echo "  make test          - Rodar testes"
	@echo "  make clean         - Limpar arquivos temporários"
	@echo "  make deploy        - Deploy para Koyeb"

install:
	pip install -r requirements.txt

run-backend:
	PYTHONPATH=. uvicorn src.presentation.api.main:app --reload --port 8000

run-frontend:
	PYTHONPATH=. streamlit run src/presentation/web/app.py --server.port 8501

run-admin:
	PYTHONPATH=. streamlit run src/presentation/web/pages/admin.py --server.port 8502

test:
	pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf logs/*.log

deploy:
	git push origin main
	koyeb services redeploy investsmart-backend