{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    uv
  ];

  shellHook = ''
    echo "Development environment ready!"
    echo "Python: $(python --version)"
    echo "uv: $(uv --version)"
  '';
}