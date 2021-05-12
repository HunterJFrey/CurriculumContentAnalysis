from gensim import corpora
import gensim
from gensim.matutils import hellinger
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis
from IPython.core.display import HTML
from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import pprint
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from pyvis.network import Network
from weasyprint import HTML

class TopicModeler:
	def CheckOverlaps(self, dist_tolerance, parsed_dict, topic_dict):
		overlaps_graph = {}
		overlaps_print = {}
		for doc1 in parsed_dict:
			#print(doc1)
			for index_doc1, topics_doc1 in enumerate(parsed_dict[doc1]):
				#print("    ", topics_doc1)
				#print('------------------')
				for doc2 in parsed_dict:
					if doc1 == doc2:
						break
					for index_doc2, topics_doc2 in enumerate(parsed_dict[doc2]):
						dist = hellinger(topics_doc1, topics_doc2)
						if(dist <= dist_tolerance):
							doc1_topic_graph = doc1 + ': Topic ' + str(index_doc1 + 1)
							doc2_topic_graph = doc2 + ': Topic ' + str(index_doc2 + 1)
							doc1_topic_print = self.GetNestedElement(topic_dict, doc1, index_doc1)
							doc2_topic_print = self.GetNestedElement(topic_dict, doc2, index_doc2)
							try:
								overlaps_graph[(doc1_topic_graph)] += [(doc2_topic_graph, dist)]
								overlaps_print[(doc1 + ': Topic ' + str(index_doc1 + 1), doc1_topic_print)] += [(doc2 + ': Topic ' + str(index_doc2 + 1), doc2_topic_print)]
							except KeyError:
								overlaps_graph[(doc1_topic_graph)] = [(doc2_topic_graph, dist)]	
								overlaps_print[(doc1 + ': Topic ' + str(index_doc1 + 1), doc1_topic_print)] = [(doc2 + ': Topic ' + str(index_doc2 + 1), doc2_topic_print)]
		return overlaps_graph, overlaps_print
		
	def CreateCorporaDocSpecific(self, num_topics, num_passes, word_list, num_words):
		parsed_topics = []
		cleaned_topics = []
		if len(word_list) < 1:
			return parsed_topics, cleaned_topics
			
		word_dictionary = corpora.Dictionary([word_list]) 
		corpus = [word_dictionary.doc2bow(text) for text in [word_list]]
		
		lda_model = gensim.models.ldamodel.LdaModel(corpus, num_topics=num_topics, id2word=word_dictionary, passes=num_passes)
		topics = lda_model.show_topics(num_words=num_words)
		
		for topic in topics:
			words = []
			vectored_topic = []
			topic_num, topic = topic
			topic = topic.split('+')
			for word in topic:
				prob, word = word.split('*')
				topic_word = word.replace(" ", "").replace('"', '')
				words.append(topic_word)
				word = lda_model.id2word.doc2bow([topic_word])[0][0]
				vectored_topic.append((word, float(prob)))
			parsed_topics.append(vectored_topic)
			cleaned_topics.append(words)

		return cleaned_topics, parsed_topics

	def GetNestedElement(self, topic_dict, key, index):
		topics = topic_dict.get(key)
		topic = ' '.join(topics[index])
		return topic

	def CreateGraph(self, graph_type, overlaps):
		overlap_frame = pd.DataFrame(columns=['Source', 'Target', 'Type', 'Weight'])
		for overlap in overlaps:
			for sub_lap in overlaps[overlap]:
				overlap_frame = overlap_frame.append({ 
					'Source' : overlap,
					'Target' : sub_lap[0],
					'Type' : 'directed',
					'Weight' :  ((1 - sub_lap[1]) / 25)
				}, ignore_index=True)

		net = Network(height='100%', width='100%', directed=True)
		sources = overlap_frame['Source']
		targets = overlap_frame['Target']
		weights = overlap_frame['Weight']
		edge_data = zip(sources, targets, weights)
		graph = nx.DiGraph()
		for index, e in enumerate(edge_data):
			src = e[0]
			dst = e[1]
			w = e[2]
			if(graph_type == 'NetworkX'):
				graph.add_node(src)
				graph.add_node(dst)
				graph.add_edge(src, dst, weights=w)
			else:
				net.add_node(src, src, title=src, physics=False, group=index, arrowStrikethrough=False)
				net.add_node(dst, dst, title=dst, physics=False, group=index, arrowStrikethrough=False)
				net.add_edge(src, dst, value=w, physics=False)
		if(graph_type == 'PyVis'):
			options = {
				'layout': {
					'hierarchical': {
						'enabled': True,
						'levelSeparation': 50,
						'treeSpacing': 75,
						'nodeSpacing': 500,
						'edgeMinimization': False
					}
				}
			}
			net.options = options
			connections = net.get_adj_list()
			for node in net.nodes:
				node['size'] = len(connections[node['id']]) / 3
				node['title'] += ' Neighbors: <br>' + '<br>'.join(connections[node['id']])
				node['value'] = len(connections[node['id']])
			net.from_nx(graph)
			net.show('SimilarityVisualizationGraph.html')
		else:
			degrees = [val * 10 for (node, val) in graph.degree()]
			pos = nx.circular_layout(graph)
			nx.draw(graph, pos, node_size=degrees, with_labels=True, font_size=8)
			plt.show()
		
	def PrintOverlapPdf(self, overlaps, topic_dict):
		overlap_frame = pd.DataFrame(columns=['Course', 'Topic', 'Similar Course', 'Similar Topic'])
		for overlap in overlaps:
			for sub_lap in overlaps[overlap]:
				overlap_frame = overlap_frame.append({ 
					'Course' : overlap[0],
					'Topic' : overlap[1],
					'Similar Course' : sub_lap[0],
					'Similar Topic' :  sub_lap[1]
				}, ignore_index=True)
		table = overlap_frame.to_html()
		table_html = HTML(string=table)
		table_html.write_pdf('Topic Similarities.pdf')

		topicFrame = pd.DataFrame(columns=['Course', 'Topics'])
		for text in topic_dict:
			topicFrame = topicFrame.append({
				'Course': text,
				'Topics': topic_dict[text]
			}, ignore_index=True)
		topics = topicFrame.to_html()
		topic_html = HTML(string=topics)
		topic_html.write_pdf('Generated Topics.pdf')
		#overlap_frame.to_html()

