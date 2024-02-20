import asyncio
from typing import List
import httpx
import json
from parsel import Selector

async def fetch_property_data(client, url):
    response = await client.get(url)
    if response.status_code != 200:
        print(f"Request blocked or failed for {url}")
        return None
    selector = Selector(response.text)
    data = selector.css("script#__NEXT_DATA__::text").get()
    data = json.loads(data)
    print(data.keys())
    
    # if data:
    #     data = json.loads(data)
    #     property_data = data.get("props", {}).get("pageProps", {}).get("componentProps", {}).get("gdpClientCache", {})
    #     if property_data:
    #         property_data = property_data[next(iter(property_data))].get('property', {})
    # else:
    #     data = selector.css("script#hdpApolloPreloadedData::text").get()
    #     if data:
    #         data = json.loads(json.loads(data).get("apiCache", "{}"))
    #         property_data = next(iter(v.get("property", {}) for k, v in data.items() if "ForSale" in k), None)
    # return property_data

async def scrape_properties(urls: List[str]):
    async with httpx.AsyncClient(
        http2=True,
        headers={
            "accept-language": "en-US,en;q=0.9",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
        },
    ) as client:
        tasks = [fetch_property_data(client, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [result for result in results if result is not None]

async def run():
    data = await scrape_properties([
        "https://www.zillow.com/homedetails/98-Greene-St-FLOOR-2-New-York-NY-10012/340032315_zpid/"
    ])
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    asyncio.run(run())