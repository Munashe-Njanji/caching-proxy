# Caching Proxy(https://roadmap.sh/projects/caching-server)

This is a simple asynchronous proxy  built with Python and aiohttp. It sends requests to a specified server and caches and logs the responses.

## Features
- Asynchronous HTTP requests using aiohttp
- Configurable proxy URL
- Detailed logging of requests and responses
- Error handling and timeout management
## Requirements
- Python 3.7+
- aiohttp
## Installation
1. Clone this repository:
```bash
git clone https://github.com/yourusername/proxy-client.git
cd proxy-client
```
2. Install the required packages:
```bash
pip install aiohttp
```
## Usage
1. Ensure your proxy server is running and accessible.
```bash
python proxy_server.py --port 3002 --origin https://dummyjson.com
```
or
```bash
python proxy_server.py --port 3002 --origin https://example.com
```
2. Run the client script:
```bash
python proxy_client.py
```
3. When prompted, enter the proxy URL (e.g., `http://localhost:3002`).

4. The client will send requests to the following endpoints:
- /products
- /users
- /todos
- /carts
- /posts
- /comments

5. Check the console output for detailed logs of each request and response.

## Configuration

You can modify the `urls` list in the `__main__` section of the script to change the endpoints the client requests.

## Troubleshooting

If you encounter connection issues:

1. Verify that your proxy server is running and accessible.
2. Check for any firewall or antivirus software that might be blocking the connection.
3. Ensure the proxy server is binding to the correct address (0.0.0.0 or localhost).
4. Try increasing the timeout values in the `aiohttp.ClientTimeout` configuration.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
