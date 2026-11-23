import json, sys
from homebot.face import reading as R, expressions as X, lexicon as L
J = lambda s: sorted(s)
d = {
 "EXACT": {" ".join(k): list(v) for k, v in R._EXACT.items()},
 "CEXACT": {" ".join(k): list(v) for k, v in R._CANON_EXACT.items()},
 "STEMS": {k: list(v) for k, v in R._STEMS.items()}, "STEM_LENS": R._STEM_LENS, "LONGEST": R._LONGEST,
 "DEVA": {k: [list(v[0]), J(v[1])] for k, v in R._DEVA_STEMS.items()}, "DEVA_LENS": R._DEVA_LENS,
 "SINGLE": {k: list(v) for k, v in R._SINGLE.items()}, "DELETES": R._DELETES, "TYPO": R._TYPO,
 "TYPO_BLOCK": J(R._TYPO_BLOCK), "EN_SUFFIX": J(R._EN_SUFFIX), "FREE_STEMS": J(R._FREE_STEMS),
 "NEG_FLIP": R._NEG_FLIP, "NEGATORS": J(R._NEGATORS), "SCOPE_VERBS": J(R._SCOPE_VERBS),
 "HEDGE_VERBS": J(R._HEDGE_VERBS), "COMPARE": J(R._COMPARE), "KAR": J(R._KAR), "POST_NEG": J(R._POST_NEG),
 "BREAK": J(R._BREAK), "OTHERS_FUTURE": J(R._OTHERS_FUTURE), "CONTRAST": J(R._CONTRAST),
 "EMOJI": R._EMOJI, "MILD_EMOJI": J(R._MILD_EMOJI), "POSITIVE": J(R._POSITIVE), "NEGATIVE": J(R._NEGATIVE),
 "SARC_PRAISE": J(R._SARC_PRAISE), "NEUTRAL": J(R._NEUTRAL), "PERSON": J(R._PERSON), "DEVICE": J(R._DEVICE),
 "EXAM": J(R._EXAM), "COPULA": J(R._COPULA), "STOP_OK": J(R._STOP_OK), "MARATHI": J(R._MARATHI),
 "ANAND_CTX": J(R._ANAND_CTX), "NEG_PHRASE": J(R._NEG_PHRASE), "EVENT_KEYS": J(R._EVENT_KEYS),
 "KILL_KEYS": J(R._KILL_KEYS), "NOISY": J(R._NOISY), "BODY": J(L.BODY), "PLANT": J(L.PLANT),
 "PAIN": list(L.PAIN_WORDS), "NEG_ONLY": L.NEG_ONLY, "GLUE": J(L.DESI_GLUE), "CGLUE": J(R._CANON_GLUE),
 "STRONG": J(R._STRONG), "ACRONYMS": J(R._ACRONYMS), "UP": J(R._UP), "SO_STOP": J(R._SO_STOP),
 "DOWN2": {" ".join(k): v for k, v in R._DOWN2.items()}, "UP2": [" ".join(k) for k in R._UP2],
 "DOWN1": R._DOWN1, "FLAT_EXEMPT": J(R._FLAT_EXEMPT_START), "TITLES": J(R._TITLES), "KIN": J(R._KIN),
 "OCCASION": J(R._OCCASION), "FAM_ORDER": R._FAM_ORDER,
 "LEVELS": {k: list(v) for k, v in X.LEVELS.items()}, "DEF_LEVELS": list(X._DEFAULT_LEVELS),
 "RE": {k: getattr(R, k).pattern for k in ("_TO_BOT_INSULT", "_TO_BOT_PRAISE", "_SARC_AGAIN", "_SARC_EVENT",
        "_SARC_NOUN", "_SARC_SET", "_SARC_MORE", "_LAUGH", "_BANG_LOSS", "_BANG_RUSH", "_BANG_MED")},
 "TO_BOT_WRONG": L.TO_BOT_WRONG.pattern,
}
print(json.dumps(d, ensure_ascii=False, separators=(",", ":")))
