import argparse
import getpass
import sys
from key_locker.core import (
    add_entry, get_entry, delete_entry,
    list_entries, vault_exists, change_master_password
)


def ask_master(confirm=False) -> str:
    pw = getpass.getpass("Master password: ")
    if confirm:
        pw2 = getpass.getpass("Confirm master password: ")
        if pw != pw2:
            print("Passwords do not match.")
            sys.exit(1)
    return pw


def run_cli():
    parser = argparse.ArgumentParser(
        prog="keylocker",
        description="A simple encrypted password vault.",
    )

    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Add a new entry.")
    p_add.add_argument("name", help="Entry label (e.g. gmail, facebook)")
    p_add.add_argument("--username", "-u", default="")
    p_add.add_argument("--password", "-p", default="")
    p_add.add_argument("--note", "-n", default="")

    # get
    p_get = sub.add_parser("get", help="Retrieve an entry.")
    p_get.add_argument("name")

    # delete
    p_del = sub.add_parser("delete", help="Delete an entry.")
    p_del.add_argument("name")

    # list
    sub.add_parser("list", help="List all saved entries.")

    # change master password
    sub.add_parser("change-master", help="Change the master password.")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "add":
            is_new = not vault_exists()
            master = ask_master(confirm=is_new)
            username = args.username or input("Username: ")
            password = args.password or getpass.getpass("Password to store: ")
            note = args.note or input("Note (optional): ")
            add_entry(master, args.name, username, password, note)
            print(f"  Saved '{args.name}' successfully.")

        elif args.command == "get":
            master = ask_master()
            entry = get_entry(master, args.name)
            print(f"\n  Name     : {args.name}")
            print(f"  Username : {entry['username']}")
            print(f"  Password : {entry['password']}")
            if entry["note"]:
                print(f"  Note     : {entry['note']}")
            print()

        elif args.command == "delete":
            master = ask_master()
            delete_entry(master, args.name)
            print(f"  Deleted '{args.name}'.")

        elif args.command == "list":
            master = ask_master()
            entries = list_entries(master)
            if not entries:
                print("  No entries saved yet.")
            else:
                print(f"\n  {len(entries)} saved entries:")
                for name in entries:
                    print(f"    - {name}")
                print()

        elif args.command == "change-master":
            old = ask_master()
            new = ask_master(confirm=True)
            change_master_password(old, new)
            print("  Master password updated.")

    except ValueError as e:
        print(f"  Error: {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"  Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_cli()
