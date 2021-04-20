import matplotlib.pyplot as plt
from nltk.stem import SnowballStemmer
from hunspell import Hunspell
import re
import os

words_list = "/Users/tannpopo/Documents/Study/ChangeLint/stats/bag_of_words_res.txt"
word_dict = {}
stemmer = SnowballStemmer('english')
h = Hunspell()
reg = re.compile(r"[a-zA-z0-9']")
plot_dir = "../plots"
labels = []
freqs = []


def checkEng(check_str):
    if reg.match(check_str):
        return True
    return False


def rearrangeData():
    with open(words_list, "r", encoding="gbk") as fd:
        all = fd.readlines()
        lines = [line[:-1] for line in all]
        for line in lines:
            if len(line) < 3:
                continue
            word, freq = line.split(' ')
            freq = int(freq)
            if not checkEng(word):
                continue
            stem_w = stemmer.stem(word)
            try:
                if not h.spell(stem_w):
                    # print(stem_w + " can't be spelled")
                    hun_stem = h.stem(word)
                    if len(hun_stem) == 0:
                        sugge = h.suggest(stem_w)
                        if len(sugge) != 0:
                            word = sugge[0]
                            # print("suggestion {} to {}".format(stem_w, sugge))
                        else:
                            word = stem_w
                            # print("stem {} to {}".format(word, stem_w))
                    else:
                        word = hun_stem[0]
                        # print("hun stem {} to {}".format(word, hun_stem))
                else:
                    word = stem_w
            except UnicodeEncodeError:
                print("error with encode")
                continue

            # word = stem_w
            word = word.split(' ')[0].lower()
            if word in word_dict:
                word_dict[word] += freq
            else:
                word_dict[word] = freq

    word_freq = []
    for word, freq in word_dict.items():
        word_freq.append((word, freq))
        labels.append(word)
        freqs.append(freq)

    word_freq.sort(key=lambda x: x[1], reverse=True)

    with open("../data/rearrangedBagOfWords", 'w') as res_fd:
        for (word, freq) in word_freq:
            res_fd.write("{} {}\n".format(word, freq))


def drawPie():
    fig1, ax1 = plt.subplots()
    ax1.pie(freqs,
            labels=labels,
            autopct='%1.1f%%',
            shadow=True,
            startangle=90)
    ax1.axis(
        'equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    fig = ax1.get_figure()
    fig.savefig(os.path.join(plot_dir, "bag_of_words.png"))


rearrangeData()
drawPie()