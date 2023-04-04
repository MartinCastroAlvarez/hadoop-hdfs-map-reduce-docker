#!/bin/bash
while read line
do
  for word in $line
  do
    echo -e "$word\t1"
  done
done
