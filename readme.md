#**Setup**
To run the program you will need to download all files from the src folder, then run the CCA_Gui.py file! This should open up the UI for the entire project.

##**-----Settings-----**\

 - Num_Topics - How many topics the LDA model will generate\
 - Num_Passes - How many passed the LDA model will take while training\
 - Num_Words - How many words will be shown per topic\
 - Default_Search - Enable the default search, seraches syllabi for "Course Description" and "Learning Outcomes". Disabling this means that the full text of each document will be run through the LDA model.\
 - Hellinger Distance - The distance between 2 topics/how closesly they are related\
 - Graph Type - Type of Graph output, Pyvis is a little less visible, but more interactable. Networkx is easier to read, but provides less interaction\
\
##**-----Text Selection-----**\

If you click an uploaded file on the left of the ui, you can then select which lines of text from the right that you want the program to clean/analyze. Note, this selection will only save if you hit save, otherwise it will use the full text when generating topics!