#  Copyright (c) 2020. Allan Galarza
#  Unathorized copying of this file, via any medium is strictly prohibited
#  Propietary and confidential.
import logging
import mimetypes
import os
import datetime
from typing import NoReturn

import aiofiles
import aiohttp
import aiohttp.web
import click

__version__ = "v0.1.0"

# Ensure logs folder exists
import humanfriendly
from aiohttp import web

os.makedirs("logs", exist_ok=True)

# Logging optimization
logging.logThreads = 0
logging.logProcesses = 0
logging._srcfile = None

logging_formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_formatter)

log = logging.getLogger("tibiastatic")
log.setLevel(logging.DEBUG)
log.addHandler(console_handler)

routes = aiohttp.web.RouteTableDef()

STATIC_BASE_URL = "https://static.tibia.com/"

STORAGE_PATH = "storage/"

GUILD_LOGO_DURATION = datetime.timedelta(hours=12)


def get_modified_time(path):
    return datetime.datetime.fromtimestamp(os.path.getmtime(path))


@routes.get('/{path:.*}')
async def serve_image(request: aiohttp.web.Request):
    """Shows status information about the server."""
    path = request.match_info["path"]
    file_path = os.path.join(STORAGE_PATH, path)
    filename = os.path.basename(path)
    _, ext = os.path.splitext(path)
    if not ext:
        return aiohttp.web.Response(text="Path must be a file", status=403)
    try:
        async with aiofiles.open(file_path, mode="rb") as f:
            log.info(f"[{path}] Getting resource from disk")
            data = await f.read()
            now = datetime.datetime.now()
            if not ('guildlogos' in path and now-get_modified_time(file_path) > GUILD_LOGO_DURATION):
                content_type, _ = mimetypes.guess_type(filename)
                log.info(f"[{path}] Resource read from disk | {humanfriendly.format_size(len(data))}")
                return aiohttp.web.Response(body=data, content_type=content_type)
            log.info(f"[{path}] File exceeded age, fetching from static.tibia.com")
    except FileNotFoundError:
        log.info(f"[{path}] File not in disk, fetching from static.tibia.com")
    except Exception:
        log.exception(f"[{path}]")
    async with request.app["client_session"].get(f"{STATIC_BASE_URL}{path}") as response:
        if response.status == 200:
            filename = os.path.basename(path)
            directories = path.replace(filename, "")
            data = await response.read()
            log.info(f"[{path}] Resource fetched | {humanfriendly.format_size(len(data))}")
            os.makedirs(os.path.join(STORAGE_PATH, directories), exist_ok=True)
            async with aiofiles.open(file_path, mode="wb") as f:
                content_type = response.headers.get('content-type')
                await f.write(data)
                log.info(f"[{path}] Saving resource to disk")
            return aiohttp.web.Response(body=data, content_type=content_type)
    return aiohttp.web.Response(text=f"Could not find resource {path}", status=404)


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
    log.debug('Creating application')
    app = web.Application()
    log.debug('Adding routes')
    app.add_routes(routes)

    log.debug('Registering cleanup contexts')
    app.cleanup_ctx.append(client_session_ctx)

    log.debug('Application started')
    return app


@click.command()
@click.option('-p', '--port', type=click.IntRange(0, 65535), default=None, show_default=True,
              help="The port the server will listen to.")
@click.option('-h', '--path', default=None, help="The path were the server will be located.")
def main(port, path):
    """Starts the orchestrator service."""
    """Launches the server."""
    aiohttp.web.run_app(app_factory(), path=path, port=port)


if __name__ == "__main__":
    main()
