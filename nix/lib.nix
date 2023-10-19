{ pkgs, python }:
{
  test = pkgs.writeShellApplication {
    name = "run-tests";
    text = ''
      python --version
      poetry --version
      poetry install
      poetry run bash test.sh $@
    '';
    runtimeInputs = [ python pkgs.poetry pkgs.bashInteractive ];
    checkPhase = "";
  };
  lint = pkgs.writeShellApplication {
    name = "run-lint";
    text = ''
      python --version
      poetry --version
      poetry install
      LINT_CMD=''${LINT_CMD:-./lint.sh}
      poetry run bash "$LINT_CMD" $@
    '';
    runtimeInputs = [ python pkgs.poetry pkgs.bashInteractive ];
    checkPhase = "";
  };

  install = appDir: buildDir: pkgs.writeShellScriptBin "python-install" ''
    set -x
    set -e
    rm -rf ${buildDir}
    mkdir -p ${buildDir}
    cd ${buildDir}

    cp ${appDir + "/pyproject.toml"} pyproject.toml
    cp ${appDir + "/poetry.lock"} poetry.lock

    export PIP_DISABLE_PIP_VERSION_CHECK=1
    export PYTHONDONTWRITEBYTECODE=1
    export PYTHONHASHSEED=0
    export PYTHONUNBUFFERED=1

    ${python.pkgs.poetry}/bin/poetry export -f requirements.txt --without-hashes --output requirements.txt

    echo Fetching Python dependencies...
    ${python.pkgs.pip}/bin/pip install --target ".env" -r requirements.txt

    # Remove bytecode to have a reproducible layer
    find "./.env" -type f -name "*.pyc" -delete
    find "./.env" -type d -name "__pycache__" -delete
  '';
}
