"""
Translates a native word into the target language and returns with descriptors.

Translates a native word into the target language and returns with optional
descriptors of definition, example use case, and audio pronunciation.



"""
import pickle
PATH_TO_TRANSLATION = './crystal-clear/language_translation/data/spanish/translation.pkl'
PATH_TO_DEFINITION = './crystal-clear/language_translation/data/spanish/definition.pkl'


def search_file(file, word):
    """Searches a file for the string associated with a word

    Parameters
    ----------
    file : str
        The file to be searched.
    word : str
        The word to be searched for.

    Returns
    ----------
    value : str or numpy array
        Value found in the loaded file.
    """
    try:
        f = pickle.load(open(file, 'rb'))
        value = f[word]
        return value
    except KeyError:
        return None


class Translator:
    def __init__(self, lang_native, lang_target):
        """
        Parameters
        ----------
        lang_native : str
            The native language.
        lang_target : str
            The target language.
        """
        self.lang_native = lang_native
        self.lang_target = lang_target

    def translate(self, word, definition=False, use_case=False, audio=False):
        """Translates a word and gets requested descriptors

        Parameters
        ----------
        word : str
            The word to be translated.
        definition : bool
            If true then retrieve the definition.
        use_case : bool
            If true then retrieve the example use case.
        audio : bool
            If true then retrieve the audio representation.

        Returns
        ----------
        translation : str
            The translated word.
        """
        translation = search_file(self._data_file("translation"), word)
        descriptors = {"definition": None, "use_case": None, "audio": None}

        if definition is True:
            descriptors["definition"]\
                = search_file(self._data_file("definition"), word)
        if use_case is True:
            descriptors["use_case"]\
                = search_file(self._data_file("use_case"), word)
        if audio is True:
            descriptors["audio"]\
                = search_file(self._data_file("audio"), word)

        return translation, descriptors

    def _data_file(self, file):
        """Returns a string representation for the data file

        Parameters
        ----------
        file : str
            The file name before .pkl (without the path).

        Returns
        -------

        """
        if file == "translation":
            return PATH_TO_TRANSLATION
        elif file == "definition":
            return PATH_TO_DEFINITION
        #return "./data/{}/{}.pkl".format(self.lang_target, file)
