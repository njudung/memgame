import click
from . import logger
from .game import Game


@click.command()
@click.option('--debug', is_flag=True, default=False, help="Run in debug mode.")
def run(debug):
    if debug:
        import logging
        logger.setLevel(logging.DEBUG)

    game = Game()
    game.run()


if __name__ == "__main__":
    run()