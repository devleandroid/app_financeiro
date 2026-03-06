{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.conda
  ];
  
  shellHook = ''
    echo "🔄 Ambiente com Conda (pesado)"
    echo "Para criar ambiente: conda create -n myenv python=3.13"
  '';
}
# nix-shell shell-conda.nix