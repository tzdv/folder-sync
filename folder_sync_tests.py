import time
import unittest
import tempfile
import folder_sync
import os
import shutil


class FolderSyncTest(unittest.TestCase):
    source_folder = None
    temp_dir = None
    log_file = None
    replica_folder = None
    test_dir = None

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_dir = os.path.join(cls.temp_dir, "Test Directory")
        shutil.copytree("Test Directory", cls.test_dir)
        cls.source_folder = os.path.join(cls.test_dir, "Source Folder")
        cls.replica_folder = os.path.join(cls.test_dir, "Replica Folder")
        cls.log_file = os.path.join(cls.test_dir, "log.txt")

        foldersync = folder_sync.FolderSync(cls.source_folder, cls.replica_folder)
        foldersync.run(cls.log_file, 10)
        time.sleep(5)
        foldersync.quit()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_dir)

    def test_invalid_source_path(self):
        with self.assertRaises(ValueError):
            foldersync = folder_sync.FolderSync("Invalid Source", self.replica_folder)
            foldersync.run(self.log_file, 10)

    def test_invalid_replica_path(self):
        with self.assertRaises(ValueError):
            foldersync = folder_sync.FolderSync(self.source_folder, "Invalid replica")
            foldersync.run(self.log_file, 10)

    def test_invalid_log_path(self):
        with self.assertRaises(ValueError):
            foldersync = folder_sync.FolderSync(self.source_folder, self.replica_folder)
            foldersync.run("Invalid log ", 10)

    def test_invalid_interval(self):
        with self.assertRaises(ValueError):
            foldersync = folder_sync.FolderSync(self.source_folder, self.replica_folder)
            foldersync.run(self.log_file, -5)

    def test_invalid_interval_string(self):
        with self.assertRaises(ValueError):
            foldersync = folder_sync.FolderSync(self.source_folder, self.replica_folder)
            foldersync.run(self.log_file, "Invalid interval")

    def test_source_path_not_directory(self):
        with self.assertRaises(ValueError):
            foldersync = folder_sync.FolderSync(self.log_file, self.replica_folder)
            foldersync.run(self.log_file, 10)

    def test_replica_path_not_directory(self):
        with self.assertRaises(ValueError):
            foldersync = folder_sync.FolderSync(self.replica_folder, self.log_file)
            foldersync.run(self.log_file, 10)

    def test_replica_folder_nested(self):
        nested_folder_path = os.path.join(self.replica_folder, "Nested Source Folder")
        os.mkdir(nested_folder_path)

        with self.assertRaises(ValueError):
            foldersync = folder_sync.FolderSync(nested_folder_path, self.replica_folder)
            foldersync.run(self.log_file, 10)

        shutil.rmtree(nested_folder_path)

    def test_source_folder_nested(self):
        nested_folder_path = os.path.join(self.source_folder, "Nested Source Folder")
        os.mkdir(nested_folder_path)

        with self.assertRaises(ValueError):
            foldersync = folder_sync.FolderSync(self.source_folder, nested_folder_path)
            foldersync.run(self.log_file, 10)

        shutil.rmtree(nested_folder_path)

    def test_folder_added(self):
        replica_folder_path = os.path.join(self.replica_folder, "Folder 1")
        source_folder_path = os.path.join(self.source_folder, "Folder 1")

        self.assertTrue(os.path.exists(replica_folder_path))
        self.assertTrue(os.path.exists(source_folder_path))

    def test_folder_deleted(self):
        source_folder_path = os.path.join(self.source_folder, "Folder 2")
        replica_folder_path = os.path.join(self.replica_folder, "Folder 2")

        self.assertFalse(os.path.exists(source_folder_path))
        self.assertFalse(os.path.exists(replica_folder_path))

    def test_file_changed(self):
        source_file_path = os.path.join(self.source_folder, "File 1.txt")
        replica_file_path = os.path.join(self.replica_folder, "File 1.txt")
        with open(source_file_path, 'r') as file:
            src_file_content = file.read()

        with open(replica_file_path, 'r') as file:
            replica_file_content = file.read()

        self.assertEqual(src_file_content, replica_file_content)

    def test_nested_folder_added(self):
        replica_folder_path = os.path.join(self.replica_folder, "Folder 1")
        source_folder_path = os.path.join(self.source_folder, "Folder 1")
        replica_nested_folder_path = os.path.join(replica_folder_path, "Nested folder 1")
        source_nested_folder_path = os.path.join(source_folder_path, "Nested folder 1")

        self.assertTrue(os.path.exists(replica_nested_folder_path))
        self.assertTrue(os.path.exists(source_nested_folder_path))

    def test_nested_folder_deleted(self):
        replica_folder_path = os.path.join(self.replica_folder, "Folder 3")
        source_folder_path = os.path.join(self.source_folder, "Folder 3")
        replica_nested_folder_path = os.path.join(replica_folder_path, "Nested folder 2")
        source_nested_folder_path = os.path.join(source_folder_path, "Nested folder 2")

        self.assertFalse(os.path.exists(replica_nested_folder_path))
        self.assertFalse(os.path.exists(source_nested_folder_path))

    def test_nested_file_changed(self):
        source_file_path = os.path.join(self.source_folder, "Folder 3")
        replica_file_path = os.path.join(self.replica_folder, "Folder 3")

        source_nested_file_path = os.path.join(source_file_path, "File 2.txt")
        replica_nested_file_path = os.path.join(replica_file_path, "File 2.txt")

        with open(source_nested_file_path, 'r') as file:
            src_file_content = file.read()

        with open(replica_nested_file_path, 'r') as file:
            replica_file_content = file.read()

        self.assertEqual(src_file_content, replica_file_content)


if __name__ == "__main__":
    unittest.main()
