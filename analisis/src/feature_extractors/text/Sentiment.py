from nltk import tokenize
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

print('Downloading punkt')
import nltk
nltk.download('punkt_tab')

Languages = {
    'es': 'spanish',
    'en': 'english',
    'fr': 'french', 
    'it': 'italian',
    'pt': 'portuguese',
    'de': 'german'
}

class Sentiment():
    def __init__(self, language: str):

        # Load the tokenizer and model
        self.language = language
        model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def get_sentiment(self, text: str):
        
        sentences = tokenize.sent_tokenize(text, language=Languages[self.language])
        
        sentiment_scores = []
        dominant_sentiments = []
        for sentence in sentences:
            encoded = self.tokenizer(sentence, return_tensors="pt", truncation=False)
            input_ids = encoded['input_ids']
            token_type_ids = encoded.get('token_type_ids')  # May not exist for some models
            attention_mask = encoded['attention_mask']
            chunked_probabilities = []
            for i in range(0, len(input_ids), 512): # 512 is the maximum length of the input
                chunk_input_ids = input_ids[i:i+512]
                chunk_token_type_ids = token_type_ids[i:i+512]
                chunk_attention_mask = attention_mask[i:i+512]
                chunk_outputs = self.model(
                    input_ids=chunk_input_ids,
                    token_type_ids=chunk_token_type_ids,
                    attention_mask=chunk_attention_mask
                )
                chunk_logits = chunk_outputs.logits
                chunked_probabilities.append(torch.nn.functional.softmax(chunk_logits, dim=1))
            probabilities = torch.cat(chunked_probabilities).mean(dim=0)
            sentiment_scores.append(probabilities)
            predicted_class = torch.argmax(probabilities).item()
            dominant_sentiments.append(predicted_class)

        # dimensions are (n_sentences, n_classes = 4)
        sentiment_scores = torch.stack(sentiment_scores)

        # Compute features by sentiment class
        res = {}
        for i in range(5):
            res[f'stats__{i}'] = sentiment_scores[:, i].mean().item()

        return res