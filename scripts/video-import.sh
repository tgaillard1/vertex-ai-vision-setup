#!/bin/bash
#*****************************************************************************
# Script Name: video-import.sh
# Version: 1.0 
# Purpose: Move and import files to Vertex Vision AI
# Date: 11/28/2022
#
# Revision History
#----------------------------------------------------------------------------

# Change Variables in CAPS below for your deployment
gcs_video_clone_location="gs://YOUR_GCS_TRANSFER_BUCKET"
source="/home/YOUR_LOCAL_USER/YOUR_LOCAL_DIR_FOR_VIDEO_UPLOADS"
dest="/home/YOUR_LOCAL_USER/YOUR_LOCAL_DESTINATION_DIR"
project="YOUR_PROJECT_ID"
region="us-central1"
stream_id="YOUR_STREAM_ID"
loop_timeout=90
sleep_amount=2
remove_amount=10
sleep_time=$(($loop_timeout + $sleep_amount))
remove_timeout=$((loop_timeout + $remove_amount))

echo "Download video files from GCS"
echo "Loop timeout '$loop_timeout' and Sleep timeout '$sleep_time' and remove timeout '$remove_timeout'"
gsutil mv $gcs_video_clone_location/*.mp4 $source
sleep 2

cd $source

for file in *.mp4
do
        if [ ! -f $dest/"$file" ]
        then
                echo "Importing file $source/$file into Vertex Vision AI"
                break
        fi
done

echo "$(date +%H:%M:%S): start"
pids=()
timeout $loop_timeout bash -c "vaictl -p '$project' \
                -l '$region' \
                -c application-cluster-0 \
                --service-endpoint visionai.googleapis.com \
                send video-file to streams '$stream_id' --file-path '$source/$file' --loop" &
pids+=($!)
timeout $remove_timeout bash -c "sleep '$sleep_time'; rm -v '$file'; echo 'Removed $file job 2 terminated successfully'" &
pids+=($!)
for pid in ${pids[@]}; do
   wait $pid
   exit_status=$?
   if [[ $exit_status -eq 124 ]]; then
      echo "$(date +%H:%M:%S): $pid terminated by timeout"
   else
      echo "$(date +%H:%M:%S): $pid exited successfully"
   fi
done
