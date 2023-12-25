import datetime
import json

from json_file import JSONFile
from paved_path import PavedPath
from scrape.recent import newest_scrape_from_folder

TEST_DATA_FOLDER = PavedPath("test_data")


class TestNewestScraperFromFolderTests:
    def tearDown(self) -> None:
        """Clean up the test data folder."""
        TEST_DATA_FOLDER.delete()

    """Tests for the newest_scrape_from_folder function."""

    def create_file(self, folder: PavedPath, file_number: int, number_of_entries: int) -> JSONFile:
        """Create a file with the given content in the given folder."""
        file = JSONFile(folder / f"{file_number}.json")
        folder.mkdir(parents=True, exist_ok=True)
        content = {"games": list(range(number_of_entries))}
        file.write_text(json.dumps(content))
        return file

    def test_one_folder_one_file_complete(self) -> None:
        """Test that the newest file is returned."""
        test_data_folder = PavedPath("test_data")
        folder = test_data_folder / datetime.datetime.now().astimezone()
        file = self.create_file(folder, 0, 10)

        assert newest_scrape_from_folder(test_data_folder) == file.aware_mtime()
        test_data_folder.delete()

    def test_one_folder_single_file_incomplete(self) -> None:
        """Test that the newest file is returned."""
        test_data_folder = PavedPath("test_data")
        folder = test_data_folder / datetime.datetime.now().astimezone()

        self.create_file(folder, 0, 100)

        assert newest_scrape_from_folder(test_data_folder) is None
        test_data_folder.delete()

    def test_one_folder_multiple_files_complete(self) -> None:
        """Test that the newest file is returned."""
        test_data_folder = PavedPath("test_data")
        folder = test_data_folder / datetime.datetime.now().astimezone()

        self.create_file(folder, 0, 100)
        file = self.create_file(folder, 10, 10)

        assert newest_scrape_from_folder(test_data_folder) == file.aware_mtime()
        test_data_folder.delete()

    def test_one_folder_multiple_files_incomplete(self) -> None:
        """Test that the newest file is returned."""
        test_data_folder = PavedPath("test_data")
        folder = test_data_folder / datetime.datetime.now().astimezone()

        self.create_file(folder, 0, 100)
        self.create_file(folder, 10, 100)

        assert newest_scrape_from_folder(test_data_folder) is None
        test_data_folder.delete()

    def test_multiple_folders_one_file_complete(self) -> None:
        """Test that the newest file is returned."""
        test_data_folder = PavedPath("test_data")
        folder = test_data_folder / datetime.datetime.now().astimezone()
        file = self.create_file(folder, 0, 10)

        folder = test_data_folder / datetime.datetime.now().astimezone()
        self.create_file(folder, 0, 100)

        assert newest_scrape_from_folder(test_data_folder) == file.aware_mtime()
        test_data_folder.delete()

    def test_multiple_folders_one_file_incomplete(self) -> None:
        """Test that the newest file is returned."""
        test_data_folder = PavedPath("test_data")
        folder = test_data_folder / datetime.datetime.now().astimezone()
        self.create_file(folder, 0, 100)

        folder = test_data_folder / datetime.datetime.now().astimezone()
        self.create_file(folder, 0, 100)

        assert newest_scrape_from_folder(test_data_folder) is None
        test_data_folder.delete()
