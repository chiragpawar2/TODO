#!/bin/sh
# One entry point for both halves of the project.
#   ./run.sh face        the character on screen
#   ./run.sh tests       the character test suites (fast mode)
#   ./run.sh server      the web/API server
#   ./run.sh cli         the text chat
#   ./run.sh phone       rebuild the phone app into docs/ (GitHub Pages)
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT/todo-character:$ROOT/todo-lists"
PY="$ROOT/.venv/bin/python"
cd "$ROOT"
case "$1" in
  face)   exec "$PY" -m homebot.face ;;
  tests)  "$PY" todo-character/tests/run_expression_tests.py --no-anim && "$PY" todo-character/tests/run_heldout.py ;;
  server) exec "$PY" -m homebot.server ;;
  cli)    exec "$PY" -m homebot.cli ;;
  phone)  exec "$PY" todo-lists/phone/build.py ;;
  *) echo "usage: ./run.sh face | tests | server | cli | phone"; exit 1 ;;
esac
