# ☁️ Guia de Deploy

## Opção 1: Koyeb (Backend)

1. Crie uma conta em [koyeb.com](https://koyeb.com)
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente:
   - `ENVIRONMENT=production`
   - `ADMIN_USER=admin`
   - `ADMIN_PASSWORD=sua_senha`
   - `FIXER_API_KEY=sua_chave`
4. Clique em **Deploy**

## Opção 2: Render (Backend)

1. Crie uma conta em [render.com](https://render.com)
2. Clique em **New Web Service**
3. Conecte seu repositório GitHub
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn src.presentation.api.main:app --host 0.0.0.0 --port $PORT`
5. Adicione as variáveis de ambiente
6. Clique em **Create Web Service**

## Opção 3: Streamlit Cloud (Frontend)

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Clique em **New app**
3. Selecione o repositório
4. Configure:
   - **Main file path:** `src/presentation/web/app.py`
   - **Secrets:** `API_URL=https://seu-backend.onrender.com`
5. Clique em **Deploy**

## Variáveis de Ambiente

| Variável | Descrição | Obrigatória |
|----------|-----------|-------------|
| `ENVIRONMENT` | `production` | ✅ Sim |
| `API_URL` | URL do backend | ✅ Sim (frontend) |
| `ADMIN_USER` | Usuário admin | ❌ (padrão: admin) |
| `ADMIN_PASSWORD` | Senha admin | ❌ (padrão: admin123) |
| `FIXER_API_KEY` | Chave Fixer.io | ❌ (usa mock) |

## Verificar Deploy

```bash
# Testar backend
curl https://seu-backend.onrender.com/api/health

# Testar frontend
# Acesse https://seu-app.streamlit.app
← Voltar
