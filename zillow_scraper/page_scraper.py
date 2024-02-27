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
    property_data = data.get("props", {}).get("pageProps", {}).get("componentProps", {}).get("gdpClientCache", {})
    print(property_data.keys())

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
    data = await scrape_properties(
        ['https://www.zillow.com/b/building/40.73873,-73.6003_ll/', 'https://www.zillow.com/b/building/40.74058,-73.58548_ll/', 'https://www.zillow.com/apartments/saratoga-springs-ny/saratoga-market-center/5XrYdh/', 'https://www.zillow.com/apartments/lynbrook-ny/the-cornerstone-yorkshire/97k3vj/', 'https://www.zillow.com/b/building/41.133896,-73.79311_ll/', 'https://www.zillow.com/apartments/ithaca-ny/library-place/BhQPQK/', r'https://www.zillow.com/apartments/east-moriches-ny/walden-pond.dash.-55%2b-community/5Xt4VP/', 'https://www.zillow.com/homedetails/32-Titus-Ct-13B4653E8-Rochester-NY-14617/340066443_zpid/', 'https://www.zillow.com/apartments/little-falls-ny/little-falls-garden-apartments/5Xm7Lp/', 'https://www.zillow.com/b/building/43.039852,-73.84325_ll/']
    )
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    asyncio.run(run())