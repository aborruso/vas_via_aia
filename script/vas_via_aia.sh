#!/bin/bash

set -x
set -e
set -u
set -o pipefail

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "${folder}"/../data/
mkdir -p "${folder}"/../data/risorse
mkdir -p "${folder}"/tmp

# clean up
mlrgo -S --csv --ifs ";" clean-whitespace "${folder}"/../rawdata/progetti_italia.csv  > "${folder}"/../data/progetti_italia.csv

# normalizza nomi campi

qsv safenames "${folder}"/../data/progetti_italia.csv >"${folder}"/tmp/tmp.csv
mv "${folder}"/tmp/tmp.csv "${folder}"/../data/progetti_italia.csv

# correggi Valle d'Aosta
mlrgo -I -S --csv sub -f regioni "Valle.+" "Valle d'Aosta" "${folder}"/../data/progetti_italia.csv

# dati per numero di progetti presentati per ciascuna regione

mlrgo -S --csv cut -f id,regioni,tipologia then nest --evar "," -f regioni then clean-whitespace then count-distinct -f regioni,tipologia then sort -f regioni,tipologia "${folder}"/../data/progetti_italia.csv > "${folder}"/../data/progetti_italia_regioni.csv

# estrai nomi regioni, province e comuni
for i in regioni province comuni; do
    mlrgo -S --csv cut -f "$i" then nest --evar "," -f "$i" then clean-whitespace then uniq -a then sort -f "$i" "${folder}"/../data/progetti_italia.csv >"${folder}"/../data/risorse/"$i".csv
done

nome="listaComuniISTAT_ANPR"

URL="https://github.com/aborruso/archivioDatiPubbliciPreziosi/raw/master/docs/archivioComuniANPR/comuniANPR_ISTAT.csv"

# scarica comuni Istat
if [ ! -f "${folder}"/../data/risorse/"$nome".csv ]; then
    curl -skL "$URL" >"${folder}"/../data/risorse/"$nome".csv
fi

