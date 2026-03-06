{ pkgs ? import <nixpkgs> {} }:

let
  pythonEnv = pkgs.python313.withPackages (ps: with ps; [
    numpy
    pandas
    plotly
    fastapi
    uvicorn
    streamlit
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
  ];
  
  shellHook = ''
    export PATH="${pythonEnv}/bin:$PATH"
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"
    
    echo ""
    echo "🚀 Ambiente InvestSmart (NixOS)"
    echo "==================================="
    echo "✅ Python: $(python --version)"
    echo "✅ Pacotes instalados via Nix:"
    echo "   - numpy, pandas, plotly"
    echo "   - fastapi, uvicorn"
    echo "   - streamlit, requests"
    echo "==================================="
  '';
}