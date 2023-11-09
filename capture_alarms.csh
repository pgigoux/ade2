#!/bin/csh -f
unalias *

if ($#argv > 1) then
   set in_file = $argv[1]
   set out_file = $argv[2]
else
   echo "Usage: $0 input_file output_file"
   exit 1
endif

if (-e $out_file) then
   echo "Output file ${out_file} already exists"
   exit 1
endif

set fields = ('SEVR' 'STAT' 'AMSG' 'NSTA' 'NSEV' 'NAMSG' 'DESC')  

foreach line (`cat $in_file`)
   echo $line
   foreach field ($fields)
       set chan = "${line}.${field}"
       set val = `caget -w 10 -t $chan`
       echo "${chan},${val}" >> $out_file
   end
end
