import requests
import re
from bs4 import BeautifulSoup


# Step 1: Obtain CIK information from a ticker 
def get_cik(ticker):
    url = 'https://www.sec.gov/files/company_tickers.json'
    res = requests.get(url, headers={'User-Agent': 'Shawn Jeong (shawn.jeongg@gmail.com)'})
    data = res.json()
    for entry in data.values():
        if entry['ticker'].lower() == ticker.lower():
            return str(entry['cik_str']).zfill(10)
    return None

# Step 2: Obtain 10-k using CIK
def get_latest_10k_info(cik):
    url = f'https://data.sec.gov/submissions/CIK{cik}.json'
    res = requests.get(url, headers={'User-Agent': 'Shawn Jeong (shawn.jeongg@gmail.com)'})
    data = res.json()

    forms = data['filings']['recent']['form']
    accession_nums = data['filings']['recent']['accessionNumber']
    primary_docs = data['filings']['recent']['primaryDocument']

    for form, accession, primary_doc in zip(forms, accession_nums, primary_docs):
        if form == '10-K':
            accession_clean = accession.replace('-', '')
            return {
                'accession': accession_clean,
                'primary_doc': primary_doc
            }
    return None

# Step 3: Obtain 10-k html information
def get_10k_html_url(cik, filing_info):
    accession = filing_info['accession']
    primary_doc = filing_info['primary_doc']
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{primary_doc}"

# Step 4: Extract 10-k in a big chunk of text and clean
def extract_items_from_10k(html_url):
    res = requests.get(html_url, headers={'User-Agent': 'Shawn Jeong (shawn.jeongg@gmail.com)'})
    # Parse with BeautifulSoup
    soup = BeautifulSoup(res.content, 'html.parser')

    # Clean unnessary noises from the parsed html
    for tag in soup.find_all(style=lambda s: s and 'display:none' in s):
        tag.decompose()

    for tag in soup(['script', 'style', 'ix:header', 'ix:nonnumeric', 'ix:nonfraction']):
        tag.decompose()

    
    text = soup.get_text(separator=' ')
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    
    return cleaned_text

# In 10-k, there is a table of content at the beginning so first occurence capturing won't work.
# Function below allows us to capture from the second occurrence.
def extract_section(text, start_pattern, end_pattern, start_index=1):
    start_matches = list(re.finditer(start_pattern, text, re.IGNORECASE))
    end_matches = list(re.finditer(end_pattern, text, re.IGNORECASE))

    if len(start_matches) > start_index and len(end_matches) > 0:
        start = start_matches[start_index].end()
        end = None
        for m in end_matches:
            if m.start() > start:
                end = m.start()
                break
        if end:
            return text[start:end]
    return None

# Step 5: Extract Item 1, Item 1A and Item 7 from the cleaned texts.
def extract_10k_items(cleaned_text):
    item1 = extract_section(cleaned_text,
                            r'Item\s+1\.*\s+Business',
                            r'Item\s+1A\.*\s+Risk\s+Factors')
    item1a = extract_section(cleaned_text,
                             r'Item\s+1A\.*\s+Risk\s+Factors',
                             r'Item\s+1B\.*')
    item7 = extract_section(cleaned_text,
                            r'Item\s+7\.*\s+Management[’\'`]?[sS]\s+Discussion.*?Operations',
                            r'Item\s+7A\.*')
    return {
        'Item 1': item1.strip() if item1 else "Not found",
        'Item 1A': item1a.strip() if item1a else "Not found",
        'Item 7': item7.strip() if item7 else "Not found"
    }

# Main() function
def main():
    ticker = 'AVGO'  # Example - Broadcom
    cik = get_cik(ticker)
    filing_info = get_latest_10k_info(cik)
    html_url = get_10k_html_url(cik, filing_info)
    clnd_txt = extract_items_from_10k(html_url)
    info_st = extract_10k_items(clnd_txt)
    
    print("\n\nItem 1 (Business)\n", info_st['Item 1'][:1000], "\n...")
    print("\n\nItem 1A (Risk Factors)\n", info_st['Item 1A'][:1000], "\n...")
    print("\n\nItem 7 (MD&A)\n", info_st['Item 7'][:1000], "\n...")

# Execution
if __name__ == '__main__':
    main()
