import httpx
from bs4 import BeautifulSoup

USER_AGENT = "GetnetMultiagentChallenge/0.1 (RAG ingestion; contact via project README)"


async def fetch_page_text(url: str, client: httpx.AsyncClient) -> str:
    """Fetch a page and extract its main readable text, stripping nav,
    footer, script and style noise so chunks are mostly prose."""
    response = await client.get(url, headers={"User-Agent": USER_AGENT}, follow_redirects=True)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    non_empty_lines = [line for line in lines if line]
    return "\n".join(non_empty_lines)
