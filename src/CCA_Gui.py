#GUI Imports
import PySimpleGUI as sg
#FileUpload Imports
import fitz
import os
import string
import re
import pprint
from DocSearcher import DocSearcher
from TextCleaner import TextCleaner
from TopicModeler import TopicModeler

from timeit import default_timer as timer

def GetFilepath(filepath, index):
	file_contents = []
	translator = str.maketrans('', '', string.punctuation)
	fileName = os.path.basename(filepath)
	files.append(fileName)
	file_paths[fileName] = (filepath)

def ReadFile(filepath, filename):
	file_contents = []
	contents_appended = []
	doc = fitz.open(filepath)
	for page in doc:
			blocks = page.getText("blocks")
			for block in blocks:
				file_contents += ([line for line in block if isinstance(line, str)])
	for item in file_contents:
		contents_appended += str.splitlines(item.translate(str.maketrans('', '', string.punctuation)).replace(u'\u2022', ''))
	text_dictionary.update({filename: contents_appended})

def CompareTopics(self):
	overlaps = []
	overlaps = functools.reduce(set.intersection, (set(val) for val in topic_dictionary.values()))
	return overlapts

def Generate():
	start = timer()
	docSearch = DocSearcher()
	textCleaner = TextCleaner()
	topicModeler = TopicModeler()
	files_to_search = []
	files_to_search = [file for file in files if file not in user_selected_text_files]	
	for file in files_to_search:
		text_dictionary[file] = textCleaner.Clean(docSearch.OpenFile(file_paths[file], default_search))

	
	for key in text_dictionary:
		m_topics = topicModeler.CreateCorporaDocSpecific(num_topics, num_passes, text_dictionary[key], num_words)
		topic_dictionary[key] = m_topics[0]
		parsed_topics[key] = m_topics[1]

	overlaps_graph, overlaps_print = topicModeler.CheckOverlaps(distance, parsed_topics, topic_dictionary)
	#PrettifyPrint(overlaps_print)
	topicModeler.PrintOverlapPdf(overlaps_print, topic_dictionary)
	topicModeler.CreateGraph(graph, overlaps_graph)

	end = timer()
	print(end - start)
	print('=========================================================')


def OpenSettings():
	num_topics = 3
	num_passes = 50
	num_words = 5
	default_search = True
	distance = 0.35
	graph = 'PyVis'
	layout = [[sg.InputText(focus=False, justification='right', default_text=num_topics, size=(12, 1)), sg.Text('Number of Topics', key="__TOPICS__", size=(15, 1))],
			  [sg.InputText(focus=False, justification='right', default_text=num_passes, size=(12, 1)), sg.Text('Number of Passes', key="__PASSES__", size=(15, 1))],
			  [sg.InputText(focus=False, justification='right', default_text=num_words, size=(12, 1)), sg.Text('Number of Words', key="__WORDS__", size=(15, 1))],
			  [sg.InputText(focus=False, justification='right', default_text=distance, size=(12, 1)), sg.Text('Hellinger Distance', key='__DIST__', size=(15, 1))],
			  [sg.Listbox(['PyVis', 'NetworkX'], key='__GRAPH__', select_mode='single', default_values='PyVis', enable_events=True, size=(11, 2)), sg.Text('Graph Type', size=(15, 1))],
			  [sg.Checkbox('Default Searching', default=default_search, size=(30, 1))],
			  [sg.Button('Save', focus=False, size=(12, 1), key='__SAVE__'), sg.Button('Exit', focus=False, size=(12, 1))]]
	
	window = sg.Window('Settings', layout, modal=True)
	choice = None
	while True:
		event, values = window.read()
		if event == 'Exit' or event == sg.WIN_CLOSED:
			break
		if event == '__SAVE__':
			num_topics = int(values[0])
			num_passes = int(values[1])
			num_words = int(values[2])
			distance = float(values[3])
			default_search = values[4]
			graph = values['__GRAPH__']
			break
	window.close()
	return num_topics, num_passes, num_words, default_search, distance, graph

sg.theme('SystemDefault')

files = []
file_paths = {}
selected_filename = ""
selected_file_text = []
col_left = sg.Column([
			[sg.Frame(
				layout=[
					[sg.Listbox(files, size=(50, 33), key='__FILES__', select_mode='single', enable_events=True)]
				], title='Uploaded Files')
			],
			[sg.Input(key='__TARGET__', enable_events=True, visible=False), sg.FilesBrowse(target='__TARGET__', size=(22,1)), sg.Button('Generate Report', focus=False, size=(22, 1), key='__GENERATE__')],
			[sg.Button('Settings', focus=False, size=(22, 1), key='__SETTINGS__'), sg.Button('Exit', focus=False, size=(22, 1))]
		   ], vertical_alignment='top', justification='center', element_justification='center')

col_right = sg.Column([
				[sg.Frame(
					layout=[
						[sg.Listbox(selected_file_text, size=(120, 35), enable_events=True, key='__CONTENT__', select_mode='multiple')],
						[sg.Button('Save Selection', focus=False, size=(25, 1), key='__SAVE_SEL__')],
					], title='Selected file text', element_justification='center')
				]
			], vertical_alignment='center')

layout = [[col_left, col_right]]

text_dictionary = {}
topic_dictionary = {}
parsed_topics = {}
overlaps_graph = {}
overlaps_print = {}
user_selected_text_files = []
num_topics = 3
num_passes = 50
num_words = 5
defualt_search = True
distance = 0.35
g_type = ''
graph = 'PyVis'
corpora = 'Doc Specific'

window = sg.Window('Curriculum Analysis', layout).Finalize()
window.Maximize()

while True:
	event, values = window.read()
	if event == sg.WIN_CLOSED or event == 'Exit':
		break
	if event == '__TARGET__':
		temp_files = values['__TARGET__'].split(';')
		for index, file in enumerate(temp_files):
			GetFilepath(file, index)
		window.Element('__FILES__').Update(values=files)
	if event == '__FILES__' and len(values['__FILES__']):
		selected_file = values['__FILES__']
		selected_filename = selected_file[0]
		ReadFile(file_paths[selected_filename], selected_filename)
		selected_file_text = text_dictionary[selected_filename]
		window.Element('__CONTENT__').Update(values=selected_file_text)
	if event == '__GENERATE__':
		print(Generate())
	if event == '__SAVE_SEL__' and len(values['__CONTENT__']):
		text_dictionary[selected_filename] = values['__CONTENT__']
		user_selected_text_files.append(selected_filename)
		selected_file_text = []
		selected_filename = ""
		window.Element('__CONTENT__').Update(values=selected_file_text)
	if event == '__SETTINGS__':
		num_topics, num_passes, num_words, default_search, distance, g_type = OpenSettings()
		graph = g_type[0]
	

		

		

window.close()

 