#!/bin/bash
#to be run on download node on savio e.g. nohup bash pull_cirrus.sh

#iterate through the lines of a text file
var=wspeed
cd /global/scratch/users/jennaisrael/time_varying_data/cirrus_LOCA2/$var

paste -d@ /global/scratch/users/jennaisrael/climate_data_processing/pull_data_scripts/site_$var.txt /global/scratch/users/jennaisrael/climate_data_processing/pull_data_scripts/filename_$var.txt | while IFS="@" read -r url fname
do
  #printf 'url: %s\n' "$url"
  #printf 'file: %s\n' "$fname"
  wget --user loca2_hybrid --password='iPnwHd5egE3$F$tjspKc' -r -nd -np $fname $url

  #wget --user loca2_hybrid --password='iPnwHd5egE3$F$tjspKc' -r -nd -np -A $fname $url
  #wget --user loca2_hybrid --password='iPnwHd5egE3$F$tjspKc' -r -e robots=off -nd -np -A $fname $url
  #wget --user loca2_hybrid --password='iPnwHd5egE3$F$tjspKc' -r -erobots=off -nd -np -A $fname $url
done


#this is giving a weird vims error
#for url in $(cat /global/scratch/users/jennaisrael/climate_data_processing/pull_data_scripts/site_psl.txt), file in $(cat /global/scratch/users/jennaisrael/climate_data_processing/pull_data_scripts/filename_psl.txt)
#do 

#this didn't work or throw and error
#readarray -t a1 < /global/scratch/users/jennaisrael/climate_data_processing/pull_data_scripts/site_psl.txt
#readarray -t a2 < /global/scratch/users/jennaisrael/climate_data_processing/pull_data_scripts/filename_psl.txt

#for i in "${!a[@]}"
#do printf "%s is a file at %s url" "${a1[i]}" "${a2[i]}"
#done

