import random
from colorama import Fore
from colorama import Style
from colorama import init
import sys

#print('Number of arguments:', len(sys.argv), 'arguments.')
#print('Argument List:', str(sys.argv))

predetermined_word = None
if (len(sys.argv) > 1):
	predetermined_word = sys.argv[1]


init()



def all_words_to_five():
	words = load_words('data/WordList.txt')

	five_length = []

	for w in words:
		if (len(w) == 5):
				five_length.append(w)

	print(len(five_length))

	with open('data/five.txt', 'w') as f:
		f.write("\n".join(five_length) + "\n")


def load_words(filename):
	with open(filename,'r') as f:
		lines = f.readlines()

	words = []

	for w in lines:
		words.append(w.strip())

	print("loaded words:", len(words))

	return words

def random_element(a):
	return a[random.randint(0,len(a)-1)]

WORD_COMPARE_EXACT = 'x'
WORD_COMPARE_CLOSE = 'c'
WORD_COMPARE_MISS = '_'
WORD_COMPARE_PLACEHOLDER = '.'

def compare_words(guess, word):
	ret = []

	for i in range(0, len(guess)):
		if guess[i] in word[i]:
			ret.append(WORD_COMPARE_EXACT)
			#replace the exact match to prevent duplicate close matches
			word = word[:i] + WORD_COMPARE_PLACEHOLDER + word[i + 1:]
		else:
			ret.append(WORD_COMPARE_MISS)

	#upgrade misses to close matches
	for i in range(0, len(guess)):
		if word[i] != WORD_COMPARE_PLACEHOLDER and guess[i] in word:
			ret[i] = WORD_COMPARE_CLOSE
			#replace the close match to prevent duplicate close matches
			word = word.replace(guess[i], WORD_COMPARE_PLACEHOLDER, 1)

	return ret

def score_guess(response):
	ret = 0
	for c in response:
		if c == WORD_COMPARE_EXACT:
			ret += 5
		elif c == WORD_COMPARE_CLOSE:
			ret += 1

	return ret

def does_match_known(word, known):
	for i in range(0, min(len(known),len(word))):
		if known[i] == ' ':
			continue
		if known[i] != word[i]:
			return False

	return True

def does_contain_close(word, close):
	for l in close:
		if not l in word:
			return False

	return True

def does_contain_excluded(word, excluded):
	for l in excluded:
		if l in word:
			return True

	return False

def filter_words(words, known, close, excluded, close_by_pos = []):
	ret = []

	for w in words:
		if not does_match_known(w, known):
			continue

		if not does_contain_close(w, close):
			continue

		if does_contain_excluded(w, excluded):
			continue

		bad = False
		for i in range(0, len(close_by_pos)):
			for l in close_by_pos[i]:
				if w[i] == l:
					bad = True

		if bad:
			continue

		ret.append(w)

	return ret


def response_to_output(word, resp, known_letters, close_letters, excluded_letters):
	pretty_response = ""
	known = []
	close = []
	for i in range(0, len(resp)):
		letter = word[i]
		if resp[i] == WORD_COMPARE_EXACT:
			pretty_response = pretty_response + Fore.GREEN + letter
			known.append(letter)
			close.append("")
			if not letter in known_letters:
				known_letters.append(letter)
		elif resp[i] == WORD_COMPARE_CLOSE:
			pretty_response = pretty_response + Fore.YELLOW + letter
			known.append(" ")
			close.append(letter)
			if not letter in close_letters:
				close_letters.append(letter)
		else:
			pretty_response = pretty_response + Style.RESET_ALL + letter
			if not letter in excluded_letters and not letter in known_letters:
				excluded_letters.append(letter)
				excluded_letters.sort()
			known.append(" ")
			close.append("")
	pretty_response = pretty_response + Style.RESET_ALL
	return (pretty_response, known, close, known_letters, close_letters, excluded_letters)

#all_words_to_five()

words = load_words('data/five.txt')

def cheater():
	file_cheat = "five - Copy.txt"
	close_by_pos = [
		['y'],
		['o'],
		[],
		[],
		[]]
	cheat_words = filter_words(words, list("     "), list('yo'), list('childabestung'), close_by_pos)
	print(len(cheat_words))
	with open(file_cheat, 'w') as f:
		f.write("\n".join(cheat_words) + "\n")


#cheater()

def more_than_one(str, c):
    return str.count(c) > 1;

def has_dupes(str):
	for l in str:
		if more_than_one(str, l):
			return True

	return False


def remove_double_letters(words):
	ret = []

	for w in words:
		if has_dupes(w):
			continue
		ret.append(w)


	return ret

def select_popular_word(words, remaining_words, guesses, ai, skip_letters = []):
	#if len(skip_letters) == 0:
	#	print("select_popular_word", len(words))

	if len(remaining_words) == 1:
		#print("got it!", remaining_words[0])
		return remaining_words[0]
	if (len(skip_letters) > 20):
		#print("too many!", remaining_words[0], "".join(skip_letters))
		return remaining_words[0]
	close = []

	popularity = {}

	for w in remaining_words:
		for l in w:
			if l in skip_letters:
				continue
			if not l in popularity:
				popularity[l] = 1
			else:
				popularity[l] = popularity[l] + 1

	if len(popularity) == 0:
		word = random_element(remaining_words)
		#print("not pop", word, len(remaining_words), skip_letters)
		return word
	most = max(popularity, key=popularity.get)
	skip_letters.append(most)


	fallback = remaining_words[0]
	pre_count = len(remaining_words)
	remaining_words = filter_words(remaining_words, [' ', ' ', ' ', ' ', ' '], [most], [])
	if (len(remaining_words) == pre_count):
		word = random_element(remaining_words)
		#print("no elim", word)
		return word
	#print(most, pre_count, len(remaining_words))
	if len(remaining_words) == 0:
		#print("falling back", fallback)
		return fallback

	#skip_letters.sort()
	#print("recursing", len(remaining_words), "".join(skip_letters))
	return select_popular_word(remaining_words, remaining_words, guesses, ai, skip_letters)

def select_random_word(words, remaining_words, guesses, ai):
	return random_element(remaining_words)

def select_fixed_word(words, remaining_words, guesses, ai):
		if len(guesses) == 0:
			return  ai['fixed_word']
		else:
			return select_random_word(words, remaining_words, guesses, ai)

def select_two_popular_word(words, remaining_words, guesses, ai):
		if len(guesses) < 3:
			excluded_letters = []
			other_words = words
			sim = remove_double_letters(other_words)
			for g in guesses:
				resp = g['resp']
				guess = g['word']
				pretty_response, known, close, known_letters, close_letters, excluded_letters = response_to_output(guess, resp, [], [], excluded_letters)

				for l in known:
					if l not in ['', " "]:
						excluded_letters.append(l)
				for l in close:
					if l not in ['', " "]:
						excluded_letters.append(l)
				other_words = filter_words(other_words, [], [], excluded_letters)
				sim = remove_double_letters(other_words)
				#print("".join(excluded_letters), len(other_words), len(sim))
			return select_popular_word(words, sim, guesses, ai)
		else:
			return select_popular_word(words, remaining_words, guesses, ai)


def ai_guess(word, ai):
	remaining_words = words
	excluded_letters = []
	close_by_pos = [[],[],[],[],[]]

	guesses = []
	guess = ""
	while guess != selected_word:
		guess = ai['selection'](words, remaining_words, guesses, ai)
		
		resp = compare_words(guess, selected_word)
		pretty_response, known, close, known_letters, close_letters, excluded_letters = response_to_output(guess, resp, [], [], excluded_letters)
		guesses.append({'word':guess, 'resp':resp, 'pretty':pretty_response,'count':len(remaining_words)})

		for i in range(0, len(close)):
			if not close[i] in close_by_pos[i]:
				close_by_pos[i].append(close[i])

		remaining_words = filter_words(remaining_words, known, close, excluded_letters, close_by_pos)
		if len(remaining_words) == 0:
			print_responses(guesses)
			print("uh oh", close_by_pos, excluded_letters)
	return guesses



ais = [ 
	{'name':"simple", 'selection':select_random_word}, 
	{'name':"duo", 'selection':select_two_popular_word}, 
	{'name':"pop", 'selection':select_popular_word}, 
	{'name': "leaner", 'selection':select_fixed_word, 'fixed_word':'leans'}
]
def print_responses(responses):
	for i in range(0, len(responses)):
		resp = responses[i]
		print(f"{i+1}: {resp['pretty']} with {resp['count']} words remaining.")

def run_ais():
	while True:
		run_count = 30
		ai_runs = []
		selected_words = []
		for i in range(0, run_count):
			selected_words.append(random_element(words))
		for ai in ais:
			total = 0
			runs = []
			for i in range(0,run_count):
				selected_word = selected_words[i]
				run = ai_guess(selected_word, ai)
				total = total + len(run)
				runs.append(run)
			ai_runs.append({'name':ai['name'], 'runs':runs, 'total':total})
			print(f"{ai['name']}:{(total/run_count)}")

		i = input(f"New word, Details, Quit?")
		if i == "q":
			break
		elif i == "n":
			selected_word = random_element(words)
		elif i == "d":
			run_index = random.randint(0, run_count-1)
			for run in ai_runs:
				print(run['name'])
				print_responses(run['runs'][run_index])
	

#run_ais()

selected_word = random_element(words)
if predetermined_word != None:
	print("Predetermined word:", predetermined_word)
	selected_word = predetermined_word

#new ai that focuses on the close ones!
#closes can count the words that have instances of that letter in each of the available columns! that is a GREAT gamble

alphabet = "abcdefghijklmnopqrstuvwxyz"
guesses = []
pretty_guesses = []
responses = []
excluded_letters = []
close_letters = []
known_letters = []
close_by_pos = [[],[],[],[],[]]
val = ""
remaining_words = words

while val != selected_word:
	print(f"{len(remaining_words)} Remaining words")
	for g in pretty_guesses:
		print(g)
	s = ""
	for l in alphabet:
		if l in excluded_letters:
			s = s + Fore.BLACK 
		elif l in known_letters:
			s = s + Fore.GREEN
		elif l in close_letters:
			s = s + Fore.YELLOW
		else:
			s = s + Fore.WHITE
		s = s + l
	print(s)
	val = input(f"{len(guesses)+1} guess: ")
	if len(val) > 5:
		val = val[0:5]

	if val == "c":
		print("target:", selected_word)
		print("close", close_letters)
		print("excluded", excluded_letters)
		print("close by pos", close_by_pos)
	if val == "s":
		print(",".join(remaining_words))

	if not val in words:
		print("not a valid word\n")
		continue


	guesses.append(val)
	resp = compare_words(val, selected_word)
	responses.append(resp)

	pretty_response, known, close, known_letters, close_letters, excluded_letters = response_to_output(val, resp, known_letters, close_letters, excluded_letters)

	for i in range(0, len(close)):
		if not close[i] in close_by_pos[i]:
			close_by_pos[i].append(close[i])


	pretty_guesses.append(pretty_response)
	remaining_words = filter_words(remaining_words, known, close, excluded_letters, close_by_pos)
	#print("".join(resp), score_guess(resp))
