"""Entry point for Protocol Bridge."""

from src.app import AppShell


def main() -> None:
    app = AppShell()
    app.run()


if __name__ == "__main__":
    main()
