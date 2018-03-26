"""
Short description of module.

Long description of module.

"""
#Python language translation module
class langTranslation:

    #Private variables
    native_Word = ""                # string
    translated_Word = ""            # string
    native_Phrase = ""              # string
    translated_Phrase = ""          # string
    none_Available = "None available."

    inPath = "./translatedWords"   # path of the file containing contents

    #Public functions
    def _init_(self, native):
        self.updateEntry(native)

    def updateEntry (self, native):
        with open(inPath, "r") as input:
            found = 0
            for line in input:
                temp = line
                english = temp.partition("$")[0]
                if native == english.strip('\n'):
                    self.native_Word,self.translated_Word,self.native_Phrase,self.translated_Phrase = temp.split('$')
                    self.native_Word.strip('\n')
                    self.native_Phrase.strip('\n')
                    self.translated_Phrase.strip('\n')
                    self.translated_Word.strip('\n')
                    found = 1
                    break
            if found == 0:
                print ("No match could be found.")

    def getNativeWord (self):
        return native_Word

    def getTranslatedWord (self):
        return translated_Word

    def getNativePhrase (self):
        if self.native_Phrase == "":
            return self.none_Available
        else:
            return native_Phrase

    def getTranslatedPhrase (self):
        if self.translated_Phrase == "":
             return self.none_Available
        else:
            return translated_Phrase