# Guia Rápido para NixOS

## 🚀 Primeira execução

```bash
# Entre no diretório do projeto
cd ~/Documentos/app_financeiro

# Dê permissão de execução aos scripts
chmod +x scripts/start.sh

# Teste se tudo está funcionando
./scripts/start.sh test

# Inicie o projeto completo
./scripts/start.sh both

📦 Comandos úteis

    ./scripts/start.sh both - Inicia backend e frontend juntos

    ./scripts/start.sh backend - Só o backend (http://localhost:8000)

    ./scripts/start.sh frontend - Só o frontend (http://localhost:8501)

    ./scripts/start.sh shell - Entra no ambiente interativo

    ./scripts/start.sh test - Testa instalação

🔧 Se precisar instalar mais pacotes
bash

# Para pacotes Python temporários
./scripts/start.sh install nome-do-pacote

# Para pacotes permanentes, edite o shell.nix

🐛 Debug

Se algo não funcionar:
bash

# Verificar se as bibliotecas estão acessíveis
nix-shell --run "python -c 'import numpy; print(numpy.__file__)'"

# Verificar PATH
nix-shell --run "echo \$PATH"

# Verificar LD_LIBRARY_PATH
nix-shell --run "echo \$LD_LIBRARY_PATH"


Como usar agora

# 1. Entre no diretório do projeto
cd ~/Documentos/app_financeiro

# 2. Dê permissão de execução
chmod +x scripts/start.sh

# 3. Teste o ambiente
./scripts/start.sh test

# 4. Inicie TUDO (backend + frontend)
./scripts/start.sh both

# 5. Ou inicie separadamente:
# Terminal 1:
./scripts/start.sh backend
# Terminal 2:
./scripts/start.sh frontend


# Rodar o backend com debug
nix-shell --run "python main_debug.py"

# Executar o teste
nix-shell --run "python test_fixer.py"

# Para usar, renomeie o arquivo:
mv services/fixer_service.py services/fixer_service_real.py
cp services/fixer_service_simple.py services/fixer_service.py

# Para testar e usaar o diagnostico completo
chmod +x diagnose.sh
./diagnose.sh

# Testar a chave do Fixer.io
nix-shell --run "python test_fixer.py"

# Se a chave não funcionar, use a versão simulada
cp services/fixer_service_simple.py services/fixer_service.py

# Iniciar backend com logs detalhados
nix-shell --run "python main_debug.py"

# Em outro terminal, testar
curl http://localhost:8000/api/dados-completos?moedas=BRL,EUR,GBP,CNY


# 1. Parar o backend atual (Ctrl+C)

# 2. Testar apenas o serviço Fixer
nix-shell --run "python test_fixer_real.py"

# 3. Se os dados estiverem corretos, iniciar o backend
./scripts/start.sh backend

# 4. Em outro terminal, testar o endpoint
nix-shell --run "python test_dados.py"


# Testar a configuração do NixOS
sudo nixos-rebuild dry-run

# Aplicar as configurações
sudo nixos-rebuild switch

# Verificar status dos serviços
sudo systemctl status app-financeiro-backend
sudo systemctl status app-financeiro-frontend
sudo systemctl status nginx


# Ver logs em tempo real
sudo journalctl -u app-financeiro-backend -f
sudo journalctl -u app-financeiro-frontend -f

# Reiniciar serviços após alterações
sudo systemctl restart app-financeiro-backend
sudo systemctl restart app-financeiro-frontend

# Ver timers agendados
systemctl list-timers | grep app-financeiro

# Testar envio de relatório manualmente
cd ~/Documentos/app_financeiro
python scripts/enviar_relatorio.py

# Verificar configuração do Nginx
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx

## Como executar AGORA no NixOS: ##
# 1. Abrir um terminal e entrar no ambiente
cd ~/Documentos/app_financeiro
nix-shell

# 2. DENTRO do nix-shell, rodar o backend:
python main.py

# 3. Abrir OUTRO terminal e também entrar no nix-shell:
cd ~/Documentos/app_financeiro
nix-shell

# 4. DENTRO deste segundo terminal, rodar o frontend:
streamlit run app.py

# 5. Abrir TERCEIRO terminal e também entrar no nix-shell:
cd ~/Documentos/app_financeiro
nix-shell

# 6. DENTRO deste terceiro terminal, rodar o admin:
streamlit run admin.py --server.port 8502

# Agora você pode rodar os 3 ambientes
# Terminal 1
./run.sh backend

# Terminal 2
./run.sh frontend

# Terminal 3
./run.sh admin

# Testar relatório
./run.sh relatorio

# Visão Geral do Sistema

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Usuário       │────▶│   Solicita      │────▶│   Recebe        │
│   Digita Email  │     │   Chave via API │     │   Chave por     │
│                 │     │                 │     │   Email         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Acessa        │◀────│   Valida Chave  │◀────│   Digita Chave  │
│   Dashboard     │     │   (4h válida)   │     │   Recebida      │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                                              ┌─────────────────┐
                                              │                 │
                                              │   Admin recebe  │
                                              │   Relatório com │
                                              │   Todos Emails  │
                                              │                 │
                                              └─────────────────┘



# Para enviar relatório toda segunda às 9h, crie um timer systemd:
sudo nano /etc/systemd/system/relatorio-investsmart.service
[ Erro ao escrever /etc/systemd/system/relatorio-investsmart.service: Read-only file system ]
[Unit]
Description=Relatório Semanal InvestSmart
After=network.target

[Service]
Type=oneshot
User=lebronx
WorkingDirectory=/home/lebronx/Documentos/app_financeiro
Environment=PATH=/run/current-system/sw/bin
ExecStart=/run/current-system/sw/bin/nix-shell --run "python scripts/relatorio_email.py"

[Install]
WantedBy=multi-user.target

# Criar timer
sudo nano /etc/systemd/system/relatorio-investsmart.timer

[Unit]
Description=Timer para relatório semanal
Requires=relatorio-investsmart.service

[Timer]
OnCalendar=Mon *-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target


# Ativar
sudo systemctl daemon-reload
sudo systemctl enable relatorio-investsmart.timer
sudo systemctl start relatorio-investsmart.timer

# Verificar
systemctl list-timers | grep relatorio



# COMO TESTAR TUDO
# 1. Instalar dependências
./run.sh install

# 2. Terminal 1 - Backend
./run.sh backend

# 3. Terminal 2 - Frontend
./run.sh frontend

# 4. Terminal 3 - Admin
./run.sh admin

# 5. Testar relatório
./run.sh relatorio



FLUXO COMPLETO DO SISTEMA

Usuário acessa http://localhost:8501

Digita email na aba "Solicitar Acesso"

Sistema gera chave de 8 dígitos e envia por email

Usuário recebe email com chave (válida 4h)

Usuário digita chave na aba "Já tenho chave"

Sistema valida e libera acesso ao dashboard

Admin acessa http://localhost:8502 para ver relatórios

Toda segunda 9h, relatório automático chega por email

# 1. Verifique se backend está rodando
ps aux | grep python

# 2. Se não estiver, inicie:
cd ~/Documentos/app_financeiro
nix-shell
python main.py

# 3. Em outro terminal, teste o diagnóstico
python diagnostico.py

# 4. Ajuste o timeout no app.py para 30 segundos
# 5. Use o script melhorado: ./scripts/start.sh both