import aiohttp
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ProxyClient:
    def __init__(self, proxy_url):
        self.proxy_url = proxy_url

    async def send_request(self, session, endpoint):
        full_url = f'{self.proxy_url}{endpoint}'
        logging.info(f'Requesting {full_url}')

        try:
            async with session.get(full_url) as response:
                logging.info(f'Response received for {full_url}')
                logging.info(f'Response status code: {response.status}')
                logging.info(f'Response headers: {response.headers}')

                content = await response.read()
                logging.info(f'Response content length: {len(content)} bytes')

                if response.status == 200:
                    text = content.decode('utf-8', errors='replace')
                    logging.info(f'Response content (first 100 chars): {text[:100]}...')
                else:
                    logging.error(f'Error: {response.status}, {response.reason}')

        except aiohttp.ClientError as e:
            logging.error(f'Request failed: {e}')
            logging.debug(f'Error details: {type(e).__name__}: {str(e)}')
        except asyncio.TimeoutError:
            logging.error(f'Request timed out for {full_url}')
        except Exception as e:
            logging.exception(f'Unexpected error occurred: {e}')

        logging.info('\n')

    async def fetch_all(self, endpoints):
        timeout = aiohttp.ClientTimeout(total=60, connect=10, sock_read=30)
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            for endpoint in endpoints:
                await self.send_request(session, endpoint)
                await asyncio.sleep(0.001)

if __name__ == '__main__':
    proxy_url = input("Enter the proxy URL (e.g., http://localhost:3002): ")
    client = ProxyClient(proxy_url)

    urls = [
        '/products',
        '/users',
        '/todos',
        '/carts',
        '/posts',
        '/comments'
    ]

    try:
        asyncio.run(client.fetch_all(urls))
    except Exception as e:
        logging.exception(f"Main execution failed: {e}")
