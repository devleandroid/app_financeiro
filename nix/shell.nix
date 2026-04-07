{ pkgs ? import <nixpkgs> {} }:

let
  pythonEnv = pkgs.python313.withPackages (ps: with ps; [
    # Data science
    numpy
    pandas
    plotly
    
    # Web framework
    fastapi
    uvicorn
    
    # Frontend
    streamlit
    
    # Utils
    requests
    python-dotenv
    pydantic
  ]);
in
pkgs.mkShell {
  buildInputs = [
    pythonEnv
    pkgs.stdenv.cc.cc.lib
    pkgs.which
    pkgs.bash
    pkgs.psmisc  # para fuser
    pkgs.curl    # para testes
    pkgs.sqlite  # <--- CORRIGIDO: sqlite, não sqlite3
  ];
  
  shellHook = ''
    export PYTHONPATH="${pythonEnv}/${pythonEnv.sitePackages}:$PYTHONPATH"
    export PATH="${pythonEnv}/bin:$PATH"
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"
    
    echo ""
    echo "🚀 Ambiente InvestSmart (NixOS)"
    echo "==================================="
    echo "✅ Python: $(python --version)"
    echo "✅ Pacotes Python instalados:"
    echo "   - numpy, pandas, plotly"
    echo "   - fastapi, uvicorn"
    echo "   - streamlit, requests"
    echo "✅ Pacotes sistema: sqlite, psmisc, curl"
    echo "==================================="
    
    # Criar aliases úteis
    alias run-backend='PYTHONPATH=. uvicorn src.presentation.api.main:app --reload --port 8000'
    alias run-frontend='PYTHONPATH=. streamlit run src.presentation.web.app:app --server.port 8501'
    alias run-admin='PYTHONPATH=. streamlit run src.presentation.web.pages.admin:app --server.port 8502'
  '';
}