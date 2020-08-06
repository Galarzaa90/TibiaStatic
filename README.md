# TibiaStatic
An [aiohttp](https://docs.aiohttp.org/) server that acts as proxy for resources in `static.tibia.com`, 
serving them from the server's disk, allowing images to be properly embedded.

## Usage
When the server is running, any image in `static.tibia.com` can be fetched by replacing the URL with the server's address.

| Server's Address | Tibia.com Resource                                        | Proxied URL                                                       |
| ---------------- | --------------------------------------------------------  | ----------------------------------------------------------------- |
| `localhost`      | https://static.tibia.com/images/forum/logo_hotsticky.gif  | `http://localhost/images/forum/logo_hotsticky.gif`                |
| `example.com`    | https://static.tibia.com/images/news/doubleloot_small.png | `https://example.com/images/news/doubleloot_small.png`            |


