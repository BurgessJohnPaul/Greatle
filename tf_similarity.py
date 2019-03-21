import tensorflow as tf
import tensorflow_hub as hub
import sentencepiece as spm
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


# Reduce logging output.
tf.logging.set_verbosity(tf.logging.ERROR)


def process_to_IDs_in_sparse_format(sp, sentences):
    # An utility method that processes sentences with the sentence piece processor
    # 'sp' and returns the results in tf.SparseTensor-similar format:
    # (values, indices, dense_shape)
    ids = [sp.EncodeAsIds(x) for x in sentences]
    max_len = max(len(x) for x in ids)
    dense_shape = (len(ids), max_len)
    values = [item for sublist in ids for item in sublist]
    indices = [[row, col] for row in range(len(ids)) for col in range(len(ids[row]))]
    return (values, indices, dense_shape)


def plot_similarity(labels, features, rotation):
    corr = np.inner(features, features)
    sns.set(font_scale=1.2)
    g = sns.heatmap(
        corr,
        xticklabels=labels,
        yticklabels=labels,
        vmin=0,
        vmax=1,
        cmap="YlOrRd")
    g.set_xticklabels(labels, rotation=rotation)
    g.set_title("Semantic Textual Similarity")
    plt.show()


def encode_sentences(session, input_placeholder, sentences, sp, encodings):
    values, indices, dense_shape = process_to_IDs_in_sparse_format(sp, sentences)

    sentence_embeddings = session.run(
        encodings,
        feed_dict={input_placeholder.values: values,
                   input_placeholder.indices: indices,
                   input_placeholder.dense_shape: dense_shape})

    sentence_vectors = []
    for index, value in enumerate(sentence_embeddings):
        sentence_vectors.append((sentences[index], value))

    return sentence_vectors


class TfSimilarity:

    def __init__(self):
        # ---
        # Load tensorflow-hub model and sentencepiece tokenizer
        # ---
        try:
            module = hub.Module("https://tfhub.dev/google/universal-sentence-encoder-lite/2")
            self.input_placeholder = tf.sparse_placeholder(tf.int64, shape=[None, None])
            self.encodings = module(
                inputs=dict(
                    values=self.input_placeholder.values,
                    indices=self.input_placeholder.indices,
                    dense_shape=self.input_placeholder.dense_shape))
            with tf.Session() as sess:
                spm_path = sess.run(module(signature="spm_path"))
            self.sp = spm.SentencePieceProcessor()
            self.sp.Load(spm_path)
            print("SentencePiece model loaded at {}.".format(spm_path))
        except Exception as e:
            print('TfSimilarity error:')
            print(e)

    # ---
    # Returns the semantic similarity between str1 and str2 as a decimal between 0 and 1
    # ---
    def get_similarity(self, str1, str2):
        try:
            messages = [str1, str2]

            sentence_vectors = None

            with tf.Session() as session:
                session.run(tf.global_variables_initializer())
                session.run(tf.tables_initializer())
                sentence_vectors = encode_sentences(session, self.input_placeholder, messages, self.sp, self.encodings)

            # print("Correlation between '{}' and '{}'".format(sentence_vectors[0][0], sentence_vectors[1][0]))
            # print(np.inner(sentence_vectors[0][1], sentence_vectors[1][1]))

            return np.inner(sentence_vectors[0][1], sentence_vectors[1][1])

        except Exception as e:
            print('TfSimilarity error:')
            print(e)

        return None

    # ---
    # Returns the phrase in phrase_list that most similar to new_phrase
    # ---
    def match_similarity_with_list(self, new_phrase, phrase_list):
        highest_score = -1
        best_phrase = None

        for candidate_phrase in phrase_list:
            score = self.get_similarity(new_phrase, candidate_phrase)
            if score > highest_score:
                highest_score = score
                best_phrase = candidate_phrase

        return best_phrase


# Example usage:

# tfs = TfSimilarity()

# print( tfs.get_similarity('I am string 1', 'I am string 2') )
#  = 0.97 (i.e. 97% correlation)

# example_sentences = ['I am a big lego', 'Jump over the ocean', 'I am also a dog', 'Wow look at the sun']
# print( tfs.match_similarity_with_list('I am a dog', example_sentences) )
#  = 'I am also a dog'
