{ nix2container
, pkgs
, appDir
, depsDir
, myTool
, tag ? "latest"
, user ? "ryax"
, group ? "ryax"
, uid ? 1200
, gid ? 1200
, userHome ? "/home/${user}"
}:
let
  uidStr = builtins.toString uid;
  gidStr = builtins.toString gid;

  inherit (pkgs) runCommand cacert coreutils python3;
  defaultConfig = runCommand "base-config" { } ''
    mkdir -p $out/etc/ssl/certs/
    ln -s ${cacert}/etc/ssl/certs/ca-bundle.crt $out/etc/ssl/certs/ca-certificates.crt

    # Create temporary directories
    mkdir $out/tmp
    mkdir -p $out/var/tmp

    mkdir -p $out/usr/bin
    ln -s ${coreutils}/bin/env $out/usr/bin/env

    # Fix localhost DNS resolution
    cat > $out/etc/nsswitch.conf <<EOF
    hosts: files dns
    EOF

    # create the Ryax user
    mkdir -p $out/etc/pam.d
    echo "${user}:x:${uidStr}:${gidStr}:Ryax User:${userHome}:/bin/bash" > $out/etc/passwd
    echo "${user}:!x:::::::" > $out/etc/shadow
    echo "${group}:x:${gidStr}:" > $out/etc/group
    echo "${group}:x::" > $out/etc/gshadow
    cat > $out/etc/pam.d/other <<EOF
    account sufficient pam_unix.so
    auth sufficient pam_rootok.so
    password requisite pam_unix.so nullok sha512
    session required pam_unix.so
    EOF
    touch $out/etc/login.defs
    mkdir -p $out${userHome}
  '';
  base = nix2container.buildLayer {
    perms = [
      {
        path = defaultConfig;
        regex = "/tmp";
        mode = "1777";
      }
      {
        path = defaultConfig;
        regex = "/var/tmp";
        mode = "1777";
      }
    ];

    copyToRoot =
      [
        (pkgs.buildEnv {
          name = "root";
          paths = with pkgs; [ coreutils python3 bashInteractive findutils procps gnutar gnugrep ];
          pathsToLink = [ "/bin" ];
        })
        defaultConfig
      ];
  };
  dependencies = nix2container.buildLayer {
    copyToRoot = runCommand "stack" { } ''
      set -x
      mkdir -p $out/data
      echo Install python environment created by pip prior to this build
      if [ -d ${depsDir}/.env ]; then
        cp -vr ${depsDir}/.env $out/data/.env
      fi
    '';
    reproducible = false;
  };
  app = nix2container.buildLayer {
    copyToRoot = runCommand "app" { } ''
      echo Install the app
      mkdir -p $out/data
      cp -vr ${appDir}/global_continuum_placement $out/data/global_continuum_placement

      mkdir -p $out/bin
      cp -v ${appDir}/${myTool} $out/bin/${myTool}
    '';
    reproducible = false;
  };
in
nix2container.buildImage {
  name = myTool;
  inherit tag;

  layers = [ base dependencies app ];

  config.EntryPoint = [ myTool ];
  config.Env = [
    "PYTHONPATH=/data/.env:/data"
  ];
  config.WorkingDir = "/data";
  config.Labels = {
    "ryax.tech" = myTool;
  };
}
