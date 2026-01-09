import asyncio
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup


async def search_web(query: str, max_results: int = 5) -> dict:
    search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        response = await client.get(search_url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for result in soup.select(".result__a", limit=max_results):
        results.append({"title": result.get_text(strip=True), "url": result.get("href")})

    return {"query": query, "results": results}


async def fetch_url(url: str, max_chars: int = 5000) -> dict:
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Убираем скрипты и стили
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    text = " ".join(text.split())[:max_chars]

    return {"url": url, "content": text}


def search_web_sync(query: str):
    return asyncio.run(search_web(query))


def fetch_url_sync(url: str):
    return asyncio.run(fetch_url(url))
