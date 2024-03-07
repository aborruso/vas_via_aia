#!/bin/bash

set -x
set -e
set -u
set -o pipefail

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "${folder}"/../data/
mkdir -p "${folder}"/tmp

# clean up
mlrgo -S --csv --ifs ";" clean-whitespace "${folder}"/../rawdata/progetti_italia.csv  > "${folder}"/../data/progetti_italia.csv

# normalizza nomi campi

qsv safenames "${folder}"/../data/progetti_italia.csv >"${folder}"/tmp/tmp.csv
mv "${folder}"/tmp/tmp.csv "${folder}"/../data/progetti_italia.csv

# dati per numero di progetti presentati per ciascuna regione

mlrgo -S --csv cut -f id,regioni,tipologia then nest --evar "," -f regioni then clean-whitespace "${folder}"/../data/progetti_italia.csv > "${folder}"/../data/progetti_italia_regioni.csv
