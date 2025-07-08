import requests
import re
import json    
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
def get_latest_filings_info(cik, count=3):
    url = f'https://data.sec.gov/submissions/CIK{cik}.json'
    res = requests.get(url, headers={'User-Agent': 'Shawn Jeong (shawn.jeongg@gmail.com)'})
    data = res.json()

    forms = data['filings']['recent']['form']
    accession_nums = data['filings']['recent']['accessionNumber']
    primary_docs = data['filings']['recent']['primaryDocument']
    filing_dates = data['filings']['recent']['filingDate']

    filings = []
    for form, accession, primary_doc, date in zip(forms, accession_nums, primary_docs, filing_dates):
        if form in ['10-K', '10-Q']:
            accession_clean = accession.replace('-', '')
            filings.append({
                'form': form,
                'accession': accession_clean,
                'primary_doc': primary_doc,
                'filing_date': date
            })
                      
            
            if len(filings) == count:
                break
    
    
    return filings

# Step 3: Obtain 10-k html information
def get_filing_html_url(cik, filing_info):
    accession = filing_info['accession']
    primary_doc = filing_info['primary_doc']
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{primary_doc}"

# Step 4: Extract 10-k in a big chunk of text and clean
def extract_clean_text(html_url):
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
        for m in end_matches:
            if m.start() > start:
                end = m.start()
                return text[start:end]
    return None

# Step 5: Extract Item 1, Item 1A and Item 7 from the cleaned texts.
def extract_item_1a_10Q(cleaned_text):
    item1 = extract_section(cleaned_text, r'Item\s+1A\.*\s+Risk\s+Factors', r'Item\s+2\.*')

    return {
        'Item 1': item1.strip() if item1 else "Not found",
    }

def extract_item_1a_10K(cleaned_text):
    item1 = extract_section(cleaned_text, r'Item\s+1A\.*\s+Risk\s+Factors', r'Item\s+1B\.*')

    return {
        'Item 1': item1.strip() if item1 else "Not found",
    }


# Main() function
def main():
    ticker = 'AVGO'
    cik = get_cik(ticker)
    filings = get_latest_filings_info(cik, count=3)
    
    
    results = []
    for filing_info in filings:
        html_url = get_filing_html_url(cik, filing_info)
        print(f"Processing: {html_url}")
        print(filing_info['form'])
        if filing_info['form'] == '10-Q':
            full_text = extract_clean_text(html_url)
            item_1a = extract_item_1a_10Q(full_text)
        else:
            full_text = extract_clean_text(html_url)
            item_1a = extract_item_1a_10K(full_text)
            
        result = {
            'ticker': ticker,
            'form': filing_info['form'],
            'filing_date': filing_info['filing_date'],
            'Item 1A': item_1a['Item 1'] if item_1a and 'Item 1' in item_1a else "Not found"
        }
        results.append(result)
        
        
    for i, filing in enumerate(results, 1):
        print(f"--- Filing {i} ---")
        for key, value in filing.items():
            print(f"{key:12}: {value}")
    
    
    
    with open(f"{ticker}_Item1A_combined.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    #print(f"\nExtracted Item 1A from latest {filing_info['form']} ({filing_info['filing_date']})")
    #print(result['Item 1A'][:1000], "\n...")

# Execution
if __name__ == '__main__':
    main()
