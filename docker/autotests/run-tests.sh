#!/bin/sh
set -eu

attempt=0
until curl -fsS http://selenoid:4444/status >/dev/null; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 60 ]; then
    echo "Selenoid is not ready after 120 seconds" >&2
    exit 1
  fi
  sleep 2
done

rm -rf allure-results
mkdir -p allure-results

pytest -n 2 -q --alluredir=allure-results --junitxml=allure-results/junit.xml
