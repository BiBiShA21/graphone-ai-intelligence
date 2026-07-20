import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def debug_arxiv_detailed():
    url = "https://arxiv.org/list/cs.AI?skip=0&size=100"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            html = await response.text()
    
    print("=" * 80)
    print("ARXIV - WITH HEADERS")
    print("=" * 80)
    print(f"Response length: {len(html)} characters")
    print(f"Status: {response.status}")
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try multiple selectors
    print("\n1. Looking for 'a' with title='Abstract':")
    links = soup.find_all('a', {'title': 'Abstract'})
    print(f"   Found: {len(links)}")
    
    print("\n2. All 'a' tags (first 10):")
    all_a = soup.find_all('a')
    print(f"   Total a tags: {len(all_a)}")
    for a in all_a[:5]:
        print(f"   {a.get('href')}")
    
    print("\n3. Checking for arxiv.org URLs:")
    arxiv_urls = [a.get('href') for a in all_a if a.get('href') and 'arxiv' in a.get('href', '')]
    print(f"   Found: {len(arxiv_urls)}")
    for url in arxiv_urls[:5]:
        print(f"   {url}")
    
    print("\n4. First 500 chars of HTML:")
    print(html[:500])

async def debug_pwc_detailed():
    url = "https://paperswithcode.com/papers?q=ai&page=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            html = await response.text()
    
    print("\n" + "=" * 80)
    print("PAPERS WITH CODE - WITH HEADERS")
    print("=" * 80)
    print(f"Response length: {len(html)} characters")
    print(f"Status: {response.status}")
    
    soup = BeautifulSoup(html, 'html.parser')
    
    print("\n1. All 'a' tags (first 10):")
    all_a = soup.find_all('a')
    print(f"   Total a tags: {len(all_a)}")
    for a in all_a[:5]:
        print(f"   {a.get('href')}")
    
    print("\n2. Looking for '/paper/' in URLs:")
    paper_links = [a.get('href') for a in all_a if '/paper/' in a.get('href', '')]
    print(f"   Found: {len(paper_links)}")
    for link in paper_links[:5]:
        print(f"   {link}")
    
    print("\n3. First 500 chars of HTML:")
    print(html[:500])

async def main():
    await debug_arxiv_detailed()
    await debug_pwc_detailed()

if __name__ == "__main__":
    asyncio.run(main())
