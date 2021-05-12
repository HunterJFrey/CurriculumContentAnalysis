import fitz
from operator import itemgetter
import string
import re

class DocSearcher:
	def Fonts(self, doc, granularity=False):
		styles = {}
		font_counts = {}

		for page in doc:
			blocks = page.getText("dict")["blocks"]
			for b in blocks:
				if b['type'] == 0:
					for l in b["lines"]:
						for s in l["spans"]:
							if granularity:
								identifier = "{0}_{1}_{2}_{3}".format(s['size'], s['flags'], s['font'], s['color'])
								styles[identifier] = {'size': s['size'], 'flags': s['flags'], 'font': s['font'], 'color': s['color']}
							else:
								identifier = "{0}".format(s['size'])
								styles[identifier] = {'size': s['size'], 'font': s['font']}

							font_counts[identifier] = font_counts.get(identifier, 0) + 1

		font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)

		if len(font_counts) < 1:
			raise ValueError("Zero discriminating fonts found! ")

		return font_counts, styles

	def FontTags(self, font_counts, styles):
		p_style = styles[font_counts[0][0]]
		p_size = p_style['size']

		font_sizes = []
		for(font_size, count) in font_counts:
			font_sizes.append(float(font_size))
		font_sizes.sort(reverse=True)

		index = 0
		size_tag = {}
		for size in font_sizes:
			index += 1
			if size == p_size:
				index = 0
				size_tag[size] = '<p>'
			if size > p_size:
				size_tag[size] = '<h{0}>'.format(index)
			elif size < p_size:
				size_tag[size] = '<s{0}>'.format(index)

		return size_tag

	def HeadersPara(self, doc, size_tag):
		header_para = []
		first = True
		previous_s = {}

		for page in doc:
			blocks = page.getText("dict")["blocks"]
			for b in blocks:
				if b['type'] == 0:
					block_string = ""
					for l in b["lines"]:
						for s in l["spans"]:
							#print(s['text'])
							temp_string = re.sub('\t', ' ', s['text'])
							#print(temp_string)
							if temp_string.strip().replace(u'\u2022', ''):
							#if s['text'].strip().replace("\t", ''):
								#print(s['text'])
								if first:
									previous_s = s
									first = False
									block_string = size_tag[s['size']] + temp_string
								else:
									if s['flags'] == 16 or s['flags'] == 20:
										#print(s['text'])
										split_string = temp_string.split()
										header_para.append('<b>' + ' '.join(split_string[:3]))
										block_string += '<p>' + ' '.join(split_string[4:])
									elif s['size'] == previous_s['size']:
										if block_string == "":
											block_string = size_tag[s['size']] + temp_string
											#header_para.append(size_tag[s['size']] + temp_string)
										else:
											#block_string += " " + temp_string
											header_para.append(' ' + temp_string)
									else:
										header_para.append(block_string)
										block_string = size_tag[s['size']] + temp_string

									previous_s = s

						block_string += "|"
					header_para.append(block_string)
		return header_para

	def CleanPunctuation(self, textToClean):
		return textToClean.translate(str.maketrans('', '', string.punctuation))

	def SearchText(self, textToSearch):
		#print(textToSearch)
		searchText = [text.lower() for text in textToSearch]
		text_to_keep = []
		#print(searchText)
		for index, text in enumerate(searchText):
			#text = text.lower()
			#index = searchText.index(text)
			#print(text)
			if 'course description' in text:  
				text_to_keep += self.SubSearch(text, searchText, index, 1)
			elif 'course information' in text:
				text_to_keep += self.SubSearch(text, searchText, index, 1)
			elif 'course overview' in text:
				text_to_keep += self.SubSearch(text, searchText, index, 1)


			if 'objectives' in text:
				text_to_keep += self.SubSearch(text, searchText, index, 2)
			elif 'outcomes' in text:
				text_to_keep += self.SubSearch(text, searchText, index, 2)
			#elif 'course learning outcomes' in text:
			#	text_to_keep += self.SubSearch(text, searchText, index, 2)	

		return text_to_keep

	def SubSearch(self, text, searchText, index, searchType):
		text_to_keep = []
		text_to_keep.append(searchText[index])
		text_to_keep.append(searchText[index + 1])
		text_to_keep.append(searchText[index + 2])
		for line_text in range(searchText.index(text) + 3, len(searchText)):
			if '<b>' in searchText[line_text] or '<h2>' in searchText[line_text]:
				break
			else:	
				text_to_keep.append(searchText[line_text])
		return text_to_keep

	def OpenFile(self, filepath, search):
		doc = fitz.open(filepath)
		font_counts, styles = self.Fonts(doc)
		size_tag = self.FontTags(font_counts, styles)
		headers_para = self.HeadersPara(doc, size_tag)
		#print(headers_para)
		if(search):
			text_to_keep = self.SearchText(headers_para)
		else: 
			text_to_keep = headers_para
		#print(text_to_keep)
		return text_to_keep

docSearcher = DocSearcher()
#print(docSearcher.OpenFile('C:/Users/hunte/Documents/Python_Projects/CCA_Study/Syllabi/CNMT 110 Gibbs SP21.pdf'))

#print(docSearcher.OpenFile('C:/Users/hunte/Documents/Python_Projects/CCA_Study/Syllabi/CIS 367 Johnson SP21.pdf'))