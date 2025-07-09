import json
import re
import os
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.tokenize import sent_tokenize, word_tokenize
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline
from nltk.corpus import stopwords
from collections import Counter
from wordcloud import WordCloud



with open("AVGO_10-k.json", "r", encoding="utf-8") as f:
    items = json.load(f)

risk_text = items['Item 1A']

sentences = sent_tokenize(risk_text)

model_name = "yiyanghkust/finbert-tone"
finbert = pipeline("sentiment-analysis", model=model_name, tokenizer=model_name)

# 영어 불용어(stopwords) 불러오기
stop_words = set(stopwords.words('english'))

# 네거티브 문장 수집
negative_sentences = [sent for sent in sentences if finbert(sent)[0]['label'] == 'Negative']

# 모든 단어 추출 및 정제
words = []
for sent in negative_sentences:
    sent = re.sub(r'[^a-zA-Z\s]', '', sent)  # 특수문자 제거
    for word in word_tokenize(sent.lower()):
        if word not in stop_words and len(word) > 2:
            words.append(word)

# 단어들을 하나의 문자열로 합침
text_for_wordcloud = ' '.join(words)
font_path = "C:\\Windows\\Fonts\\times.ttf"

# WordCloud 생성
wordcloud = WordCloud(
    width=800,
    height=400,
    background_color='white',
    colormap='Reds',
    font_path=font_path  
).generate(text_for_wordcloud)

# 시각화
plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title("Negative Sentiment Keywords in Item 1A (Risk Factors)", fontsize=16)
plt.tight_layout()
plt.show()
