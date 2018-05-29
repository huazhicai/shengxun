#!/bin/sh

pcm_recordfile=/data/recordfile_pcm/

#echo arg num is: $#

if [ $# -ne 7 ] ;then
    echo "Usage : ./compress.sh src_dir dest_dir micon logfile area industry label"
    exit 1
fi

mkdir $3
mkdir $3"_pcm"


filelist=`find $1 -name *$3*.pcm`

for absolutely_file in $filelist
do
    file=${absolutely_file##*/}
    name=${file%.*}
    /usr/local/bin/lame --silent -r -s 8 --bitwidth 16 -m m $absolutely_file $3"/"$name"".mp3
    mv -f $absolutely_file $3"_pcm"
done

#copy communicate log file to compress directory
if [ -f $4 ]; then
    cp $4 $3
    mv $4 $3"_pcm"
fi

log_path=${4%/*}
echo $log_path
if [ -f $log_path"/$3_speech.txt" ]; then
    mv $log_path"/$3_speech.txt" $3"_pcm"
fi

tar -cf $2""$3"".tar $3
rm -rf $3
mv $3"_pcm" $3
tar -zcf ${pcm_recordfile}$5"_"$6"_"$3"_"$7"".tar.gz $3

rm -rf $3