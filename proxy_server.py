import aiohttp
import asyncio
import json
import logging
from aiohttp import web
from typing import Dict, Optional
import os

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('proxy_server.log'),
                        logging.StreamHandler()
                    ])

class CacheManager:
    def __init__(self) -> None:
        self.cache: Dict[str, Dict[str, str]] = {}
        self.cache_file = 'cache_data.json'
        self.load_cache()

    def get_cached_response(self, url: str) -> Optional[Dict[str, str]]:
        cached_response = self.cache.get(url)
        if cached_response:
            logging.info(f'Cache HIT: {url}')
        else:
            logging.info(f'Cache MISS: {url}')
        return cached_response

    def cache_response(self, url: str, content: str, headers: Dict[str, str]) -> None:
        self.cache[url] = {
            'headers': dict(headers),
            'content': content
        }
        self.save_cache()
        logging.info(f'CACHED: {url}')

    def load_cache(self) -> None:
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                logging.info(f'Cache loaded from {self.cache_file}')
            else:
                logging.info(f'Cache file {self.cache_file} not found. Starting with empty cache.')
        except json.JSONDecodeError:
            logging.error(f'Error decoding JSON from {self.cache_file}. Starting with empty cache.')
        except Exception as e:
            logging.error(f'Error loading cache: {str(e)}. Starting with empty cache.')

    def save_cache(self) -> None:
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
            logging.info(f'Cache saved to {self.cache_file}')
        except Exception as e:
            logging.error(f'Error saving cache: {str(e)}')

    def clear_cache(self) -> None:
        self.cache.clear()
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)
        logging.info('Cache cleared')

async def handle_request(request: web.Request, cache_manager: CacheManager, origin: str) -> web.Response:
    url = request.path
    logging.info(f'Incoming request for: {url}')
    cached_response = cache_manager.get_cached_response(url)

    if cached_response:
        logging.info(f'Serving cached response for: {url}')
        return web.Response(body=cached_response['content'], headers=cached_response['headers'], status=200)

    origin_url = f'{origin}{url}'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(origin_url) as response:
                logging.info(f'Forwarding request to: {origin_url}')
                content = await response.text()
                headers = dict(response.headers)
                if response.status == 200:
                    cache_manager.cache_response(url, content, headers)
                return web.Response(body=content, headers=headers, status=response.status)
    except Exception as e:
        logging.error(f'Error forwarding request to {origin_url}: {str(e)}')
        return web.Response(text=f"Error: {str(e)}", status=500)

async def start_proxy_server(port: int, origin: str) -> None:
    cache_manager = CacheManager()
    app = web.Application()

    app.router.add_get('/{tail:.*}', lambda request: handle_request(request, cache_manager, origin))
    logging.info(f'Starting proxy server on port {port}, forwarding requests to {origin}')
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', port)
    await site.start()

    print(f"Proxy server is running on http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print("Shutting down the server...")
    finally:
        await runner.cleanup()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='CLI-based caching proxy app')
    parser.add_argument('--port', type=int, required=True, help='Port number for the proxy server')
    parser.add_argument('--origin', type=str, required=True, help='URL of the origin server')
    parser.add_argument('--clear-cache', action='store_true', help='Clear the cache')
    args = parser.parse_args()

    cache_manager = CacheManager()

    if args.clear_cache:
        cache_manager.clear_cache()
    else:
        asyncio.run(start_proxy_server(args.port, args.origin))
