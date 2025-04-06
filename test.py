import requests
from bs4 import BeautifulSoup
from fpdf import FPDF

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

# Step 2: Set up the PDF
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=12)

# Step 3: Extract content and write to PDF
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

            # Write to PDF
            pdf.set_font("Arial", 'B', size=14)
            pdf.cell(0, 10, title, ln=True)
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 10, f"URL: {link}\n", align='L')
            pdf.multi_cell(0, 10, text, align='L')
            pdf.ln(10)

        else:
            print("No content found in expected container.")
    
    except Exception as e:
        print(f"Error while processing {link}: {e}")

# Step 4: Save the PDF
pdf.output("shl_product_pages.pdf")
print("\n✅ PDF saved as 'shl_product_pages.pdf'")
