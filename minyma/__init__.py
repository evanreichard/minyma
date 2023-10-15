import click
import signal
import sys
from importlib.metadata import version
from minyma.config import Config
from minyma.oai import OpenAIConnector
from minyma.vdb import ChromaDB
from flask import Flask
from flask.cli import FlaskGroup

__version__ = version("minyma")

def signal_handler(sig, frame):
    sys.exit(0)


def create_app():
    global oai, cdb

    import minyma.api.common as api_common
    import minyma.api.v1 as api_v1

    app = Flask(__name__)
    cdb = ChromaDB(Config.DATA_PATH)
    oai = OpenAIConnector(Config.OPENAI_API_KEY, cdb)

    app.register_blueprint(api_common.bp)
    app.register_blueprint(api_v1.bp)

    return app


@click.group()
def cli():
    """Minyma CLI"""


@cli.group(cls=FlaskGroup, create_app=create_app)
def server():
    """Minyma flask server"""


@cli.command()
@click.option('--filename', type=click.File('r'), required=True)
@click.option('--normalizer', help="pubmed", required=True)
@click.option('--database', help="chroma", required=True)
@click.option('--datapath', type=click.Path(), help="database datapath", required=False)
def normalize(filename, normalizer, database, datapath):
    """Minyma data normalizer & loader"""

    database = database.lower()
    normalizer = normalizer.lower()

    # Validate Database
    if database == "chroma":
        if datapath is None:
            return print("INVALID DATAPATH")
        vdb = ChromaDB(datapath)
    else:
        return print("INVALID DATABASE:", database)

    # Select Normalizer
    if normalizer == "pubmed":
        from minyma.normalizer import PubMedNormalizer
        norm = PubMedNormalizer(filename)
    else:
        return print("INVALID NORMALIZER:", normalizer)

    # Process Data
    vdb.load_documents(norm)


signal.signal(signal.SIGINT, signal_handler)
