#!/usr/bin/env python3
# coding=utf-8
from __future__ import print_function
import copy
import json
import unicodedata
import codecs
import sys

titleStart = len("    <title>")
titleEnd = len("</title>\n")

encoder = json.JSONEncoder()
metaTitles = ["Wiktionnaire:", "Aide:", "Modèle:", "MediaWiki:"]

# we use "compressed" keys for the json
# which permit to decrease the output size from 200mo to 130mo
LEMMA = 'l'
TRANSITIVITY = 'trans'
GROUP = 'gr'
FLEXION = 'f'
GENDER = "g"

TENSE = "t"
MODE = "m"
PERSON = "p"
NUMBER = "n"

UNKNOWN_MODE=0
PARTICIPE_MODE=1
INDICATIVE_MODE=2
IMPERATIVE_MODE=3
CONDITIONAL_MODE=4
SUBJUNCTIVE_MODE=5

UKNOWN_TENSE=0
PRESENT_TENSE=1
PAST_TENSE=2
IMPERFECT_TENSE=3
SIMPLE_PAST_TENSE=4
FUTURE_TENSE=5

UNKNOWN_NUMBER=0
SINGULAR_NUMBER=1
PLURAL_NUMBER=2

UNKNOWN_GENDER=0
MASCULIN_GENDER=1
FEMININ_GENDER=2

UNKNOWN_PERSON=0
FIRST_PERSON=1
SECOND_PERSON=2
THIRD_PERSON=3

wordTypesToID = {
    "nom" : 1,
    "nom commun": 2,
    "nom propre": 3,
    "nom de famille": 4,
    "prénom": 5,
    "verbe": 6,
    "particule": 7,
    "adjectif": 8,
    "adj": 8,
    "adjectif possessif": 9,
    "adjectif démonstratif": 10,
    "adjectif numéral": 11,
    "adjectif interrogatif": 12,
    "adv": 13,
    "adverbe": 13,
    "adverbe interrogatif": 14,
    "adverbe relatif": 15,
    "interjection": 16,
    "prép": 17,
    "préposition": 17,
    "conjonction": 18,
    "conjonction de coordination": 19,
    "article défini": 20,
    "article partitif": 21,
    "article indéfini": 22,
    "adjectif indéfini": 23,
    "lettre": 24,
    "pronom": 25,
    "pronom relatif": 26,
    "pronom indéfini": 27,
    "pronom personnel": 28,
    "pronom démonstratif": 29,
    "pronom possessif": 30,
    "pronom interrogatif": 31,
    "onom": 32,
    "onomatopée": 33,
    "gentilés": 34,
    "symbole": 35,
    "préfixe": 36,
    "suffixe": 37,
    "locution phrase": 38,
    "locution-phrase": 38
}
validWordTypes = wordTypesToID.keys()

def remove_accents(input_str):
    if input_str is None:
        return None
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nkfd_form if not unicodedata.combining(c)])

def hash_32_bit(input_str):
    import hashlib
    return int(
        hashlib.md5(input_str.encode('utf-8')).hexdigest()[-8:],
        16
    )

def extract_templates(line):
    return list(map(
        # 2nd, until }}
        lambda s : s.split("}}")[0] ,
        # 1st: we take all the part starting with }}
        line.split("{{")[1:]
    ))

class CompleteWord:
    def __init__(self, lemma, lang, wordType, information):
        self.lemma = lemma
        self.lang = lang
        self.wordType = wordType
        self.information = copy.deepcopy(information)

    def __str__(self):
        base = "word: %s, lang: %s, type: %s [" % (self.lemma, self.lang, self.wordType)
        for key, value in self.information.iteritems():
            base += "%s => %s, " % (key, value)
        base += "]"
        return base

    def toCSVLine(self):

        normalizedLemma = remove_accents(self.lemma)
        # no need to waste space by storing two times
        # the same string (reduce size from 214mo to 200)
        if normalizedLemma == self.lemma:
            hashNormalized = -1
            normalizedLemma = ""
        else:
            hashNormalized = hash_32_bit(normalizedLemma)

        return u"%d\t%d\t%s\t%s\t%d\t%s" % (
            hash_32_bit(self.lemma),
            hashNormalized,
            self.lemma,
            normalizedLemma,
            wordTypesToID[self.wordType],
            encoder.encode(self.information)
        )


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
        if len([x for x in metaTitles if x in title]) != 0:
        #if len(filter(lambda x: x in title, metaTitles)) != 0:
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
        if line.startswith('== {{langue|'):
            self.tryCreateWord()
            self.reset()
            return

        if not line.startswith('=== {{S|'):
            return

        # extract from:
        # === {{S|nom|fr|flexion|num=1}} ===
        # the array:
        # ["S", "nom", "fr", "flexion", "num=1"]
        inside = line.split("{{")[1].split("}}")[0].split("|")

        template = inside[1]
        if template not in validWordTypes:
            #TODO: actually a lot of them only appear in `====` sections
            if template in [
                "étym",
                "étymologie",
                "synonymes",
                "Synonymes",
                "expressions",
                "apparentés",
                "voir",
                "notes",
                "attestations",
                "Traductions",
                "traductions",
                "pron",
                "prononciation",
                "faux-amis",
                "références",
                "note",
                "réf",
                "variantes",
                "ant",
                "antonymes",
                " dérivés",
                "dérivés",
                "erreur",
                "hypo",
                "dimin",
                "phrases",
                "compos",
                "trad",
                "trad-trier",
                "diminutifs",
                "homo",
                "homophones",
                "holonymes",
                "paronymes",
                "voir aussi",
                "anagrammes"
                "abréviations",
                "var",
                "var-ortho",
                "variantes dialectales",
                "anagr",
                "variantes ortho",
                "variantes ortho", #not same
                "traductions à trier",
                "syn",
                "hyperonymes",
                "vocabulaire",
                "anagrammes",
                "composés",
                "voc",
                "variante typographique",
                "variantes orthographiques",
                "méronymes",
                "dérivés autres langues",
                "abréviations",
                "quasi-synonymes",
                "transcriptions",
                "troponymes",
                "hyponymes"
            ]:
                return
            #TODO: check for inconsistency in the template names

            return

        if self.wordType is not None:
            self.tryCreateWord()
            self.information = {}

        self.wordType = template

        if "flexion" in inside:
            self.step = self.lookForFlexion
            return

        if self.wordType == "nom":
            self.step = self.lookForGender
            return

        if self.wordType == "verbe":
            self.step = self.lookForTransitivity
            return

    def lookForFlexion(self, line):
        if line.startswith('== {{') or line.startswith('=== {{'):
            self.tryCreateWord()
            self.reset()
            return

        if self.wordType == "nom" or self.wordType == "nom commun":
            if not line.startswith("# ") or "[[" not in line or "''" not in line:
                return
            if "''Pluriel" in line:
                inside = line.split("[[")[1].split("]]")[0].split("|")
                self.information[LEMMA] = inside[-1];
                self.information[FLEXION] = {NUMBER : PLURAL_NUMBER}
                return
            if "''Féminin singulier" in line:
                inside = line.split("[[")[1].split("]]")[0].split("|")
                self.information[LEMMA] = inside[-1];
                self.information[FLEXION] = {
                    GENDER: FEMININ_GENDER,
                    NUMBER : SINGULAR_NUMBER,
                }
                return

            if "''Masculin pluriel" in line:
                inside = line.split("[[")[1].split("]]")[0].split("|")
                self.information[LEMMA] = inside[-1];
                self.information[FLEXION] = {
                    GENDER: MASCULIN_GENDER,
                    NUMBER: PLURAL_NUMBER,
                }
                return
            if "''Féminin pluriel" in line:
                inside = line.split("[[")[1].split("]]")[0].split("|")
                self.information[LEMMA] = inside[-1];
                self.information[FLEXION] = {
                    GENDER: FEMININ_GENDER,
                    NUMBER: PLURAL_NUMBER,
                }
                return
            if "''Féminin d" in line:
                inside = line.split("[[")[1].split("]]")[0].split("|")
                self.information[LEMMA] = inside[-1];
                #TODO: check if we can correct witkionnary to put "Feminin singulier"
                self.information[FLEXION] = {
                    GENDER: FEMININ_GENDER,
                }
                return

            #
            if "''Graphie souvent utilisée pour ''" in line:
                return

            #print(line)
            return

        if self.wordType == "verbe":
            if not line.startswith("{{fr-verbe-flexion|"):
                return
            #TODO factorize
            inside = line.split("{{")[1].split("}}")[0].split("|")

            if "=" in inside[1]:
                #TODO the infinitive is not the first argument
                #     need to clean in the wiktionnary
                return

            #Note: the infinitive form of a verb in french
            # is also its lemma form
            self.information[LEMMA] = inside[1];

            for form in inside[2:]:
                if (
                    FLEXION in self.information and
                    len(self.information[FLEXION]) != 0
                ):
                    self.tryCreateWord()

                self.information[FLEXION] = {}


                if form == "pp=oui":
                    self.information[FLEXION][MODE] = PARTICIPE_MODE
                    self.information[FLEXION][TENSE] = PAST_TENSE
                    continue
                if form == "ppf=oui" or form == "ppfs=oui":
                    self.information[FLEXION][MODE] = PARTICIPE_MODE
                    self.information[FLEXION][TENSE] = PAST_TENSE
                    self.information[FLEXION][GENDER] = FEMININ_GENDER
                    self.information[FLEXION][NUMBER] = SINGULAR_NUMBER
                    continue

                if form == "ppfp=oui":
                    self.information[FLEXION][MODE] = PARTICIPE_MODE
                    self.information[FLEXION][TENSE] = PAST_TENSE
                    self.information[FLEXION][GENDER] = FEMININ_GENDER
                    self.information[FLEXION][NUMBER] = PLURAL_NUMBER
                    continue

                if form == "ppms=oui":
                    self.information[FLEXION][MODE] = PARTICIPE_MODE
                    self.information[FLEXION][TENSE] = PAST_TENSE
                    self.information[FLEXION][GENDER] = MASCULIN_GENDER
                    self.information[FLEXION][NUMBER] = SINGULAR_NUMBER
                    continue

                if form == "ppmp=oui":
                    self.information[FLEXION][MODE] = PARTICIPE_MODE
                    self.information[FLEXION][TENSE] = PAST_TENSE
                    self.information[FLEXION][GENDER] = MASCULIN_GENDER
                    self.information[FLEXION][NUMBER] = PLURAL_NUMBER
                    continue

                if form == "ppr=oui":
                    self.information[FLEXION][MODE] = PARTICIPE_MODE
                    self.information[FLEXION][TENSE] = PRESENT_TENSE
                    continue

                if "." in form:
                    formInfo = form.split('.')

                    mode = formInfo[0]
                    tense = formInfo[1]
                    person = formInfo[2].split('=')[0]

                    if mode == 'ind':
                        self.information[FLEXION][MODE] = INDICATIVE_MODE
                    if mode == 'imp':
                        self.information[FLEXION][MODE] = IMPERATIVE_MODE
                    if mode == 'cond':
                        self.information[FLEXION][MODE] = CONDITIONAL_MODE
                    if mode == 'sub':
                        self.information[FLEXION][MODE] = SUBJUNCTIVE_MODE

                    if tense == 'p':
                        self.information[FLEXION][TENSE] = PRESENT_TENSE
                    if tense == 'i':
                        self.information[FLEXION][TENSE] = IMPERFECT_TENSE
                    if tense == 'ps':
                        self.information[FLEXION][TENSE] = SIMPLE_PAST_TENSE
                    if tense == 'f':
                        self.information[FLEXION][TENSE] = FUTURE_TENSE

                    if person == "1s":
                        self.information[FLEXION][PERSON] = FIRST_PERSON
                        self.information[FLEXION][NUMBER] = SINGULAR_NUMBER
                    if person == "2s":
                        self.information[FLEXION][PERSON] = FIRST_PERSON
                        self.information[FLEXION][NUMBER] = SINGULAR_NUMBER
                    if person == "3s":
                        self.information[FLEXION][PERSON] = THIRD_PERSON
                        self.information[FLEXION][NUMBER] = SINGULAR_NUMBER
                    if person == "1p":
                        self.information[FLEXION][PERSON] = FIRST_PERSON
                        self.information[FLEXION][NUMBER] = PLURAL_NUMBER
                    if person == "2p":
                        self.information[FLEXION][PERSON] = SECOND_PERSON
                        self.information[FLEXION][NUMBER] = PLURAL_NUMBER
                    if person == "3p":
                        self.information[FLEXION][PERSON] = THIRD_PERSON
                        self.information[FLEXION][NUMBER] = PLURAL_NUMBER

                if form == "'=oui":
                    #TODO we ignore elision
                    continue
                if form == "réfl=oui":
                    #TODO we ignore reflection
                    continue
                if form == "impers=oui":
                    #TODO we ignore impersonal form
                    continue
                if form == "'=oui":
                    #TODO we ignore elision
                    continue
                if form.startswith("grp="):
                    #TODO we ignore group
                    continue

                #TODO log: strange flexion
                #if len(self.information["flexion"]) == 0:
                #    print(self.word)
                #    print(line)
                #    print(form)

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
            self.information[GENDER] = "m"
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
            self.information[GENDER] = "f"
            return
        if (
            "{{mf" in line or
            "{{fm" in line or
            "{{masculin et féminin|" in line
        ):
            self.information[GENDER] = "mf"
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

        #TODO: log, strange gender
        #print("strange gender")
        #print(line)

    def checkForGroup(self, line):
        if line.startswith('== {{langue|'):
            self.tryCreateWord()
            self.reset()
            return

        if not line.startswith("'''"+self.word+"'''"):
            return
        if (
            "{{conj|grp=" not in line and
            "{{conjugaison|fr|groupe=" not in line
        ):
            if "{{voir-conj|" not in line:
                return

            # we take the word "yyy" in {{voir-conj|yyy}}
            self.information["voir-conj"] = line.split("{{voir-conj|")[1].split("}}")[0]
            return

        if "grp=1" in line or "groupe=1" in line:
            self.information[GROUP] = "1"
        if "grp=2" in line or "groupe=2" in line:
            self.information[GROUP] = "2"
        if "grp=3" in line or "groupe=3" in line:
            self.information[GROUP] = "3"


    def lookForTransitivity(self, line):
        if line.startswith('== {{langue|'):
            self.tryCreateWord()
            self.reset()
            return

        if not line.startswith("'''"+self.word+"'''"):
            return
        self.checkForGroup(line)

        if "{{t" not in line and "{{i" not in line:
            return

        self.step = self.lookForType

        templates = extract_templates(line)

        def add_transitivity(newTransitivity):
            if TRANSITIVITY in self.information:
                self.tryCreateWord()
            self.information[TRANSITIVITY] = newTransitivity

        for template in templates:

            templateName = template.split("|")[0]
            if templateName in ["t", "transitif"]:
                add_transitivity("t")
                continue

            if templateName in ["i", "intrans", "intransitif"]:
                add_transitivity("i")
                continue

            if templateName == "tr-dir":
                add_transitivity("tr-dir")
                continue

            if templateName in ["tind", "tr-indir", "tr-ind"]:
                add_transitivity("tr-indir")
                continue

        #TODO: log stranged transitivy
        ##print("strange transitivy")
        ##print(line)

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
        print(word.toCSVLine())
