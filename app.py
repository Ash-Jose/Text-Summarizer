from flask import Flask, request, render_template
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest

app = Flask(__name__)

def summarizer(rawdocs, summary_ratio):
    stopwords = list(STOP_WORDS)
    NLP = spacy.load('en_core_web_sm')
    doc = NLP(rawdocs)

    # Calculate word frequency
    word_freq = {}
    for word in doc:
        if word.text.lower() not in stopwords and word.text.lower() not in punctuation:
            if word.text not in word_freq.keys():
                word_freq[word.text] = 1
            else:
                word_freq[word.text] += 1

    max_freq = max(word_freq.values())
    for word in word_freq.keys():
        word_freq[word] = word_freq[word] / max_freq

    # Scoring sentences
    sentence_tokens = [sentence for sentence in doc.sents]
    sent_scores = {}
    for sentence in sentence_tokens:
        for word in sentence:
            if word.text in word_freq.keys():
                if sentence not in sent_scores.keys():
                    sent_scores[sentence] = word_freq[word.text]
                else:
                    sent_scores[sentence] += word_freq[word.text]

    # Select top sentences based on user-defined ratio
    select_length = int(len(sentence_tokens) * summary_ratio)
    summary = nlargest(select_length, sent_scores, key=sent_scores.get)
    final_summary = [word.text for word in summary]
    summary = ' '.join(final_summary)

    return summary, len(rawdocs.split(' ')), len(summary.split(' '))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    raw_text = request.form['text']
    ratio = float(request.form['summary_ratio']) / 100  # Convert slider value to ratio
    summary, original_len, summary_len = summarizer(raw_text, ratio)
    return render_template('index.html', summary=summary, original_len=original_len, summary_len=summary_len, raw_text=raw_text, ratio=int(ratio * 100))

if __name__ == '__main__':
    app.run(debug=True)
