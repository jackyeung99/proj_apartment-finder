import random
import asyncio
import json
import httpx
from loguru import logger as log
from parsel import Selector


async def _search(
    query: str,
    session: httpx.AsyncClient,
    filters: dict = None,
    categories=("cat1", "cat2"),
):
    """base search function which is used by sale and rent search functions"""
    html_response = await session.get(f"https://www.zillow.com/homes/{query}_rb/")
    assert html_response.status_code == 403, "request is blocked"
    selector = Selector(html_response.text)
    # find query data in script tags
    script_data = json.loads(
        selector.xpath("//script[@id='__NEXT_DATA__']/text()").get()
    )
    query_data = script_data["props"]["pageProps"]["searchPageState"]["queryState"]
    if filters:
        query_data["filterState"] = filters

    # scrape search API
    url = "https://www.zillow.com/async-create-search-page-state"
    found = []
    # cat1 - Agent Listings
    # cat2 - Other Listings
    for category in categories:
        full_query = {
            "searchQueryState": query_data,
            "wants": {category: ["mapResults"]},
            "requestId": random.randint(2, 10),
        }
        api_response = await session.put(
            url,
            headers={"content-type": "application/json"},
            body=json.dumps(full_query),
        )
        data = api_response.json()
        _total = data["categoryTotals"][category]["totalResultCount"]
        if _total > 500:
            log.warning(f"query has more results ({_total}) than 500 result limit ")
        else:
            log.info(f"found {_total} results for query: {query}")
        map_results = data[category]["searchResults"]["mapResults"]
        found.extend(map_results)
    return found


async def search_sale(query: str, session: httpx.AsyncClient):
    """search properties that are for sale"""
    log.info(f"scraping sale search for: {query}")
    return await _search(query=query, session=session)


async def search_rent(query: str, session: httpx.AsyncClient):
    """search properites that are for rent"""
    log.info(f"scraping rent search for: {query}")
    filters = {
        "isForSaleForeclosure": {"value": False},
        "isMultiFamily": {"value": False},
        "isAllHomes": {"value": True},
        "isAuction": {"value": False},
        "isNewConstruction": {"value": False},
        "isForRent": {"value": True},
        "isLotLand": {"value": False},
        "isManufactured": {"value": False},
        "isForSaleByOwner": {"value": False},
        "isComingSoon": {"value": False},
        "isForSaleByAgent": {"value": False},
    }
    return await _search(
        query=query, session=session, filters=filters, categories=["cat1"]
    )

BASE_HEADERS = {
"accept-language": "en-US,en;q=0.9",
"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
"accept-encoding": "gzip, deflate, br",
}   

async def run():
    limits = httpx.Limits(max_connections=5)
    async with httpx.AsyncClient(limits=limits, timeout=httpx.Timeout(15.0), headers=BASE_HEADERS) as session:
        data = await search_rent("New Haven, CT", session)
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    asyncio.run(run())