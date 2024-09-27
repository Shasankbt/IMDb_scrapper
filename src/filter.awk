BEGIN{
    FS = "\t";
}
FNR==NR { 
    if ($3 > 2500) ratingCount_filtered[$1] = $3; 
    next 
} 
($1 in ratingCount_filtered) {
    if (($2 == "tvSeries" || $2 == "movie") &&  $6 >= 2010) print $1;
}
