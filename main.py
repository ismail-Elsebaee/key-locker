import sys


def main():
    if "--cli" in sys.argv:
        sys.argv.remove("--cli")
        from key_locker.cli import run_cli
        run_cli()
    else:
        from key_locker.gui import run_gui
        run_gui()


if __name__ == "__main__":
    main()
