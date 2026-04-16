{ pkgs ? import <nixpkgs> {} }:

let
  pythonEnv = pkgs.python313.withPackages (ps: with ps; [
    # Web framework
    fastapi
    uvicorn
    
    # Frontend
    streamlit
    plotly
    
    # Data science
    pandas
    numpy
    
    # Utils
    requests
    python-dotenv
    pydantic
    psycopg2      # <--- ADICIONADO para PostgreSQL
  ]);
in
pkgs.mkShell {
  buildInputs = [
    pythonEnv
    pkgs.stdenv.cc.cc.lib
    pkgs.which
    pkgs.bash
    pkgs.psmisc
    pkgs.curl
    pkgs.sqlite
    pkgs.postgresql  # <--- ADICIONADO cliente PostgreSQL
  ];
  
  shellHook = ''
    export PYTHONPATH="${pythonEnv}/${pythonEnv.sitePackages}:$PYTHONPATH"
    export PATH="${pythonEnv}/bin:$PATH"
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"
    
    echo ""
    echo "🚀 Ambiente InvestSmart (NixOS)"
    echo "==================================="
    echo "✅ Python: $(python --version)"
    echo "✅ Pacotes: fastapi, uvicorn, streamlit, plotly, pandas, psycopg2"
    echo "✅ PostgreSQL: $(psql --version 2>/dev/null || echo 'cliente disponível')"
    echo "==================================="
  '';
}
