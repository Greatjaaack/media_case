import re

HEADERS: dict[str, str] = {
    'Host': 'www.youtube.com',
    'Cache-Control': 'max-age=0',
    'Sec-Ch-Ua': '"Chromium";v="121", "Not A(Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Full-Version': '""',
    'Sec-Ch-Ua-Arch': '""',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Ch-Ua-Platform-Version': '""',
    'Sec-Ch-Ua-Model': '""',
    'Sec-Ch-Ua-Bitness': '""',
    'Sec-Ch-Ua-Wow64': '?0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.160 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Service-Worker-Navigation-Preload': 'true',
    'X-Client-Data': 'COXaygE=',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Priority': 'u=0, i',
}

JSON_PATTERN: re.compile = re.compile(r'var ytInitialData = (?P<jsonData>{.*?});</script>')
