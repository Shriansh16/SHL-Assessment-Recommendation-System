import requests
from bs4 import BeautifulSoup

base_url = "https://www.shl.com/solutions/products/product-catalog/"
results = []

# Step 1: Collect all product page links
for page in range(12):
    start_value = page * 12
    url = f"{base_url}?start={start_value}&type=2"
    print(f"Scraping listing page: {url}")
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        continue
    
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.select("td.custom__table-heading__title a")
    
    for link in links:
        href = link.get("href")
        if href:
            full_url = requests.compat.urljoin(base_url, href)
            results.append(full_url)

# Step 2: Extract content and write to text file
with open("shl_product_pages.txt", "w", encoding="utf-8") as f:
    for link in results:
        print(f"\nExtracting content from: {link}")
        try:
            response = requests.get(link)
            if response.status_code != 200:
                print(f"Failed to fetch {link}")
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            container = soup.find("div", class_="product-catalogue module")

            if container:
                # Try getting the title of the page
                title_tag = soup.find("h1") or soup.find("title")
                title = title_tag.get_text(strip=True) if title_tag else "No Title"

                text = container.get_text(separator="\n", strip=True)

                # Write to text file
                f.write(f"Title: {title}\n")
                f.write(f"URL: {link}\n")
                f.write(text)
                f.write("\n\n" + "="*80 + "\n\n")  # separator between products
            
            else:
                print("No content found in expected container.")
                f.write(f"URL: {link} - No content found\n\n")
        
        except Exception as e:
            print(f"Error while processing {link}: {e}")
            f.write(f"Error processing URL: {link} - {str(e)}\n\n")

print("\n✅ Text file saved as 'shl_product_pages.txt'")