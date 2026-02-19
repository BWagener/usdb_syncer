{
  inputs.nixpkgs-unstable.url = "nixpkgs/nixos-unstable";

  outputs = {
    self,
    nixpkgs-unstable,
  }: let
    pkgs = nixpkgs-unstable.legacyPackages.x86_64-linux;
    qtEnv = pkgs.qt6.env "qt6-simc-${pkgs.qt6.qtbase.version}" [
      # qt6.full has been removed. Please use individual packages instead.
      # List of packages retrieved from
      # https://github.com/NixOS/nixpkgs/blob/master/pkgs/development/libraries/qt-6/default.nix
      pkgs.qt6.qtbase
      pkgs.qt6.qtwebengine
      pkgs.qt6.qttools
      pkgs.qt6.qtdeclarative
      pkgs.qt6.qtmultimedia
      pkgs.qt6.qt5compat
      pkgs.qt6.qtwayland
      pkgs.qt6.qtsvg
      pkgs.qt6.qtwebchannel
      pkgs.qt6.qtpositioning
    ];
  in {
    devShells.x86_64-linux.default = pkgs.mkShell {
      buildInputs = with pkgs; [
        kdePackages.breeze
        ffmpeg
        deno
        rsgain

        libkrb5
        python312Packages.gssapi
        qtEnv
        cmake
        gnumake
        gcc
        gdb
        qtcreator

        # this is for the shellhook portion
        qt6.wrapQtAppsHook
        makeWrapper
        bashInteractive
      ];
      # set the environment variables that Qt apps expect
      shellHook = ''
        export QT_QPA_PLATFORM=wayland
        bashdir=$(mktemp -d)
        makeWrapper "$(type -p bash)" "$bashdir/bash" "''${qtWrapperArgs[@]}"
        exec "$bashdir/bash"

        echo "Entering Qt6 development environment"

        # Set up Qt6 library paths for linking
        export QT_PLUGIN_PATH="${qtEnv}/lib/qt-6/plugins"
        export QML_IMPORT_PATH="${qtEnv}/lib/qt-6/qml"
        export QT_QPA_PLATFORM_PLUGIN_PATH="${qtEnv}/lib/qt-6/plugins/platforms"
        export QT_STYLE_OVERRIDE = "breeze";

        # Additional Qt6 library paths
        export PKG_CONFIG_PATH="${qtEnv}/lib/pkgconfig:$PKG_CONFIG_PATH"
      '';
    };
  };
}
