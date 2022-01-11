#!/usr/bin/env bash

set -e
# For debug
# set -x

while getopts "fd:" opt; do
  case "$opt" in
    f)
      DO_CHECK_ONLY="false"
      ;;
    d)
      CHECK_DIR="$OPTARG"
      ;;
    ?)
      echo "script usage: $(basename $0) [-f] [-d directory]" >&2
      exit 1
      ;;
  esac
done

TO_CHECK_DIR=${CHECK_DIR:-"."}
CHECK_ONLY=${DO_CHECK_ONLY:-"true"}

if [[ $CHECK_ONLY == "true" ]]
then
    BLACK_EXTRA_OPTS="--check --diff"
    ISORT_EXTRA_OPTS="--check-only --diff"
fi

cat > .flake8 <<EOF
[flake8]
max-line-length = 88
select = C,E,F,W,B,B950
ignore = E203, E501, W503
EOF

echo "-- Checking import sorting"
isort --filter-files $ISORT_EXTRA_OPTS $TO_CHECK_DIR

echo "-- Checking python formating"
black $TO_CHECK_DIR --exclude "docs|ci|ryaxpkgs|migrations|.*pb2.py" $BLACK_EXTRA_OPTS

echo "-- Checking python static checking"
flake8 $TO_CHECK_DIR --exclude="docs/*,ci/*,ryaxpkgs/*,migrations/*,*pb2.py" --per-file-ignores='*/__init__.py:F401'

echo "-- Checking type annotations"
mypy $TO_CHECK_DIR/global_continuum_placement --exclude '(/*pb2.py|ryax_runner/infrastructure/execution_trigger/grpcv1/ryax_execution)'


