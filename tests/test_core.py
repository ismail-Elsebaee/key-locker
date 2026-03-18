import sys
import os
import unittest
import tempfile
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from key_locker.core import (
    add_entry, get_entry, delete_entry,
    list_entries, change_master_password, save_vault, load_vault
)


# redirect vault to a temp file during tests
def temp_vault_path(tmp_dir):
    return Path(tmp_dir) / "test_vault.dat"


class TestVault(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.patcher = patch(
            "key_locker.core.get_vault_path",
            return_value=temp_vault_path(self.tmp)
        )
        self.patcher.start()
        self.master = "TestMaster123!"

    def tearDown(self):
        self.patcher.stop()

    def test_add_and_get(self):
        add_entry(self.master, "gmail", "user@gmail.com", "secret123")
        entry = get_entry(self.master, "gmail")
        self.assertEqual(entry["username"], "user@gmail.com")
        self.assertEqual(entry["password"], "secret123")

    def test_list_entries(self):
        add_entry(self.master, "gmail", "u1", "p1")
        add_entry(self.master, "facebook", "u2", "p2")
        entries = list_entries(self.master)
        self.assertIn("gmail", entries)
        self.assertIn("facebook", entries)

    def test_delete_entry(self):
        add_entry(self.master, "twitter", "u", "p")
        delete_entry(self.master, "twitter")
        with self.assertRaises(KeyError):
            get_entry(self.master, "twitter")

    def test_wrong_master_password(self):
        add_entry(self.master, "github", "u", "p")
        with self.assertRaises(ValueError):
            load_vault("wrong_password")

    def test_entry_name_lowercase(self):
        add_entry(self.master, "GMAIL", "u", "p")
        entry = get_entry(self.master, "gmail")
        self.assertIsNotNone(entry)

    def test_empty_name_raises(self):
        with self.assertRaises(ValueError):
            add_entry(self.master, "  ", "u", "p")

    def test_change_master_password(self):
        add_entry(self.master, "netflix", "u", "p")
        new_master = "NewMaster456!"
        change_master_password(self.master, new_master)
        entry = get_entry(new_master, "netflix")
        self.assertEqual(entry["password"], "p")

    def test_note_saved(self):
        add_entry(self.master, "work", "u", "p", note="work laptop login")
        entry = get_entry(self.master, "work")
        self.assertEqual(entry["note"], "work laptop login")


if __name__ == "__main__":
    unittest.main()
