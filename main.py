#  Copyright (c) 2019. Allan Galarza
#  Unathorized copying of this file, via any medium is strictly prohibited
#  Propietary and confidential.
import asyncio
import datetime as dt
import logging
import mimetypes
import os
import platform
from collections import deque
from logging.handlers import TimedRotatingFileHandler
from typing import NoReturn

import aiofiles
import aiohttp
import aiohttp.web
import click
import pkg_resources

__version__ = "v1.2.1"

# Ensure logs folder exists
from aiohttp import web

os.makedirs("logs", exist_ok=True)

# Logging optimization
logging.logThreads = 0
logging.logProcesses = 0
logging._srcfile = None

logging_formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_formatter)

log = logging.getLogger("orchestrator")
log.setLevel(logging.DEBUG)
log.addHandler(console_handler)

routes = aiohttp.web.RouteTableDef()

STATIC_BASE_URL = "https://static.tibia.com/"

@routes.get('/{path:.*}')
async def get_status(request: aiohttp.web.Request):
    """Shows status information about the server."""
    path = request.match_info["path"]
    log.info(f"Path: {path}")
    data = None
    content_type = None
    filename = os.path.basename(path)
    route = path.replace(filename, "")
    _, ext = os.path.splitext(path)
    if not ext:
        return aiohttp.web.Response(status=404)
    if os.path.exists(path):
        log.info("Getting resource from disk")
        async with aiofiles.open(path, mode="rb") as f:
            data = await f.read()
            content_type, _ = mimetypes.guess_type(filename)
            return aiohttp.web.Response(body=data, content_type=content_type)
    else:
        log.info("Fetching resource from static.tibia.com...")
        async with request.app["client_session"].get(f"{STATIC_BASE_URL}{path}") as response:
            if response.status == 200:
                filename = os.path.basename(path)
                directories = path.replace(filename, "")
                os.makedirs(directories, exist_ok=True)
                f = await aiofiles.open(path, mode="wb")
                content_type = response.headers.get('content-type')
                data = await response.read()
                log.info("Resource fetched")
                log.info("Saving resource to disk")
                await f.write(data)
                await f.close()
        return aiohttp.web.Response(body=data, content_type=content_type)


async def client_session_ctx(app: web.Application) -> NoReturn:
    """
    Cleanup context async generator to create and properly close aiohttp ClientSession

    Ref.:

        > https://docs.aiohttp.org/en/stable/web_advanced.html#cleanup-context
        > https://docs.aiohttp.org/en/stable/web_advanced.html#aiohttp-web-signals
        > https://docs.aiohttp.org/en/stable/web_advanced.html#data-sharing-aka-no-singletons-please
    """
    log.debug('Creating ClientSession')
    app['client_session'] = aiohttp.ClientSession()

    yield

    log.debug('Closing ClientSession')
    await app['client_session'].close()


async def app_factory() -> web.Application:
    """
    See: https://docs.aiohttp.org/en/stable/web_advanced.html
    """
    log.debug('[APP Factory] Creating Application (entering APP Factory)')
    app = web.Application()

    log.debug('[APP Factory] Adding Routes')
    app.add_routes(routes)

    log.debug('[APP Factory] Registering Cleanup contexts')
    app.cleanup_ctx.append(client_session_ctx)

    log.debug('[APP Factory] APP is now prepared and can be returned by APP Factory')
    return app


@click.command()
@click.option('--debug', is_flag=True, help="Whether to show debugging messages or not.")
@click.option('--quiet', is_flag=True, help="Whether to hide information messages in console.")
@click.option('-p', '--port', type=click.IntRange(0, 65535), default=7700, show_default=True,
              help="The port the server will listen to.")
@click.option('-g', '--logpath', type=click.Path(file_okay=False),
              help="The directory where logs will be stored.")
def main(debug, quiet, port, logpath):
    """Starts the orchestrator service."""
    """Launches the worker."""
    if debug:
        log.setLevel(logging.DEBUG)
    if quiet:
        console_handler.setLevel(logging.WARNING)

    if logpath is None:
        logpath = 'logs'
    os.makedirs(logpath, exist_ok=True)

    file_handler = TimedRotatingFileHandler(os.path.join(logpath, "worker"), when='midnight')
    file_handler.suffix = "%Y_%m_%d.log"
    file_handler.setFormatter(logging_formatter)
    log.addHandler(file_handler)

    aiohttp.web.run_app(app_factory())


if __name__ == "__main__":
    main()
