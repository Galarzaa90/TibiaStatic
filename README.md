# TibiaStatic

An [aiohttp](https://docs.aiohttp.org/) server that acts as proxy for resources in `static.tibia.com`, serving them from
the server's disk, allowing images to be properly embedded in applications like Discord.

Note that in order to use this, this must be run from a publicly accessible location (i.e. with a public IP or a domain)

## Installing

### Using python

First you must install the required dependencies:

```shell
python -m pip install -r requirements.txt
```

Then you can run `main.py` to start it. It supports the following command line arguments:

| Argument               | Default       | Description                                           |
| ---------------------- | ------------- | ----------------------------------------------------- |
| `-p`, `--port`         | 8000          | The port where the HTTP server will be exposed to.    |
| `--help`               | --            | Shows information about the available options.        |

For example:

```shell
python main.py -p 7500
```

## Usage

When the server is running, any image in `static.tibia.com` can be fetched by replacing the URL with the server's
address.

| Server's Address | Tibia.com Resource                                        | Proxied URL                                                       |
| ---------------- | --------------------------------------------------------  | ----------------------------------------------------------------- |
| `localhost`      | https://static.tibia.com/images/forum/logo_hotsticky.gif  | `http://localhost/images/forum/logo_hotsticky.gif`                |
| `example.com`    | https://static.tibia.com/images/news/doubleloot_small.png | `https://example.com/images/news/doubleloot_small.png`            |

Prometheus metrics are available at `/metrics` on the same port as the server.

