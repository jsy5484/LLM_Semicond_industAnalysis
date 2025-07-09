# Semiconductor Industry 10-K/10-Q Risk Text Analysis & Financial Performance Prediction

### Author: Shawn Jeong / Manuscript in progress

### Project Overview
This project focuses on analyzing risk disclosures within the 10-K and 10-Q filings of semiconductor companies submitted to the U.S. SEC.
Using advanced natural language processing techniques—including sentiment analysis and topic modeling—we extract key risk themes and their evolution over time.
The ultimate goal is to quantitatively link these textual risk factors to financial performance metrics such as ROA, ROE, EPS, and stock returns through regression modeling.

The semiconductor sector faces diverse and dynamic risk factors including supply chain disruptions, geopolitical tensions, regulatory changes, and rapid technological innovation.
Risk disclosures in SEC filings provide rich textual data reflecting these challenges, making this industry an ideal case for text-based risk analysis.

### Description
- Automated Data Collection of 10-K and 10-Q reports for semiconductor firms via SEC EDGAR
- Text Preprocessing: Tokenization, stopword removal, and sentence segmentation tailored for financial language
- Sentiment Analysis: Utilizing FinBERT for domain-specific risk sentiment scoring
- Topic Modeling: LDA to identify and track evolving risk themes unique to semiconductors
- Feature Engineering: Extraction of TF-IDF features, risk density, and topic distributions
- Regression Modeling: Predicting financial KPIs based on textual risk indicators
- Visualization: Industry-specific risk topic trends and sentiment over time


### Data 
- Input JSON files contain parsed Item 1A (Risk Factors) and Item 7 (MD&A) sections from EDGAR API
- Outputs include yearly sentiment scores, topic distributions, and regression results
- List of companies in the dataset: **Nvidia, Broadcom, AMD, Qualcomm, Intel, Micron, Microchip Technology, Texas Industry**

### Application
- Identification of semiconductor-specific risk themes such as supply chain, trade regulations, technology shifts, and market volatility
- Quantitative insights into how these risks impact financial performance
- Monitoring tools for investors and analysts tracking sector risk evolution

