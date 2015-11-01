# coding=utf-8

titleStart = len("    <title>")
titleEnd = len("</title>\n")

metaTitles = ["Wiktionnaire:", "Aide:", "Modèle:", "MediaWiki:"]

class CompleteWord:
    def __init__(self, lemma, lang, wordType, information):
        self.lemma = lemma
        self.lang = lang
        self.wordType = wordType
        self.information = information

    def __str__(self):
        base = "lemma: %s, lang: %s, type: %s [" % (self.lemma, self.lang, self.wordType)
        for key, value in self.information.iteritems():
            base += "%s => %s, " % (key, value)
        base += "]"
        return base

class State:
    def __init__(self):
        self.information = {}
        self.word = None
        self.lang = None
        self.wordType = None
        self.step = self.lookForTitle

        self.completeWords = []

    def tryCreateWord(self):
        if (
            self.word is not None and
            self.lang is not None and
            self.wordType is not None
        ):
            self.completeWords.append(
                CompleteWord(
                    self.word,
                    self.lang,
                    self.wordType,
                    self.information
                )
            )

    def consume(self, line):
        if "<page>" in line:
            self.tryCreateWord()
            self.reset()
        previousStep = None
        self.step(line)

        words = self.completeWords
        self.completeWords = []
        return words

    def lookForTitle(self, line):
        if "<title>" not in line:
            return

        title = line[titleStart:-titleEnd]
        if len(filter(lambda x: x in title, metaTitles)) != 0:
            return

        self.word = title
        self.step = self.lookForLanguage

    def lookForLanguage(self, line):
        if '== {{langue|' not in line:
            return

        if '== {{langue|fr}}' not in line:
            return
        self.lang = "fr"
        self.step = self.lookForType

    def lookForType(self, line):
        if '== {{langue|' in line:
            self.tryCreateWord()
            self.reset()
            return

        if '=== {{S|' not in line or '}} ===' not in line:
            return

        # extract from:
        # === {{S|nom|fr|flexion|num=1}} ===
        # the array:
        # ["S", "nom", "fr", "flexion", "num=1"]
        inside = line.split("{{")[1].split("}}")[0].split("|")
        if "flexion" in inside:
            #TODO: manage flexion
            return

        template = inside[1]
        if template not in ["nom", "verbe", "adjectif"]:
            return

        if self.wordType is not None:
            self.tryCreateWord()
            self.information = {}

        self.wordType = template

        if self.wordType == "nom":
            self.step = self.lookForGender
            return

        if self.wordType == "verbe":
            self.step = self.lookForTransitivity
            return

    def lookForGender(self, line):
        if not line.startswith("'''"+self.word+"'''"):
            return
        if "{{m" not in line and "{{f" not in line:
            return

        # we can find {{m| or {{f| in case an equivalent in the other gender
        # exists (for example:
        # * '''jument''' {{pron|ʒy.mɑ̃|fr}} {{f|équiv=étalon|équiv2=cheval}}
        # {{mf ? or {{fm ?  can be found in case it's not sure wether m or f :
        # * '''après-midi''' {{pron|a.pʁɛ mi.di|fr}} {{mf ?|fr}}
        # {{msing}} or {{fsing}} can be found if the noun only exists
        # in singular form: e.g sismique
        # same for {{mplur}} and {{fplural}} e.g: litisconsorts


        self.step = self.lookForType
        if (
            "{{m|" in line or
            "{{m}}" in line or
            "{{msing}}" in line or
            "{{mplur}}" in line or
            "{{msing|fr}}" in line or
            "{{masculin}}" in line
        ):
            self.information["gender"] = "m"
            return

        if (
            "{{f|" in line or
            "{{f}}" in line or
            "{{fsing}}" in line or
            "{{fplur}}" in line or
            "{{fpl}}" in line or
            "{{fsing|fr}}" in line or
            "{{féminin}}" in line
        ):
            self.information["gender"] = "f"
            return
        if (
            "{{mf" in line or
            "{{fm" in line or
            "{{masculin et féminin|" in line
        ):
            self.information["gender"] = "mf"
            return

        if (
            "{{marque}}" in line or
            "{{ms}}" in line or
            "{{familier}}" in line or
            "{{familier|fr}}" in line or
            "{{fr-rég|" in line or
            "{{fr-accord-" in line or
            "{{fr-inv" in line
        ):
            return

        print("!!!!!!!woot!!!!!")
        print(line)

    def checkForGroup(self, line):
        if '== {{langue|' in line:
            self.tryCreateWord()
            self.reset()
            return

        if not line.startswith("'''"+self.word+"'''"):
            return
        if "{{conj|grp=" not in line:
            if "{{voir-conj|" not in line:
                return

            # we take the word "yyy" in {{voir-conj|yyy}}
            self.information["voir-conj"] = line.split("{{voir-conj|")[1].split("}}")[0]
            return

        if "grp=1" in line:
            self.information["group"] = "1"
        if "grp=2" in line:
            self.information["group"] = "2"
        if "grp=3" in line:
            self.information["group"] = "3"





    def lookForTransitivity(self, line):
        if '== {{langue|' in line:
            self.tryCreateWord()
            self.reset()
            return

        if not line.startswith("'''"+self.word+"'''"):
            return
        self.checkForGroup(line)

        if "{{t" not in line and "{{i" not in line:
            return

        self.step = self.lookForType

        if (
            "{{t}}" in line or
            "{{t|nocat}}" in line or
            "{{t|nocat=non}}" in line or
            "{{t|fr}}" in line or
            "{{transitif|fr}}" in line
        ):
            self.information["transitivity"] = "t"
            return

        if (
            "{{i}}" in line or
            "{{i|nocat}}" in line or
            "{{i|nocat=non}}" in line or
            "{{i|fr}" in line or
            "{{intrans|fr}}" in line or
            "{{intransitif|fr}}" in line
        ):
            self.information["transitivity"] = "i"
            return

        if (
            "{{tr-dir}}" in line or
            "{{tr-dir|fr}}" in line
        ):
            self.information["transitivity"] = "tr-dir"
            return

        if (
            "{{tind|fr}}" in line or
            "{{tr-indir|nocat}}" in line or
            "{{tr-indir}}" in line or
            "{{tr-indir|fr}}" in line or
            "{{tr-ind|fr}}" in line
        ):
            self.information["transitivity"] = "tr-indir"
            return

        if (
            "{{invar}}" in line or
            "{{tradit}}" in line
        ):
            return

        print("!!!!!!!wat!!!!!")
        print(line)

    def reset(self):
        self.word = None
        self.lang = None
        self.wordType = None
        self.information = {}
        self.step = self.lookForTitle

state = State()
data = open("frwiktionary-20151002-pages-articles.xml", "r", 128*1024*1024)

i = 0
for line  in data:
    words = state.consume(line)
    for word in words:
        print(word)
