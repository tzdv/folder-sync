# Folder sync

## How to run

1. Clone this repo:

         git clone https://github.com/tzdv/folder-sync

2. Navigate to source folder:

         cd folder-sync

3. Start the script by providing command line arguments as follows:

         python3 folder_sync.py "/Your/path/to/Source Folder" "/Your/path/to/Replica Folder" "/Your/path/to/Log Folder/my_log.txt" 10
    You can replace 10 with your sync interval (seconds).
      
    If you want to exclude files you can provide optional --ef command line with the list of file names to exclude:

          python3 folder_sync.py "/Your/path/to/Source Folder" "/Your/path/to/Replica Folder" "/Your/path/to/Log Folder/my_log.txt" 10 --ef "file to exclude.txt"

5. If provided details are valid the script should now start syncing directories