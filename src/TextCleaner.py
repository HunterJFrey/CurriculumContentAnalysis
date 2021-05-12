import string
import nltk
#NLTK Imports
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.probability import FreqDist

class TextCleaner:
	def Clean(self, text):
		#print('Un-tokenized text: ', text)
		tokenized_text = self.TokenizeText(text)
		#print('Token Text: ', tokenized_text)
		filtered_text = self.FilterText(tokenized_text)
		#print(filtered_text)
		lemmatized_text = self.LemmatizeText(filtered_text)
		#print(lemmatized_text)
		return lemmatized_text

	def TokenizeText(self, text):
		token_text = []
		#print('Text to token: ', text)
		for content in text:
			token_text += word_tokenize(content)
		#print('Token Text: ', token_text)
		return token_text

	def FilterText(self, text):
		first_filter = [word for word in text if word.isalpha()]
		second_filter = [word for word in first_filter if len(word) > 2]
		stop_words = set(stopwords.words('english'))
		stopwords_filtered = [word for word in second_filter if not word in stop_words]
		return stopwords_filtered

	def LemmatizeText(self, text):
		lemmatizer = WordNetLemmatizer()
		return [lemmatizer.lemmatize(i) for i in text]
