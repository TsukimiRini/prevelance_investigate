import matplotlib.pyplot as plt
from nltk.stem import SnowballStemmer
from hunspell import Hunspell
import re
import os
from google_trans_new import google_translator
import wordninja
from nltk.corpus import stopwords
import numpy as np

words_list = "../data/bag_of_words_res"
data_dir = "../data"
word_dict = {}
stemmer = SnowballStemmer('english')
h = Hunspell()
reg = re.compile(r"[a-zA-z0-9']")
noCh = re.compile(r"[^a-zA-Z]")
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
        return ""
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
                if word == "":
                    continue
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
            if word == "":
                continue
            if word in word_dict:
                word_dict[word] += freq
            else:
                word_dict[word] = freq

    _word_dict = {}
    with open(os.path.join(data_dir, "valid_words_list"),
              'w') as valid_word_fd:
        for word, freq in word_dict.items():
            t = getType(word, freq)
            key = word
            if t == "meaningless":
                continue
            else:
                valid_word_fd.write("{} {}\n".format(word, freq))
                key = t
            if key in _word_dict:
                _word_dict[key] += freq
            else:
                _word_dict[key] = freq

    word_freq = []
    for word, freq in _word_dict.items():
        word_freq.append((word, freq))
        labels.append(word)
        freqs.append(freq)

    word_freq.sort(key=lambda x: x[1], reverse=True)

    with open(os.path.join(data_dir, "bag_of_wors_by_types"), 'w') as res_fd:
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


commit_types = {
    "NewFeature": [
        "add", "additional", "new", "create", "initial", "feature", "feat",
        "task", "function", "support", "implement", "develop", "completed",
        "complete", "work", "start", "intent", "introduce"
    ],
    "UI/resource changes": [
        "view", "show", "activity", "activities", "fragment", "dialog",
        "button", "ui", "icon", "screen", "bar", "menu", "color", "user",
        "name", "layout", "option", "thumbnail", "image", "background",
        "album", "play", "playback", "draw", "message", "list", "item",
        "string", "file", "video", "audio", "photo", "header", "theme", "xml",
        "gallery", "widget", "animation", "link", "box", "media", "download",
        "hub", "folder", "feed", "notification", "text", "title", "settings",
        "setting", "resource", "camera"
    ],
    "Maintenance": [
        "update", "modify", "change", "changed", "edit", "make", "made", "use",
        "api", "module", "custom", "improvement", "improve", "better", "class",
        "set", "adapt"
    ],
    "Refactoring": [
        "refactor", "move", "rename", "extract", "group", "remove", "stop",
        "cleanup", "clean", "delete", "unused", "sort", "tidy", "replace",
        "enable", "disable", "switch", "select", "refresh", "allow"
    ],
    "Reformat":
    ["reformat", "formatter", "format", "whitespace", "white", "space"],
    "Bugfix": [
        "fix", "close", "issue", "bug", "error", "revert", "extractor",
        "crash", "resolve", "resolved", "issued", "handling", "handle",
        "minor", "major", "minor", "fatal"
    ],
    "Branch/tag related": [
        "merge", "pull", "branch", "master", "dev", "rc", "conflict", "tag",
        "release"
    ],
    "Dependecy related": [
        "library", "version", "dependence", "dependent", "upgrade", "crypt",
        "encrypt", "encrypted", "decrypt", "outdated"
    ],
    "Document/config": [
        "readme", "doc", "comment", "data", "log", "markdown", "md", "website",
        "web", "date", "time", "link", "mail", "account", "info",
        "description", "translate", "keyword", "configure", "configuration"
    ],
    "meaningless": [
        "com", "pap", "java", "android", "code", "id", "commit", "daniel",
        "xi", "berg", "https", "you", "me", "I", "welcome", "de", "good",
        "language"
    ]
}


def getType(word, freq):
    for t in commit_types.keys():
        if word in commit_types[t]:
            return t
    if not h.spell(word):
        return "meaningless"
    elif noCh.match(word):
        return "meaningless"
    elif freq <= 1:
        return "meaningless"
    return "others"


def drawPie():
    global labels
    fig1, ax1 = plt.subplots()
    freq_arr = np.array(freqs)
    percent = 100. * freq_arr / freq_arr.sum()
    patches, texts = ax1.pie(
        freqs,
        # labels=labels,
        # autopct='%1.1f%%',
        shadow=True,
        startangle=90)
    labels = ['{0} - {1:1.2f} %'.format(i, j) for i, j in zip(labels, percent)]

    sort_legend = True
    if sort_legend:
        patches, labels, dummy = zip(*sorted(
            zip(patches, labels, freqs), key=lambda x: x[2], reverse=True))

        patches = patches[1:] + tuple([patches[0]])
        labels = labels[1:] + tuple([labels[0]])
        dummy = dummy[1:] + tuple([dummy[0]])

    plt.legend(patches,
               labels,
               loc='center left',
               bbox_to_anchor=(-0.1, 0.2),
               fontsize=8)

    ax1.axis(
        'equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    fig = ax1.get_figure()
    fig.savefig(os.path.join(plot_dir, "bag_of_words.png"),
                bbox_inches='tight')


rearrangeData()
drawPie()