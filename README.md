# Vertex Vision AI
- This repo provides a process to perform the following tasks for Vertex Vision AI
    - Trigger a function from a GCS bucket to transfer videos and images to transfer GCS buckets
    - Shell script to download files from corresponding GCS buckets on a Compute Engine server
    - Script to ingest videos via the viactl (Vision SDK) to a Vertex Vision AI stream
    - Steps to invoke the Person/Face blur to the ingested videos and store in Vision Warehouse

<img src="https://github.com/tgaillard1/vertex-ai-vision-setup/blob/main/images/overview-vision1.png" alt="Video Push Architecture"/>

## Setup Steps

1. Create a GCP Project

2. Enable the Vertex AI Vision API:
    [Vertex AI Vision API](https://console.cloud.google.com/flows/enableapi?apiid=visionai.googleapis.com)
    
    ![Enable Vertex AI API](https://github.com/tgaillard1/vertex-ai-vision-setup/blob/main/images/enable-api.png)

3. Create Vertex AI Vision Application
    * Create Stream.  (Note: This is the location where files will be uploaded with the vaictl command line):

        * Navigate to **console** -> **Vertex AI Vision** -> **Streams**
        * Click **REGISTER**
        * Name your stream in the Stream name location, e.g., **store1-bay1-stream**
        * Choose where to store your data select **Region** -- **us-central1** 
        * Select **REGISTER**
        
    * Create Warehouse.  (Note: This is the location where files stored once they are upload to the stream):

        * Navigate to **console** -> **Vertex AI Vision** -> **Warehouses**
        * Click **CREATE**
        * Name your Warehouse, e.g., **store1-video-warehouse**
        * Update the default Time to Live (TTL) to at least **90** days.  This should be modified for your long term needs
        * Select **CREATE**
  
    * Create Application.  (Note: This is workflow for your uploads):

        * Navigate to **console** -> **Vertex AI Vision** -> **Applications**
        * Click **CREATE**
        * Name your Application, e.g., **store1-application**
        * Select Region --> **us-central1** 
        * Select **CREATE**
        * Select **Streams** from the Connectors location.
        * Select the "Box" Streams in the studio.  On the right hand side of the console select **+ STREAMS**
        * Choose the radio button **Select from existing streams** then select the stream you created in step 1, e.g., store1-bay1-stream, then select **ADD STREAMS**
        * Select **Person Blur** from the Pre-trained models location.
        * Select the "Box" Person blur in the studio.  On the right hand side of the console select **Full occlusion**
        * Select **Vision AI Warehouse** from the Connectors location.
	* Select the "Box" Vision AI Warehouse in the studio.  On the right hand side of the console select **CONNECT WAREHOUSE**
	* Choose the radio button **Select from existing warehouses** then select the Warehouse you created earlier, e.g., store1-video-warehouse, then select **CONNECT**
        * Your Studio should look like this:
        ![App-Studio](https://github.com/tgaillard1/vertex-ai-vision-setup/blob/main/images/app-studio1.png)

        * Select the **DEPLOY** button from the top of the page.  The application should deploy without issues.
  
4. Create GCS buckets: (Note: This is where your source files will be uploaded)

    * Create your upload bucket.  (Note: This is where you source files will be uploaded and where your function will trigger transfers):

        * Navigate to **console** -> **Cloud Storage** -> **Buckets**
        * Click **CREATE**
        * Name your bucket, e.g., **vertex-vision-uploads** --> click **CONTINUE**
        * Choose where to store your data select **Region** -- **us-central1 (Iowa)** (Note: you can also use Multi-region) --> click **CONTINUE**
        * Choose a storage class for your data select **Set a default class** -- **Standard** --> click **CONTINUE**
        * Use remaining defaults and then select **CREATE**
    
    * Create GCS transfer bucket: (Note: This is a pass through bucket to ensure the source bucket is not altered)

        * Navigate to **console** -> **Cloud Storage** -> **Buckets**
        * Click **CREATE**
        * Name your bucket, e.g., **vertex-vision-transfer** --> click **CONTINUE**
        * Choose where to store your data select **Region** -- **us-central1 (Iowa)** (Note: you can also use Multi-region) --> click **CONTINUE**
        * Choose a storage class for your data select **Set a default class** -- **Standard** --> click **CONTINUE**
        * Use remaining defaults and then select **CREATE**
        
    * Create Cloud Function:
    
        This function is intended to copy any files that are sent to the GCS "upload" bucket to the GCS "transfer" bucket.  The fuction is based on events in the upload bucket and will provide a cloned copy to the transfer bucket, ensuring that the source files are never disrupted and no duplicates are made.  
   The function has a couple of options included and can be invoked per your requirments.  It currently is set up to delineate between jpg and mp4 files with the option to send the respective files to different transfer buckets.  The default code also limits the file size of the videos to 35MB.  To adjust the size limit change the value of the "blob.size < 35000000" value to your requirements.   

        * Navigate to **console** -> **Cloud Funcctions**
        * Click **CREATE FUNCTION**
        * For environment select **1st gen**
        * Name your function, e.g., **buckets-transfer-function**
        * Choose Region --> **us-central1 (Iowa)**
        * In the Trigger section for "Trigger type" select **Cloud Storage**
        * In the Trigger section for "Event type" select **On (finalizing/creating) file in the selected bucket**
        * For the "Bucket" select **BROWSE** and locate the GCS "upload" bucket you created above, e.g., vertex-vision-uploads  --> then clicke **SELECT** 
        * Click **SAVE**
        * Clice **NEXT**
        * In the **Code** section for "Runtime" select **Python 3.10**
        * In the "Inline Editor" select main.py then replace all of the code in default with the code in the Git functions directory functions/main.py
		* Replace variables in CAPS with your information.
			* YOUR_PROJECT_ID (the project ID where your bucket is created)
            * YOUR_GCS_UPLOAD_BUCKET (This is your source bucket where videos and images are uploaded.  It should only have the name of the bucket, e.g., **vertex-vision-uploads**)
            * YOUR_GCS_VIDEO_TRANSFER_BUCKET (This is your transfer bucket for videos.  It should only have the name of the bucket, e.g., **vertex-vision-transfer**)
            * YOUR_GCS_IMAGES_TRANSFER_BUCKET (This is your transfer bucket for images.  It should only have the name of the bucket, e.g., **vertex-images-transfer**) (Note: this was not created as part of the project but is an option for users) 
            
        * Ensure the "Entry point" is pointed to **hello_gcs**
        * In the "Inline Editor" select requirements.txt then replace all of the code in default with the code in the Git functions directory functions/requirements.txt
        * Then selct **DEPLOY**

5. Create and Start a VM:

    * Navigate to **console** -> **Compute Engine** -> **VM instances**
    * Click **CREATE INSTANCE**j
    * Name your VM, e.g., **vertex-vision-ai-vm**
    * Select region **us-central1 (Iowa)** and select any **Zone**
    * In **Identity and API access** select **Allow full access to all Cloud APIs**
    * In **Firewall** select **Allow HTTPS traffic**
    * Use defaults for all other values or adapt for your specific needs
    * Click **CREATE**
    * Once created select **SSH** from VM instances console

6. Set up authentication:

    * Set gcloud command line:
    
        ```
        gcloud auth login  (login as you for user rights to amend policy)

        gcloud init -- set project and region
        ```
    * Create the service account:
    
        ```
        gcloud iam service-accounts create NAME
        ```
        Replace **NAME** with a name for the service account.
        
    * Grant roles to the service account. Run the following command once for each of the following IAM roles: *roles/visionai.editor*:
    
        ```
        gcloud projects add-iam-policy-binding PROJECT_ID --member="serviceAccount:SERVICE_ACCOUNT_NAME@PROJECT_ID.iam.gserviceaccount.com" --role=ROLE
        ```
        Replace the following:

       * **SERVICE_ACCOUNT_NAME**: the name of the service account
       * **PROJECT_ID**: the project ID where you created the service account
       * **ROLE**: the role to grant (roles/visionai.editor)
        
    * Generate the key file:
    
        ```
        gcloud iam service-accounts keys create FILE_NAME.json --iam-account=SERVICE_ACCOUNT_NAME@PROJECT_ID.iam.gserviceaccount.com
        ```
        Replace the following:

       * **FILE_NAME**: a name for the key file
       * **SERVICE_ACCOUNT_NAME**: the name of the service account
       * **PROJECT_ID**: the project ID where you created the service account

    * Set the environment variable GOOGLE_APPLICATION_CREDENTIALS to the path of the JSON file that contains your service account key. This variable only applies to your current shell session, so if you open a new session, set the variable again. Example: Linux or macOS
    
        ```
        export GOOGLE_APPLICATION_CREDENTIALS="KEY_PATH"
        ```
        Replace **KEY_PATH** with the path of the JSON file that contains your service account key.
        For example:
        
        ```
        export GOOGLE_APPLICATION_CREDENTIALS="/home/user/Downloads/service-account-file.json"
        ```
    
    * Install Vision SDK:

        ```
        sudo apt-get remove visionai

        wget https://github.com/google/visionai/releases/download/v0.0.4/visionai_0.0-4_amd64.deb

        sudo apt install ./visionai_0.0-4_amd64.deb

        vaictl --help
        ```
    * Install Scripts:
    
        Install Git and Clone Repo
    
        ```
        sudo apt-get install git

        git clone https://github.com/tgaillard1/vertex-ai-vision-setup.git

        cd vertex-ai-vision-setup

        cp -rf scripts/ /home/YOUR_LOCAL_USER/
        
        cd /home/YOUR_LOCAL_USER/scripts
        ```
        
        Change Variables in scripts.  In the video-import.sh script you will need to change Variables in CAPS section at the top of the script (outlined below)
            
        ```
        gcs_video_clone_location="gs://YOUR_GCS_TRANSFER_BUCKET"
        source="/home/YOUR_LOCAL_USER/YOUR_LOCAL_DIR_FOR_VIDEO_UPLOADS"
        dest="/home/YOUR_LOCAL_USER/YOUR_LOCAL_DESTINATION_DIR"
        project="YOUR_PROJECT_ID"
        region="us-central1"
        stream_id="YOUR_STREAM_ID"
        loop_timeout=90
        sleep_amount=2
        remove_amount=10
        ```
        You also need to change the permissions on the **video-import.sh** script to allow it to run.

	   ```
	   chmod 755 video-import.sh
        ```
       
       You can now test your script.  
       ```
        cd /home/YOUR_LOCAL_USER/scripts
        
        ./video-import.sh
        ```
       
       For best results manually put a mp4 file in the transfer GCS bucket you created and run the script.  In the default configuration it will run for ~95 seconds and then terminate.  To validate the upload:

        * Navigate to **console --> Vertex AI Vision --> Warehouses**
        * Select **VIEW ASSETS** for the Warehouse you are using for the stream, e.g., store1-video-warehouse
        * For the **Stream name** capture the full name of the steam from the face blur component, e.g., application-output-store1-application....
        * For the **Date range** select "All time"
        * Your Studio should look like this:
        ![Vertex-Warehous-Search](https://github.com/tgaillard1/vertex-ai-vision-setup/blob/main/images/warehouse-search.png)

        * Select the **SEARCH** button at the bottom of the console.
	
	   In the crontab script you will just need to change the path to reflect where you have stored the script.  Then you will just need to install the crontab:
                    
       ```
        contab -e (this enters vim mode to edit the cron)
        
        Insert (i) then paste in the contenxt of the crontab provided.  Then save crontab.  Currently set up to run every 3 mintues to allow for looping of uploaded videos.
	   ```
