import operator

import numpy as np

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

class Sentence():
    
    def __init__(self, text):
        self.text = text

class TextSummary():
    
    def __init__(self, text, summary):
        self.text = text
        self.summary = summary

class TextSummarizer():

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()

    def _combine_quotation_clauses(self, clauses):
        combined_clauses = []
        current_sentence = ""
        quote_counter = 0
        for sentence in clauses:
            current_sentence += ' {}'.format(sentence)
            quote_counter += sentence.count('"')
            if quote_counter % 2 == 0:  # all quotes closed
                combined_clauses.append(current_sentence)
                current_sentence = ""
                quote_counter = 0
        if len(current_sentence) > 0:
            combined_clauses.append(current_sentence)
        
        return combined_clauses

    def _combine_mistaken_split_clauses(self, clauses):
        combined_clauses = []
        current_sentence = ""

        for sentence in clauses:
            new_sentence = False
            for c in sentence:
                if c.isalpha():  # first alpha char in sentence
                    if c.isupper():
                        # capitalized, new sentence
                        new_sentence = True
            if new_sentence:
                combined_clauses.append(current_sentence)
                current_sentence = ""
                        
            current_sentence += ' {}'.format(sentence)
        if len(current_sentence) > 0:
            combined_clauses.append(current_sentence)
        
        return combined_clauses

    def _tokenize_and_stem_clauses(self, clauses, min_word_length = 3):
        sentences = []
        stems = {}
        for idx, clause in enumerate(clauses):
            clause = clause.strip()
            words = word_tokenize(clause)
            
            filtered_words = []
            for word in words:
                if word not in self.stop_words and len(word) > min_word_length:
                    filtered_words.append(word)

            stemmed_words = [self.stemmer.stem(word) for word in filtered_words]

            for stem_word in stemmed_words:
                if stem_word in stems:
                    stems[stem_word] += 1
                else:
                    stems[stem_word] = 1

            sentence = Sentence(clause)
            sentence.stemmed_words = stemmed_words
            sentence.index = idx

            sentences.append(sentence)
        return (sentences, stems)

    def _score_sentences(self, sentences, stems_count):
        for sentence in sentences:
            score = 0
            for stem_word in sentence.stemmed_words:
                score += stems_count[stem_word]
            if score != 0:
                score /= len(sentence.stemmed_words)

            sentence.score = score

    # grab sentences by bin until we reach base_count
    def _calculate_num_sentences(self, sentences, base_count = 4):
        n = 0
        bins = np.histogram([s.score for s in sentences], bins='auto')
        for count in reversed(bins[0]):
            n += count
            if n >= base_count:
                return n
        return n

    def _add_neighboring_sentences(self, chosen_indices, sentences):
        to_add = []
        for index in chosen_indices:
            if index > 0:
                to_add.append(index - 1)
            to_add.append(index + 1)
        chosen_indices.extend(to_add)

        chosen_sentences = []
        for index in set(chosen_indices):
            for sentence in sentences:
                if sentence.index == index:
                    chosen_sentences.append(sentence)
                    break
        
        return chosen_sentences

    def summarize(self, text, num_sentences = None):
        # tokenize the text
        sent_tokens = sent_tokenize(text)
        clauses = [s.strip() for s in sent_tokens]

        # combine broken clauses
        combined_clauses = self._combine_quotation_clauses(clauses)
        combined_clauses = self._combine_mistaken_split_clauses(combined_clauses)

        # tokenize and stem sentences
        sentences, stems_count = self._tokenize_and_stem_clauses(combined_clauses)

        # score each sentence
        self._score_sentences(sentences, stems_count)

        # sort sentences by score
        sorted_sentences = sorted(sentences, key=operator.attrgetter('score'), reverse=True)

        # calculate num_sentences
        if num_sentences is None:
            num_sentences = self._calculate_num_sentences(sentences)

        # take top n sentences and order by index
        top_sentences = sorted_sentences[:num_sentences]
        top_sentences = self._add_neighboring_sentences([s.index for s in top_sentences], sentences)
        top_sentences = sorted(top_sentences, key=operator.attrgetter('index'))
        
        # setup summary object
        summary = TextSummary(text, ' '.join([s.text for s in top_sentences]))
        summary.keystems = sorted(stems_count.items(), key=operator.itemgetter(1), reverse=True)
        summary.sentences = sentences
        summary.summary_sentences = top_sentences
        summary.num_sentences = num_sentences
        if sum([s.score for s in sentences]) > 0:
            summary.score = sum([s.score for s in top_sentences]) / sum([s.score for s in sentences])
        else:
            summary.score = 0

        return summary
