"""Entry point for TCP Tactical Messenger."""

from src.app import AppShell


def main() -> None:
    app = AppShell()
    app.run()


if __name__ == "__main__":
    main()
