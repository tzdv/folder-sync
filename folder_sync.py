import logging
import os
import shutil
import hashlib
import time
import threading
import argparse


class FolderSync:
    def __init__(self, source_folder_path, replica_folder_path):
        self.source_folder_path = source_folder_path
        self.replica_folder_path = replica_folder_path
        self.should_run = True

    def get_file_hash(self, file_path):
        with open(file_path, "rb") as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)

        file_md5_hash = file_hash.hexdigest()
        return file_md5_hash

    def traverse_files(self, source_folder, files_to_exclude):
        items = {}
        for item in os.walk(source_folder):
            directory = item[0]
            files = [file for file in item[2] if file not in files_to_exclude]
            items[directory] = files
        return items

    def check_for_changes(self, source_items, replica_items):
        for path, files in source_items.items():
            replica_folder_path = path.replace(self.source_folder_path, self.replica_folder_path)
            if replica_folder_path not in replica_items:
                try:
                    os.mkdir(replica_folder_path)
                    logging.info("New folder: %s", path)
                except Exception as e:
                    logging.warning("Could not sync new folder: %s", e)
            for file in files:
                source_file_path = os.path.join(path, file)
                replica_file_path = os.path.join(replica_folder_path, file)
                if not os.path.exists(replica_file_path):
                    try:
                        shutil.copy2(source_file_path, replica_folder_path)
                        logging.info("New file: %s", source_file_path)
                    except Exception as e:
                        logging.warning("Could not sync new file: %s", e)

                else:
                    source_file_date_modified = os.path.getmtime(source_file_path)
                    replica_file_date_modified = os.path.getmtime(replica_file_path)

                    if source_file_date_modified != replica_file_date_modified:
                        try:
                            source_file_hash = self.get_file_hash(source_file_path)
                            replica_file_hash = self.get_file_hash(replica_file_path)
                            if source_file_hash != replica_file_hash:
                                os.remove(replica_file_path)
                                shutil.copy2(source_file_path, replica_file_path)
                                logging.info("Changed file: %s", source_file_path)
                        except Exception as e:
                            logging.warning("Could not sync file change: %s", e)

    def check_for_deletions(self, source_items, replica_items):
        for path, files in replica_items.items():
            source_folder_path = path.replace(self.replica_folder_path, self.source_folder_path)
            for file in files:
                replica_file_path = os.path.join(path, file)
                source_file_path = os.path.join(source_folder_path, file)
                if not os.path.exists(source_file_path):
                    try:
                        os.remove(replica_file_path)
                        logging.info("File deleted: %s", source_file_path)
                    except Exception as e:
                        logging.warning(f"Could not sync file deletion: %s", e)
            if source_folder_path not in source_items:
                try:
                    shutil.rmtree(path)
                    logging.info("Folder deleted: %s", path)
                except Exception as e:
                    logging.warning(f"Could not sync folder deletion: %s", e)

    def sync_files(self, source_items, replica_items):
        logging.info("Syncing files...")
        t1 = threading.Thread(target=self.check_for_changes, args=(source_items, replica_items))
        t2 = threading.Thread(target=self.check_for_deletions, args=(source_items, replica_items))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        logging.info("Syncing finished")

    def validate_inputs(self, log_file_path, interval):
        if not os.path.exists(self.source_folder_path):
            raise ValueError("Source folder does not exist")
        if not os.path.exists(self.replica_folder_path):
            raise ValueError("Replica folder does not exist")
        if not os.path.exists(log_file_path):
            raise ValueError("Log file path does not exist")
        if not os.path.isdir(self.source_folder_path):
            raise ValueError("Source folder is not directory")
        if not os.path.isdir(self.replica_folder_path):
            raise ValueError("Replica folder is not directory")
        if self.source_folder_path.startswith(self.replica_folder_path) or self.replica_folder_path.startswith(
                self.source_folder_path):
            raise ValueError("Source and replica folders are nested")
        if not isinstance(interval, int) or interval <= 0:
            raise ValueError("Interval must be a positive number ")

    def continuous_sync(self, interval, excluded_files):
        while self.should_run:
            source_items = self.traverse_files(self.source_folder_path, excluded_files)
            replica_items = self.traverse_files(self.replica_folder_path, excluded_files)
            self.sync_files(source_items, replica_items)
            time.sleep(interval)

    def run(self, log_file_path, interval, excluded_files=None):
        self.validate_inputs(log_file_path, interval)
        if excluded_files is None:
            excluded_files = []

        logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode="w",
                            format="%(asctime)s - %(levelname)s - %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)

        logging.getLogger().addHandler(console_handler)
        logging.info("Program started")
        thread = threading.Thread(target=self.continuous_sync, args=(interval, excluded_files))
        thread.start()

    def quit(self):
        self.should_run = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sync file folders.')
    parser.add_argument('source', metavar='source', type=str, help='your source folder path')
    parser.add_argument('replica', metavar='replica', type=str, help='your replica folder path')
    parser.add_argument('log', metavar='log', type=str, help='your log file path')
    parser.add_argument('interval', metavar='interval', type=int, help='interval of syncing')
    parser.add_argument('--ef', metavar='ef', type=str, nargs='+', help='files to exclude')
    args = parser.parse_args()
    folder_sync = FolderSync(args.source, args.replica)
    folder_sync.run(args.log, args.interval, args.ef)
