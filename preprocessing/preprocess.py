import requests
import json
from bs4 import BeautifulSoup
from collections import defaultdict
from os.path import join, dirname
from dotenv import load_dotenv
import pymongo
import os

def get_3000_most_common_words():
	common_words = []

	site_url = 'https://www.ef.com/english-resources/english-vocabulary/top-3000-words/'
	r = requests.get(site_url)

	soup = BeautifulSoup(r.content, 'lxml')

	# The second p tag on the page. Need to strip the line breaks
	for w in soup.find_all('p')[1].stripped_strings:
		if is_word_len_good(w):
			common_words.append(w)

	print len(common_words)
	return common_words

def is_word_len_good(w):
	return True if (len(w) >=5 and len(w) <= 8) else False

def get_sub_words(common_words):
	# of the form {w1:[sub_1, sub_2, ...], w2:[sub_1, sub_2, ...]}
	unscramble_url = 'https://www.litscape.com/word_tools/ajax/wordfinder.php'
	params = {'dic':'default', 'searchtype':'containsonly', 'lentype':'rangelen', 'num1':'3', 'num2':'8' ,'auth':'924aeeec45d7'}
	global_dict = {}


	for index, word in enumerate(common_words):
		# first add the word to the params
		try:
			print index, word
			params['str'] = word
			r = requests.get(unscramble_url, params=params)
			global_dict[word] =  r.json()['resultset']['wordlist']

		except ValueError:
			store_data_set_in_file(global_dict)

	return global_dict

def store_data_set_in_file(words_to_sub_words):
	with open('words_to_sub_words.json', 'w') as fp:
		json.dump(words_to_sub_words, fp)

def read_data_set_from_file():
	with open('words_to_sub_words.json', 'r') as fp:
		return json.load(fp)

def prettify_data_set():
	mongo_documents = []
	words_to_sub_words = read_data_set_from_file()

	for word in words_to_sub_words:
		if has_enough_sub_words(word, words_to_sub_words):
			mongo_document = generate_mongo_document(word, words_to_sub_words[word])
			mongo_documents.append(mongo_document)

	return mongo_documents

# Only return true if this word has more than 10 sub-words to ensure certain level of competition
def has_enough_sub_words(word, word_list):
	return True if len(word_list[word]) >=10 else False

'''
Will generate a python dict of this format:
{
	'pupil': {
		5: ['pupil'],
		3: ['pup', 'lip'],
		2: ['up']
	}
}
'''
def generate_mongo_document(word, word_list):
	word_len_to_words = defaultdict(list)

	for wl in word_list:
		w = wl['w']
		word_len_to_words[str(len(w))].append(w)

	return {word:word_len_to_words}

def get_db_auth():
	return os.environ.get('DB_USER'), os.environ.get('DB_PASS')


def store_data_set_in_mlab(pretty_data_set):
	dotenv_path = join(dirname(__file__), '.env')
	load_dotenv(dotenv_path, verbose=True)

	DB_USER, DB_PASS = get_db_auth()
	mlab_uri = 'mongodb://'+DB_USER+':'+DB_PASS+'@ds133627.mlab.com:33627/letter_mix_words'

	client = pymongo.MongoClient(mlab_uri)
	db = client.get_default_database()

	# Create the letter_mix collection if not already present
	letter_mix = db['letter_mix']
	letter_mix.insert_many(pretty_data_set)

def main():
	# Uncomment the below two lines if running for the first time

	# common_words = get_3000_most_common_words()
	# words_to_sub_words = get_sub_words(common_words)

	pretty_data_set = prettify_data_set()
	store_data_set_in_mlab(pretty_data_set)	

if __name__ == '__main__':
	main()
