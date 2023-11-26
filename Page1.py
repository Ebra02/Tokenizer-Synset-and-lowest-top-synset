# Input is English text
# The outputs:
# Tokenize the text into sentences
# For each sentence:
# The lowest top synset(s) that are shared among most of the
# core words in the sentence
# Determine the most appropriate synsets that represent the
# words in the sentence
# Replaces 3-5 words in the sentence so that the sentence
# appears the same
import re
import random
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet
from nltk.wsd import lesk
from nltk.tag import pos_tag

# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')

word = "car"
synset_list = wordnet.synsets(word)
synonyms = []

for synset in synset_list:
    for lemma in synset.lemma_names():
        synonyms.append(lemma)

print(synonyms)

def get_core_synsets(words):
    synsets = [wordnet.synsets(word) for word in words if wordnet.synsets(word)]
    return synsets

def get_lowest_common_hypernyms(synsets):
    hypernym_counts = {}
    for synset_list in synsets:
        for synset in synset_list:
            for hypernym in synset.hypernym_paths()[0]:
                hypernym_counts[hypernym] = hypernym_counts.get(hypernym, 0) + 1

    # Find hypernyms shared by at least half of the core words
    common_hypernyms = {
        hypernym
        for hypernym, count in hypernym_counts.items()
        if count >= len(synsets) // 2
    }

    # Find the lowest common hypernyms among those shared by most core words
    lowest_common = None
    for hypernym in common_hypernyms:
        if lowest_common is None or hypernym.min_depth() > lowest_common.min_depth():
            lowest_common = hypernym

    return lowest_common





def replace_words_with_synonyms(sentence):
    words = word_tokenize(sentence)
    tagged_words = pos_tag(words)
    replaced_sentence = sentence
    replacements = 0
    replaced_words = []

    for word, tag in tagged_words:
        if replacements >= 3:  # Limit the number of replacements
            break

        wordnet_pos = get_wordnet_pos(tag)  # Get the WordNet POS tag
        if wordnet_pos and word.lower() not in replaced_words:  # Check if we have a valid POS tag and the word hasn't been replaced already
            synset = lesk(sentence, word, wordnet_pos)  # Use Lesk algorithm to get the best synset
            if synset:
                synonyms = synset.lemma_names()
                # Exclude the original word and any synonyms already in the sentence
                synonyms = [synonym for synonym in synonyms if synonym.lower() != word.lower() and synonym.lower() not in sentence.lower()]
                if synonyms:
                    replacement = random.choice(synonyms).replace('_', ' ')
                    # Replace only whole words to avoid partial matches
                    replaced_sentence = re.sub(r'\b' + re.escape(word) + r'\b', replacement, replaced_sentence, count=1)
                    replacements += 1
                    replaced_words.append(word.lower())  # Add the word to the list of replaced words to avoid duplicate replacements

    return replaced_sentence

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


# Input text
input_text = "During our expedition, we encountered diverse animals such as eagles, trout, and rabbits. navigated through different terrains like mountains, forests, and rivers. and used equipment including compasses, maps, and binoculars."


# Step 1: Tokenize the input text into sentences
sentences = sent_tokenize(input_text)

# Process each sentence
for sentence in sentences:
    # Step 2: Tokenize the sentence into words
    words = word_tokenize(sentence)

    # Step 3: Determine the synsets for each word in the sentence
    word_synsets = get_core_synsets(words)
    #print(word_synsets)

    # Step 4: Find the lowest common hypernyms shared among the core words
    lowest_hypernym = get_lowest_common_hypernyms(word_synsets)

    # Step 5: Choose the most appropriate synset that represents each word
    # Assuming the first synset is the most appropriate for simplicity

    appropriate_synsets = [synset_list[0] for synset_list in word_synsets if synset_list]

    # Step 6: Replace 3-5 words in the sentence with their synonyms from the chosen synsets
    replaced_sentence = replace_words_with_synonyms(sentence)

    # ...
    # Output the results
    print("Original Sentence:", sentence)
    print("Replaced Sentence:", replaced_sentence)
    # Use the .name().split('.')[0] to print only the synset name without the extra symbols and information
    if lowest_hypernym:
        print("The lowest top synset:", lowest_hypernym.name().split('.')[0])
# ...
