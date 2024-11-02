"""
Main entry point for the Stream Filter Router.
"""

import click
import time
import logging
from router import StreamFilterRouter

@click.command()
@click.option('--flows-config', '-s', 
              default="config/flows.json",
              help="Path to flows configuration JSON file",
              type=click.Path(exists=True))
@click.option('--process-config', '-p',
              default="config/process.json",
              help="Path to process configuration JSON file",
              type=click.Path(exists=True))
def main(flows_config: str, process_config: str):
    """Main entry point for the Stream Filter Router."""
    router = StreamFilterRouter(flows_config, process_config)

    try:
        router.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        router.stop()
        logging.info("Stream Filter Router shutdown complete")

if __name__ == "__main__":
    main()
