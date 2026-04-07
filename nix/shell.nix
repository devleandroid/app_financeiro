{ pkgs ? import <nixpkgs> {} }:

let
  pythonEnv = pkgs.python313.withPackages (ps: with ps; [
    # Web framework
    fastapi
    uvicorn
    
    # Frontend
    streamlit
    plotly        # <--- ADICIONADO
    
    # Data science
    pandas
    numpy
    
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
    pkgs.psmisc
    pkgs.curl
    pkgs.sqlite
  ];
  
  shellHook = ''
    export PYTHONPATH="${pythonEnv}/${pythonEnv.sitePackages}:$PYTHONPATH"
    export PATH="${pythonEnv}/bin:$PATH"
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"
    
    echo ""
    echo "🚀 Ambiente InvestSmart (NixOS)"
    echo "==================================="
    echo "✅ Python: $(python --version)"
    echo "✅ Pacotes: fastapi, uvicorn, streamlit, plotly, pandas"
    echo "==================================="
  '';
}
