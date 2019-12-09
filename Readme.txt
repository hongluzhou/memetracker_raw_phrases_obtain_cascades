Readme.txt

The code to handel memetracker raw phrases data
https://snap.stanford.edu/data/other.html

'memetracker_check.ipynb' is for checking the unique number of websites, phrases, their frequencies, constructing cascades, etc.

'memetracker_plot.ipynb' plots histogram (website and phrase frequency) for choosing the suitable cut-off for cleanning the data.

'memetracker_cleaner.py' will clean the data with the specified number of most popular websites and phrases. 
(Note: 
1. requre more than 100G memory, and need to be run in jupyter notebook to aviod memory error.
2. use the for loop to read the raw file one by one is slow, once lines.pickle is generated, next time could directly load the lines.pickle and comment out that part, which will be a lot faster. 
)
