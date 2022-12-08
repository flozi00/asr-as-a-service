from transformers import AutoModelForSpeechSeq2Seq
from optimum.onnxruntime import ORTModelForSpeechSeq2Seq

MODEL_MAPPING = {
    "small":{
        "german": {"name": "flozi00/whisper-small-german", "class": AutoModelForSpeechSeq2Seq},
        "english": {"name": "openai/whisper-small.en", "class": AutoModelForSpeechSeq2Seq},
        "universal": {"name": "openai/whisper-small", "class": AutoModelForSpeechSeq2Seq},
    },
    "medium":{
        "german": {"name": "flozi00/whisper-medium-german", "class": AutoModelForSpeechSeq2Seq},
        "english": {"name": "openai/whisper-medium.en", "class": AutoModelForSpeechSeq2Seq},
        "universal": {"name": "openai/whisper-medium", "class": AutoModelForSpeechSeq2Seq},
    },
    "large":{
        "universal": {"name": "openai/whisper-large-v2", "class": AutoModelForSpeechSeq2Seq},
    },
}

LANGUAGE_CODES = {
    "en": "english",
    #"zh": "chinese",
    "de": "german",
    "es": "spanish",
    "ru": "russian",
    #"ko": "korean",
    "fr": "french",
    #"ja": "japanese",
    #"pt": "portuguese",
    #"tr": "turkish",
    #"pl": "polish",
    #"ca": "catalan",
    #"nl": "dutch",
    #"ar": "arabic",
    #"sv": "swedish",
    "it": "italian",
    #"id": "indonesian",
    #"hi": "hindi",
    #"fi": "finnish",
    #"vi": "vietnamese",
    #"iw": "hebrew",
    #"uk": "ukrainian",
    #"el": "greek",
    #"ms": "malay",
    #"cs": "czech",
    #"ro": "romanian",
    #"da": "danish",
    #"hu": "hungarian",
    #"ta": "tamil",
    #"no": "norwegian",
    #"th": "thai",
    #"ur": "urdu",
    #"hr": "croatian",
    #"bg": "bulgarian",
    #"lt": "lithuanian",
    #"la": "latin",
    #"mi": "maori",
    #"ml": "malayalam",
    #"cy": "welsh",
    #"sk": "slovak",
    #"te": "telugu",
    #"fa": "persian",
    #"lv": "latvian",
    #"bn": "bengali",
    #"sr": "serbian",
    #"az": "azerbaijani",
    #"sl": "slovenian",
    #"kn": "kannada",
    #"et": "estonian",
    #"mk": "macedonian",
    #"br": "breton",
    #"eu": "basque",
    #"is": "icelandic",
    #"hy": "armenian",
    #"ne": "nepali",
    #"mn": "mongolian",
    #"bs": "bosnian",
    #"kk": "kazakh",
    #"sq": "albanian",
    #"sw": "swahili",
    #"gl": "galician",
    #"mr": "marathi",
    #"pa": "punjabi",
    #"si": "sinhala",
    #"km": "khmer",
    #"sn": "shona",
    #"yo": "yoruba",
    #"so": "somali",
    #"af": "afrikaans",
    #"oc": "occitan",
    #"ka": "georgian",
    #"be": "belarusian",
    #"tg": "tajik",
    #"sd": "sindhi",
    #"gu": "gujarati",
    #"am": "amharic",
    #"yi": "yiddish",
    #"lo": "lao",
    #"uz": "uzbek",
    #"fo": "faroese",
    #"ht": "haitian creole",
    #"ps": "pashto",
    #"tk": "turkmen",
    #"nn": "nynorsk",
    #"mt": "maltese",
    #"sa": "sanskrit",
    #"lb": "luxembourgish",
    #"my": "myanmar",
    #"bo": "tibetan",
    #"tl": "tagalog",
    #"mg": "malagasy",
    #"as": "assamese",
    #"tt": "tatar",
    #"haw": "hawaiian",
    #"ln": "lingala",
    #"ha": "hausa",
    #"ba": "bashkir",
    #"jw": "javanese",
    #"su": "sundanese",
}

LANG_MAPPING = {v: k for k, v in LANGUAGE_CODES.items()}

