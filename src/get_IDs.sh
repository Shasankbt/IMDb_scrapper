#!/bin/bash

function checkDataFiles(){
    if ! [ -f $1 ] ; then
        if ! [ -f "${1}.gz" ]; then
            echo "no '${1}.gz' nor '${1}' found"
            exit 1
        fi
        echo "no '${1}' , extracting from '${1}.gz'"
        gunzip -k "${1}.gz"
    elif [ "${1}.gz" -nt $1 ]; then
        echo "newer '${1}.gz' found, extracting"
        gunzip -k -f "${1}.gz"
    else
        echo "${1} is up-to-date."
    fi
}

checkDataFiles "title.basics.tsv"
checkDataFiles "title.ratings.tsv"

awk -f filter.awk "title.ratings.tsv" "title.basics.tsv" > "../scrape/imdbID.txt"


