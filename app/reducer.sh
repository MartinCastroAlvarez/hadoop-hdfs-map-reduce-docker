#!/bin/bash
while read key values
do
  count=0
  for value in $values
  do
    count=$((count + value))
  done
  echo -e "$key\t$count"
done
