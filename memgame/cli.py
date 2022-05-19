import click
from . import logger
from .game import Game


@click.command()
@click.option("--debug", is_flag=True, default=False, help="Run in debug mode.")
@click.option("--kiosk", is_flag=True, default=False, help="Run in kiosk mode, (full screen).")
def run(debug, kiosk):
    if debug:
        import logging

        logger.setLevel(logging.DEBUG)

    game = Game(kiosk=kiosk)
    game.run()


if __name__ == "__main__":
    run()
