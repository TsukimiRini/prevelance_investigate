import matplotlib.pyplot as plt
from nltk.stem import SnowballStemmer
from hunspell import Hunspell
import re
import os
from google_trans_new import google_translator
import wordninja
from nltk.corpus import stopwords

words_list = "../data/bag_of_words_res"
data_dir = "../data"
word_dict = {}
stemmer = SnowballStemmer('english')
h = Hunspell()
reg = re.compile(r"[a-zA-z0-9']")
plot_dir = "../plots"
labels = []
freqs = []

translator = google_translator()
chinese_dict = {}
stop_words = stopwords.words('english')

stem_dict = {
    "added": ["add", 0],
    "remove": ["remove", 0],
    "ui": ["ui", 0],
    "settings": ["settings", 0],
    "daniel": ["daniel", 0],
    "https": ["https", 0],
    "removed": ["remove", 0],
    "issues": ["issue", 0],
    "setting": ["setting", 0],
    "api": ["api", 0],
    "radle": ["radle", 0],
    "readme": ["readme", 0],
    "apps": ["app", 0],
    "rename": ["rename", 0],
    "improved": ["improve", 0],
    "popup": ["popup", 0],
    "unused": ["unused", 0],
}


def checkEng(check_str):
    if reg.match(check_str):
        return True
    return False


def stemWord(word, freq):
    res = word
    if word in stem_dict:
        stem_dict[word][1] += freq
        return stem_dict[word][0]
    stemmed = stemmer.stem(word)
    try:
        if not h.spell(stemmed):
            # print(stem_w + " can't be spelled")
            hun_stem = h.stem(word)
            if len(hun_stem) == 0:
                sugge = h.suggest(stemmed)
                if len(sugge) != 0:
                    res = sugge[0]
                    # print("suggestion {} to {}".format(stem_w, sugge))
                else:
                    res = stemmed
                    # print("stem {} to {}".format(word, stem_w))
            else:
                res = hun_stem[0]
                # print("hun stem {} to {}".format(word, hun_stem))
        else:
            res = stemmed
    except UnicodeEncodeError:
        print("error with encode")
    res = res.split(' ')[0].lower()

    stem_dict[word] = [res, freq]

    return res


def translate():
    with open(words_list, "r") as fd:
        all = fd.readlines()
        lines = [line[:-1] for line in all]
        for line in lines:
            if len(line) < 3:
                continue
            word, freq = line.split(' ')
            freq = int(freq)
            if not checkEng(word):
                chinese_dict[word] = freq
    keys = chinese_dict.keys
    translated = translator.translate(keys, lang_tgt='en').lower()
    for idx, w in enumerate(translated):
        msg = wordninja.split(w)
        for word in msg:
            if len(
                    word
            ) > 1 and word != '\t' and word != '\n' and word != '\r\n' and word not in stop_words:
                # stem_w = stemmer.stem(word)
                # try:
                #     if not h.spell(stem_w):
                #         # print(stem_w + " can't be spelled")
                #         hun_stem = h.stem(word)
                #         if len(hun_stem) == 0:
                #             sugge = h.suggest(stem_w)
                #             if len(sugge) != 0:
                #                 word = sugge[0]
                #                 # print("suggestion {} to {}".format(stem_w, sugge))
                #             else:
                #                 word = stem_w
                #                 # print("stem {} to {}".format(word, stem_w))
                #         else:
                #             word = hun_stem[0]
                #             # print("hun stem {} to {}".format(word, hun_stem))
                #     else:
                #         word = stem_w
                # except UnicodeEncodeError:
                #     print("error with encode")
                #     continue

                # # word = stem_w
                # word = word.split(' ')[0].lower()
                word = stemWord(word, chinese_dict[keys[idx]])
                if word in word_dict:
                    word_dict[word] += chinese_dict[keys[idx]]
                else:
                    word_dict[word] = chinese_dict[keys[idx]]


def rearrangeData():
    translate()
    with open(words_list, "r") as fd:
        all = fd.readlines()
        lines = [line[:-1] for line in all]
        for line in lines:
            if len(line) < 3:
                continue
            word, freq = line.split(' ')
            freq = int(freq)
            if not checkEng(word):
                continue
            # stem_w = stemmer.stem(word)
            # try:
            #     if not h.spell(stem_w):
            #         # print(stem_w + " can't be spelled")
            #         hun_stem = h.stem(word)
            #         if len(hun_stem) == 0:
            #             sugge = h.suggest(stem_w)
            #             if len(sugge) != 0:
            #                 word = sugge[0]
            #                 # print("suggestion {} to {}".format(stem_w, sugge))
            #             else:
            #                 word = stem_w
            #                 # print("stem {} to {}".format(word, stem_w))
            #         else:
            #             word = hun_stem[0]
            #             # print("hun stem {} to {}".format(word, hun_stem))
            #     else:
            #         word = stem_w
            # except UnicodeEncodeError:
            #     print("error with encode")
            #     continue

            # # word = stem_w
            # word = word.split(' ')[0].lower()
            word = stemWord(word, freq)
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

    with open(os.path.join(data_dir, "rearrangedBagOfWords"), 'w') as res_fd:
        for (word, freq) in word_freq:
            res_fd.write("{} {}\n".format(word, freq))

    stemDictStats()


def stemDictStats():
    stem_stats = []
    for word, val in stem_dict.items():
        stem_stats.append(("{} -> {}".format(word, val[0]), val[1]))
    stem_stats.sort(key=lambda x: x[1], reverse=True)

    with open(os.path.join(data_dir, "stem_stats"), "w") as fd:
        for (stem, freq) in stem_stats:
            fd.write("{} {}\n".format(stem, freq))


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