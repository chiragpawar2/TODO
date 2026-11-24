"""Text to phonemes, for English.

WHY THIS EXISTS

The first lip sync went straight from letters to mouth shapes. That is wrong
for English in two ways, and the second one is much worse than the first.

1. English spelling does not predict pronunciation. "though", "through",
   "tough" and "thought" share four letters and share no vowel. A letter rule
   cannot get these right, because the information is not in the letters.

2. NUMBERS AND SYMBOLS WERE SILENT. "I have 25 books" produced no mouth at all
   for the 25. A face that skips a word while the voice says it is worse than
   a face with a slightly wrong vowel - the error is a whole missing word, and
   the viewer sees it immediately.

So the pipeline is now the standard one:

    text -> NORMALISE -> words -> PHONEMES -> visemes

Normalising is exact: there is no ambiguity about how 25 is read aloud, so
that stage is simply correct. Phonemes come from a lexicon first and letter
rules only as a fallback.

ON THE LEXICON

The right lexicon is CMUdict - 134,000 words, the standard for this job, and
what every real TTS front end uses. It is not installed here, so the lexicon
below is hand-built and covers the irregular high-frequency words, which is
where nearly all the error lives: English's irregular spellings are heavily
concentrated in its commonest words ("one", "two", "said", "does", "women",
"enough"). Regular words are left to the rules, which handle them correctly
because they are regular.

`lookup()` is the seam. Drop CMUdict in there and every word becomes exact
without touching anything else.

Phonemes are ARPAbet without stress digits.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# 1. NORMALISATION - numbers, times, money, symbols
# ---------------------------------------------------------------------------

_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven",
         "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
         "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
         "eighty", "ninety"]
_SCALE = [(1_000_000_000, "billion"), (1_000_000, "million"), (1_000, "thousand")]

_ORDINAL = {
    "one": "first", "two": "second", "three": "third", "five": "fifth",
    "eight": "eighth", "nine": "ninth", "twelve": "twelfth",
}


def _under_hundred(n: int) -> list[str]:
    if n < 20:
        return [_ONES[n]]
    t, r = divmod(n, 10)
    return [_TENS[t]] + ([_ONES[r]] if r else [])


def _under_thousand(n: int) -> list[str]:
    h, r = divmod(n, 100)
    out = []
    if h:
        out += [_ONES[h], "hundred"]
    if r:
        out += _under_hundred(r)
    return out


def number_words(n: int) -> list[str]:
    """123 -> ['one','hundred','twenty','three']."""
    if n < 0:
        return ["minus"] + number_words(-n)
    if n == 0:
        return ["zero"]
    out: list[str] = []
    for value, name in _SCALE:
        if n >= value:
            q, n = divmod(n, value)
            out += _under_thousand(q) + [name]
    if n:
        out += _under_thousand(n)
    return out


def _ordinal_words(n: int) -> list[str]:
    w = number_words(n)
    last = w[-1]
    if last in _ORDINAL:
        w[-1] = _ORDINAL[last]
    elif last.endswith("y"):
        w[-1] = last[:-1] + "tieth"
    else:
        w[-1] = last + "th"
    return w


_SYMBOL = {
    "%": ["percent"], "&": ["and"], "@": ["at"], "+": ["plus"],
    "=": ["equals"], "<": ["less", "than"], ">": ["greater", "than"],
    "°": ["degrees"], "#": ["number"], "~": ["about"], "/": ["slash"],
    "₹": ["rupees"], "$": ["dollars"], "€": ["euros"], "£": ["pounds"],
}
_ABBREV = {
    "rs": ["rupees"], "dr": ["doctor"], "mr": ["mister"], "mrs": ["missus"],
    "ms": ["miss"], "st": ["street"], "vs": ["versus"], "etc": ["etcetera"],
    "ok": ["okay"], "tv": ["tee", "vee"], "prof": ["professor"], "smt": ["shrimati"],
    "lt": ["lieutenant"], "col": ["colonel"], "capt": ["captain"],
}

_TIME = re.compile(r"^(\d{1,2}):(\d{2})$")
_CLOCK = re.compile(r"^(\d{1,2})(?::(\d{2}))?(am|pm|a\.m\.?|p\.m\.?)$", re.I)
_DEC = re.compile(r"^(\d[\d,]*)\.(\d+)$")
_ORD = re.compile(r"^(\d+)(st|nd|rd|th)$", re.I)
_INT = re.compile(r"^\d[\d,]*$")
_INDIAN = re.compile(r"^\d{1,2}(,\d{2})+,\d{3}$")     # 1,00,000 / 1,25,000
_FRAC = re.compile(r"^(\d+)/(\d+)$")
_PHONE = re.compile(r"^\+?\d[\d-]{7,}\d$")
_RANGE = re.compile(r"^(\d[\d,.:]*%?)-(\d[\d,.:]*%?)$")
_UNIT_JOINED = re.compile(r"^(\d[\d,.]*)([a-z]+)$", re.I)
_RUPEE = re.compile(r"^(rs\.?|inr)(\d.*)$", re.I)
_NUM_SYM = re.compile(r"^(\d[\d,]*(?:\.\d+)?)([%°])$")
_DATE3 = re.compile(r"^(\d{1,2})[/.-](\d{1,2})[/.-](\d{2}|\d{4})$")
_DATE2 = re.compile(r"^(\d{1,2})/(\d{1,2})$")
_MONTHS = ["january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december"]
# Money in the sentence turns "1.5L" from litres into lakh.
_MONEY_CTX = re.compile(r"[₹$]|\b(rs\.?|inr|rupees?|loan|lakhs?|salary|price|cost|"
                        r"emi|budget|fees?|paid|pay|income|ctc|package|amount|"
                        r"deposit|balance|worth|crore)\b", re.I)
# Spaced digit groups that together make a phone number: "98765 43210",
# "+91 98765 43210". Joined so the phone rule reads them digit by digit.
_SPACED_PHONE = re.compile(r"(?<![\w.,])(\+?\d{2,5})((?: \d{3,5}){1,3})(?!\w|[.,]\d)")
_PLURAL_UNIT = {"teaspoons": "teaspoon", "tablespoons": "tablespoon",
                "kilos": "kilo", "kilometres": "kilometre",
                "centimetres": "centimetre", "millimetres": "millimetre",
                "milligrams": "milligram", "millilitres": "millilitre",
                "hours": "hour", "minutes": "minute", "seconds": "second",
                "litres": "litre", "grams": "gram", "rupees": "rupee",
                "dollars": "dollar", "euros": "euro", "pounds": "pound",
                "degrees": "degree", "feet": "foot", "inches": "inch", "stars": "star",
                "cents": "cent", "paise": "paisa"}
_money = False

_DEVA_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
_UNICODE_FRAC = {"½": "1/2", "¼": "1/4", "¾": "3/4", "⅓": "1/3", "⅔": "2/3",
                 "⅛": "1/8", "⅜": "3/8", "⅝": "5/8", "⅞": "7/8"}

# Units. Read only after a number (or glued to one), because "min", "l" and
# "g" are words or letters too. The few that are never anything else
# ("mg", "ml") are read wherever they appear.
_UNITS = {
    "mg": ["milligrams"], "ml": ["millilitres"], "kg": ["kilos"],
    "kgs": ["kilos"], "km": ["kilometres"], "cm": ["centimetres"],
    "mm": ["millimetres"], "gb": ["gee", "bee"], "mb": ["em", "bee"],
    "tb": ["tee", "bee"], "mbps": ["em", "bee", "pee", "ess"],
    "kmph": ["kilometres", "per", "hour"], "tsp": ["teaspoons"],
    "tbsp": ["tablespoons"], "hrs": ["hours"], "hr": ["hour"],
    "mins": ["minutes"], "min": ["minutes"], "secs": ["seconds"],
    "sec": ["seconds"], "l": ["litres"], "ltr": ["litres"], "g": ["grams"],
    "gm": ["grams"], "gms": ["grams"], "k": ["thousand"], "kwh": ["kilowatt", "hours"],
    "lakh": ["lakh"], "lakhs": ["lakh"], "ft": ["feet"], "cr": ["crore"], "crore": ["crore"],
}
_ALWAYS_UNIT = {"mg", "ml", "gb", "mbps", "kmph", "tsp", "tbsp", "kg", "km"}

# A four-digit number after these is dialled, not dated: "call 1930" is
# "one nine three zero", never "nineteen thirty".
_DIAL_CTX = {"call", "calling", "dial", "dialling", "dialing", "helpline", "number", "no", "no.", "ring", "line",
             "pin", "otp", "code", "ext", "extension", "toll-free", "sms"}

_FRAC_NAME = {2: ("half", "halves"), 3: ("third", "thirds"),
              4: ("quarter", "quarters"), 5: ("fifth", "fifths"),
              6: ("sixth", "sixths"), 8: ("eighth", "eighths"),
              10: ("tenth", "tenths"), 12: ("twelfth", "twelfths"),
              16: ("sixteenth", "sixteenths")}


def _digits(s: str) -> list[str]:
    return [_ONES[int(c)] for c in s if c.isdigit()]


def _indian_words(n: int) -> list[str]:
    """1,25,000 is read "one lakh twenty five thousand" in India, and a family
    reading their own bank balance will hear "one hundred and twenty five
    thousand" as a mistake."""
    out: list[str] = []
    crore, n = divmod(n, 10_000_000)
    lakh, n = divmod(n, 100_000)
    if crore:
        out += (_indian_words(crore) if crore >= 100_000 else number_words(crore)) + ["crore"]
    if lakh:
        out += _under_hundred(lakh) + ["lakh"]
    if n:
        out += number_words(n)
    return out or ["zero"]


def _int_words(tok: str) -> list[str]:
    n = int(tok.replace(",", ""))
    if _INDIAN.match(tok):
        return _indian_words(n)
    return number_words(n)


def _clock_words(h: int, mi: int | None) -> list[str]:
    out = number_words(h)
    if mi is None:
        return out
    if mi == 0:
        return out + ["oh", "clock"]
    if mi < 10:
        return out + ["oh"] + number_words(mi)
    return out + number_words(mi)


def _one(num: str, unit: list[str]) -> list[str]:
    """ "1 tsp" is one teaspoon, not one teaspoons."""
    if num.strip(".,") == "1" and unit and unit[-1] in _PLURAL_UNIT:
        return unit[:-1] + [_PLURAL_UNIT[unit[-1]]]
    return unit


def _say(tok: str, prev: str, prev_num: bool) -> tuple[list[str], bool] | None:
    """Words for one numeric-ish token, and whether it was a number. None if
    the token is not one this stage handles."""
    low = tok.lower()
    if m := _CLOCK.match(tok):
        mi = int(m.group(2)) if m.group(2) else None
        return _clock_words(int(m.group(1)), mi) + (
            ["ay", "em"] if low[len(m.group(1)) + (len(m.group(2)) + 1 if m.group(2) else 0)] == "a"
            else ["pee", "em"]), True
    if m := _TIME.match(tok):
        h, mi = int(m.group(1)), int(m.group(2))
        if 13 <= h <= 23 or (h == 0 and len(m.group(1)) == 2):
            # 24-hour clock: "21:00" is "nine pm", "18:45" "six forty five pm".
            h12 = h - 12 if h else 12
            return _clock_words(h12, mi or None) + (["pee", "em"] if h else ["ay", "em"]), True
        return _clock_words(h, mi), True
    if m := _DATE3.match(tok):
        d, mo, y = int(m.group(1)), int(m.group(2)), m.group(3)
        if 1 <= d <= 31 and 1 <= mo <= 12:
            yr = _say(("20" + y) if len(y) == 2 else y, "", False)
            return _ordinal_words(d) + [_MONTHS[mo - 1]] + (yr[0] if yr else []), True
    if m := _DATE2.match(tok):
        d, mo = int(m.group(1)), int(m.group(2))
        # "14/02", "23/11": a date. "1/2", "3/4" stay fractions.
        if 1 <= d <= 31 and 1 <= mo <= 12 and (d >= mo or m.group(2).startswith("0")
                                                or m.group(1).startswith("0")) and d > 1:
            return _ordinal_words(d) + [_MONTHS[mo - 1]], True
    if m := _NUM_SYM.match(tok):
        num = _say(m.group(1), prev, False)
        if num:
            return num[0] + _SYMBOL[m.group(2)], True
    if m := _ORD.match(tok):
        return _ordinal_words(int(m.group(1))), True
    if tok[:1] in "₹$€£" and (m := _DEC.match(tok[1:])) and len(m.group(2)) == 2:
        # ₹99.99 is "ninety nine rupees ninety nine paise", not "point".
        whole, part = _int_words(m.group(1)), int(m.group(2))
        return whole + _SYMBOL[tok[0]] + ((number_words(part) + [_CURRENCY_SUB[tok[0]]])
                                          if part else []), True
    if m := _DECADE.match(tok):
        yr = _say(m.group(1), "", False)[0] if len(m.group(1)) == 4 else number_words(int(m.group(1)))
        last = yr[-1]
        yr[-1] = last[:-1] + "ies" if last.endswith("y") else last + "s"
        return yr, True
    if tok[:1] in "₹$€£" and len(tok) > 1:
        rest = _say(tok[1:], "rs", False)
        if rest:
            return _SYMBOL[tok[0]] + rest[0], True
    if m := _RUPEE.match(tok):
        rest = _say(m.group(2), "rs", False)
        if rest:
            return ["rupees"] + rest[0], True
    if m := _FRAC.match(tok):
        n, d = int(m.group(1)), int(m.group(2))
        if d in _FRAC_NAME and 0 < n < d:
            one, many = _FRAC_NAME[d]
            head = ["and"] if prev_num else []
            if n == 1:
                return head + (["a"] if prev_num or d == 2 else ["one"]) + [one], True
            return head + number_words(n) + [many], True
        return number_words(n) + ["by"] + number_words(d), True
    if _PHONE.match(tok) and sum(c.isdigit() for c in tok) >= 8:
        # A phone number is read digit by digit, in its groups.
        return _digits(tok), True
    if m := _DEC.match(tok):
        return _int_words(m.group(1)) + ["point"] + _digits(m.group(2)), True
    if _INT.match(tok):
        digits = tok.replace(",", "")
        n = int(digits)
        if prev.lower() in _DIAL_CTX and "," not in tok and len(digits) >= 3:
            return _digits(digits), True
        if len(digits) >= 10 and "," not in tok:
            return _digits(digits), True
        if (len(tok) == 6 and "," not in tok and tok[0] != "0" and not _money
                and prev.lower() not in ("rs", "rs.", "inr", "rupees")):
            # A bare six-digit number is a PIN code, said digit by digit.
            return _digits(digits), True
        # A four-digit number in a sentence is usually a year, and a year
        # is read in pairs: "nineteen forty seven", not "one thousand...".
        if 1100 <= n <= 2099 and len(tok) == 4:
            return _under_hundred(n // 100) + (
                ["oh"] + number_words(n % 100) if 0 < n % 100 < 10
                else number_words(n % 100) if n % 100 else ["hundred"]), True
        return _int_words(tok), True
    if m := _RANGE.match(tok):
        a = _say(m.group(1), prev, False)
        b = _say(m.group(2), prev, False)
        if a and b:
            return a[0] + ["to"] + b[0], True
    if m := _UNIT_JOINED.match(tok):
        unit = m.group(2).lower()
        if unit == "l" and _money:
            unit = "lakh"
        if unit in _UNITS:
            num = _say(m.group(1), prev, False)
            if num:
                return num[0] + _one(m.group(1), _UNITS[unit]), True
    if "-" in tok and any(c.isdigit() for c in tok):
        # 5-star, covid-19: say each part.
        out: list[str] = []
        for part in tok.split("-"):
            if not part:
                continue
            r = _say(part, prev, False)
            out += r[0] if r else [part]
        return out, False
    if prev_num and low in _UNITS:
        if low == "l" and _money:
            return ["lakh"], False
        return _one(prev, _UNITS[low]), False
    if low in _ALWAYS_UNIT:
        return _one(prev, _UNITS[low]), False
    if prev_num and low in ("am", "a.m", "a.m."):
        return ["ay", "em"], False
    if prev_num and low in ("pm", "p.m", "p.m."):
        return ["pee", "em"], False
    return None


# ---------------------------------------------------------------------------
# Whole-text rewrites, done before the text is split into tokens: things
# whose reading depends on a neighbour (a minus sign, "/month", "Henry VIII").
# ---------------------------------------------------------------------------

_LETTER_NAME = {
    "a": "ay", "b": "bee", "c": "see", "d": "dee", "e": "ee", "f": "ef",
    "g": "jee", "h": "aitch", "i": "eye", "j": "jay", "k": "kay", "l": "el",
    "m": "em", "n": "en", "o": "oh", "p": "pee", "q": "cue", "r": "ar",
    "s": "ess", "t": "tee", "u": "you", "v": "vee", "w": "double you",
    "x": "ex", "y": "why", "z": "zed",
}
_ROMAN = {"II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8,
          "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13, "XIV": 14,
          "XV": 15, "XVI": 16, "XVIII": 18, "XX": 20}
# After these a numeral is a number ("Class four"); after a person's name
# it is a regnal ordinal ("Henry the eighth").
_ROMAN_COUNT = {"class", "chapter", "part", "standard", "std", "book", "volume",
                "vol", "phase", "grade", "act", "scene", "section", "level",
                "stage", "war", "world", "unit", "round", "season", "episode",
                "type", "sector", "block", "wing", "gate", "page", "form"}
_PER = ("month|mo|day|week|wk|year|yr|annum|hour|hr|h|night|person|head|"
        "piece|pc|kg|kilo|km|litre|liter|l|unit|plate|min|minute|sec|second|"
        "sq ?ft|month's")
_PRE = [
    (re.compile(r"(\d)/-"), r"\1"),                                  # ₹2,500/-
    (re.compile(r"(?<![\w.,%)])[-−–](?=\d)"), "minus "),              # -4°C
    (re.compile(r"(\d)\s*°\s*C\b"), r"\1 degrees celsius"),
    (re.compile(r"(\d)\s*°\s*F\b"), r"\1 degrees fahrenheit"),
    (re.compile(r"km/hr?\b", re.I), "kmph"),
    (re.compile(r"(\d)\s*/\s*(" + _PER + r")\b", re.I), r"\1 per \2"),
    (re.compile(r"\b24\s*[x×/]\s*7\b"), "twenty four seven"),
    (re.compile(r"\b(\d+)\s*[x×]\s*(\d+)\b"), r"\1 by \2"),
    (re.compile(r"\b(\d+(?:\.\d+)?)[x×](?![\w])"), r"\1 times"),
    (re.compile(r"(?<![\w])[x×](\d+)\b"), r"times \1"),
    (re.compile(r"(\d+)\s*'\s*(\d+)\s*(?:\"|''|in\b|inches\b)?"), r"\1 feet \2 inches"),
    (re.compile(r"(\d+)\s*(?:ft|feet)\s+(\d+)\s*(?:in|inch|inches)\b"), r"\1 feet \2 inches"),
    (re.compile(r"(\d+(?:\.\d+)?)\s*[★⭐]"), r"\1 stars"),
    (re.compile(r"(\d(?:st|nd|rd|th))\s*/\s*(?=\d)", re.I), r"\1 or "),
    (re.compile(r"\b(\d+)/(\d+)(?:st|nd|rd|th)\b", re.I), r"\1/\2"),
    (re.compile(r"\b(Dr|Mr|Mrs|Ms|Prof|Sr|Jr|Smt|Shri|Lt|Col|Capt)\.(?=\s+[A-Z])"), r"\1"),
    (re.compile(r"\b(No|no|Nos|nos)\.\s*(?=\d)"), "number "),
    (re.compile(r"\b(Q|H)([1-4])\b"), lambda m: _LETTER_NAME[m.group(1).lower()] + " " + m.group(2)),
    (re.compile(r"\bFY\s?'?(\d{2,4})\b"), r"ef why \1"),
]
_ROMAN_RE = re.compile(r"\b([A-Z][a-z]+)\s+(" + "|".join(sorted(_ROMAN, key=len, reverse=True))
                       + r")\b(?!['\w])")
_DECADE = re.compile(r"^'?(\d{2}|\d{4})s$")
_CURRENCY_SUB = {"₹": "paise", "$": "cents", "€": "cents", "£": "pence"}


def _roman(m: re.Match) -> str:
    name, num = m.group(1), _ROMAN[m.group(2)]
    if name.lower() in _ROMAN_COUNT:
        return f"{name} {' '.join(number_words(num))}"
    return f"{name} the {' '.join(_ordinal_words(num))}"


def _prepass(text: str) -> str:
    for rx, rep in _PRE:
        text = rx.sub(rep, text)
    return _ROMAN_RE.sub(_roman, text)


def _join_phone(m: re.Match) -> str:
    whole = m.group(0)
    if sum(c.isdigit() for c in whole) >= 10:
        return whole.replace(" ", "-")
    return whole


def normalise(text: str) -> list[str]:
    """Turn raw text into the words a voice would actually say.

    This stage is exact. There is no guesswork about how "7:30" is read, so
    nothing here is an approximation - unlike the letter rules below.
    """
    global _money
    text = _prepass(text.translate(_DEVA_DIGITS))
    _money = bool(_MONEY_CTX.search(text))
    if " " in text and any(c.isdigit() for c in text):
        text = _SPACED_PHONE.sub(_join_phone, text)
    for k, v in _UNICODE_FRAC.items():
        if k in text:
            text = text.replace(k, " " + v)
    # The danda is a full stop. Glued to a Latin word ("500 mg।") it would
    # drag that word into the Devanagari reader, which cannot say it.
    text = text.replace("।", ".").replace("॥", ".")
    out: list[str] = []
    prev, prev_num = "", False
    for raw in text.split():
        # strip trailing punctuation but keep it as its own token so the
        # track still pauses on it. A full stop at the END of a token is
        # always a stop: "platform 5." is five, then a pause. A decimal point
        # has digits after it ("3.5"), so it is never the last character.
        trail = ""
        if raw.lower() in ("a.m.", "p.m."):
            raw = raw[:-1] + "@"     # keep the abbreviation whole
        while raw and raw[-1] in ".,!?;:":
            trail = raw[-1] + trail
            raw = raw[:-1]
        raw = raw.replace("@", ".")
        if not raw:
            out.append(trail)
            prev, prev_num = "", False
            continue

        tok = raw.strip("\"'()[]")
        if not tok:
            if trail:
                out.append(trail)
            continue
        low = tok.lower().rstrip(".")

        said = _say(tok, prev, prev_num)
        if said is not None:
            out += said[0]
            prev_num = said[1]
        elif low in _ABBREV:
            out += _ABBREV[low]
            prev_num = False
        elif any(c in _SYMBOL for c in tok):
            # Split into runs, so "50%" is "fifty percent" and not
            # "five zero percent" - digits next to a symbol are still a number.
            for part in re.findall(r"\d+|[A-Za-z]+|.", tok):
                if part in _SYMBOL:
                    out += _SYMBOL[part]
                elif part.isdigit():
                    out += number_words(int(part))
                elif part.isalpha():
                    out.append(part)
            prev_num = False
        else:
            out.append(tok)
            prev_num = False
        prev = tok
        if trail:
            out.append(trail)
            prev_num = prev_num and trail not in ".!?"
    return [w for w in out if w]


# ---------------------------------------------------------------------------
# 2. LEXICON - the irregulars, where nearly all the error is
# ---------------------------------------------------------------------------

_LEX_RAW = {
    # the words a letter rule gets wrong, and that appear constantly
    "a": "AH", "the": "DH AH", "to": "T UW", "do": "D UW", "does": "D AH Z",
    "done": "D AH N", "of": "AH V", "off": "AO F", "one": "W AH N",
    "two": "T UW", "three": "TH R IY", "four": "F AO R", "five": "F AY V",
    "six": "S IH K S", "seven": "S EH V AH N", "eight": "EY T",
    "nine": "N AY N", "ten": "T EH N", "eleven": "IH L EH V AH N",
    "twelve": "T W EH L V", "twenty": "T W EH N T IY",
    "thirty": "TH ER T IY", "forty": "F AO R T IY", "fifty": "F IH F T IY",
    "hundred": "HH AH N D R AH D", "thousand": "TH AW Z AH N D",
    "million": "M IH L Y AH N", "zero": "Z IH R OW", "point": "P OY N T",
    "rupees": "R UW P IY Z", "percent": "P ER S EH N T",
    "i": "AY", "you": "Y UW", "your": "Y AO R", "he": "HH IY",
    "she": "SH IY", "we": "W IY", "they": "DH EY", "them": "DH EH M",
    "their": "DH EH R", "there": "DH EH R", "these": "DH IY Z",
    "those": "DH OW Z", "this": "DH IH S", "that": "DH AE T",
    "what": "W AH T", "who": "HH UW", "where": "W EH R", "when": "W EH N",
    "why": "W AY", "how": "HH AW", "which": "W IH CH",
    "was": "W AH Z", "were": "W ER", "are": "AA R", "is": "IH Z",
    "been": "B IH N", "have": "HH AE V", "has": "HH AE Z", "had": "HH AE D",
    "said": "S EH D", "says": "S EH Z", "say": "S EY",
    "come": "K AH M", "came": "K EY M", "some": "S AH M", "none": "N AH N",
    "could": "K UH D", "would": "W UH D", "should": "SH UH D",
    "through": "TH R UW", "though": "DH OW", "thought": "TH AO T",
    "tough": "T AH F", "rough": "R AH F", "enough": "IH N AH F",
    "cough": "K AO F", "laugh": "L AE F", "daughter": "D AO T ER",
    "eye": "AY", "eyes": "AY Z", "buy": "B AY", "by": "B AY",
    "women": "W IH M AH N", "woman": "W UH M AH N", "water": "W AO T ER",
    "many": "M EH N IY", "any": "EH N IY", "again": "AH G EH N",
    "friend": "F R EH N D", "people": "P IY P AH L", "busy": "B IH Z IY",
    "business": "B IH Z N AH S", "minute": "M IH N AH T",
    "knight": "N AY T", "know": "N OW", "knew": "N UW", "knee": "N IY",
    "write": "R AY T", "wrong": "R AO NG", "wrap": "R AE P",
    "hour": "AW ER", "honest": "AA N AH S T", "honour": "AA N ER",
    "island": "AY L AH N D", "listen": "L IH S AH N", "castle": "K AE S AH L",
    "often": "AO F AH N", "answer": "AE N S ER", "sword": "S AO R D",
    "school": "S K UW L", "chaos": "K EY AA S", "character": "K EH R IH K T ER",
    "machine": "M AH SH IY N", "chef": "SH EH F", "ocean": "OW SH AH N",
    "sure": "SH UH R", "sugar": "SH UH G ER", "question": "K W EH S CH AH N",
    "nature": "N EY CH ER", "picture": "P IH K CH ER",
    "phone": "F OW N", "photo": "F OW T OW", "graph": "G R AE F",
    "rhythm": "R IH DH AH M", "wednesday": "W EH N Z D EY",
    "colonel": "K ER N AH L", "once": "W AH N S", "only": "OW N L IY",
    "other": "AH DH ER", "another": "AH N AH DH ER", "mother": "M AH DH ER",
    "father": "F AA DH ER", "brother": "B R AH DH ER",
    "very": "V EH R IY", "every": "EH V R IY", "city": "S IH T IY",
    "baby": "B EY B IY", "happy": "HH AE P IY", "family": "F AE M AH L IY",
    "my": "M AY", "me": "M IY", "be": "B IY", "see": "S IY", "go": "G OW",
    "no": "N OW", "so": "S OW", "now": "N AW", "new": "N UW",
    "put": "P UH T", "push": "P UH SH", "pull": "P UH L", "full": "F UH L",
    "good": "G UH D", "book": "B UH K", "books": "B UH K S",
    "look": "L UH K", "foot": "F UH T", "food": "F UW D", "blood": "B L AH D",
    "door": "D AO R", "floor": "F L AO R", "poor": "P UH R",
    "heart": "HH AA R T", "heard": "HH ER D", "learn": "L ER N",
    "earth": "ER TH", "early": "ER L IY", "world": "W ER L D",
    "work": "W ER K", "word": "W ER D", "worth": "W ER TH",
    "great": "G R EY T", "break": "B R EY K", "steak": "S T EY K",
    "bread": "B R EH D", "head": "HH EH D", "ready": "R EH D IY",
    "dead": "D EH D", "death": "D EH TH", "health": "HH EH L TH",
    "please": "P L IY Z", "thank": "TH AE NG K", "thanks": "TH AE NG K S",
    "yes": "Y EH S", "okay": "OW K EY", "hello": "HH AH L OW",
    "today": "T AH D EY", "tomorrow": "T AH M AA R OW",
    "yesterday": "Y EH S T ER D EY", "morning": "M AO R N IH NG",
    "night": "N AY T", "light": "L AY T", "right": "R AY T",
    "might": "M AY T", "high": "HH AY", "sign": "S AY N",
    "half": "HH AE F", "calm": "K AA M", "palm": "P AA M",
    "talk": "T AO K", "walk": "W AO K", "call": "K AO L", "ball": "B AO L",
    "small": "S M AO L", "all": "AO L", "also": "AO L S OW",
    "climb": "K L AY M", "comb": "K OW M", "lamb": "L AE M",
    "doubt": "D AW T", "debt": "D EH T", "subtle": "S AH T AH L",
    "science": "S AY AH N S", "scene": "S IY N", "scissors": "S IH Z ER Z",
    "use": "Y UW Z", "used": "Y UW Z D", "usually": "Y UW ZH AH L IY",
    "beautiful": "B Y UW T AH F AH L", "europe": "Y UH R AH P",
    "give": "G IH V", "live": "L IH V", "love": "L AH V", "above": "AH B AH V",
    "move": "M UW V", "prove": "P R UW V", "lose": "L UW Z", "close": "K L OW Z",
    "whose": "HH UW Z", "shoe": "SH UW", "true": "T R UW", "blue": "B L UW",
    "chapati": "CH AH P AA T IY", "namaste": "N AH M AH S T EY",
    "india": "IH N D IY AH", "aai": "AA IY",
    # letter names, for spelt-out codes (Q3, FY25)
    "ay": "EY", "bee": "B IY", "dee": "D IY", "ee": "IY", "ef": "EH F",
    "jee": "JH IY", "aitch": "EY CH", "jay": "JH EY", "kay": "K EY",
    "el": "EH L", "em": "EH M", "en": "EH N", "pee": "P IY", "cue": "K Y UW",
    "ar": "AA R", "ess": "EH S", "tee": "T IY", "vee": "V IY", "ex": "EH K S",
    "zed": "Z EH D", "paise": "P AY S AH", "minus": "M AY N AH S",
    "celsius": "S EH L S IY AH S", "per": "P ER", "times": "T AY M Z",
}
LEXICON: dict[str, list[str]] = {k: v.split() for k, v in _LEX_RAW.items()}


def lookup(word: str) -> list[str] | None:
    """The seam. A real dictionary (CMUdict) plugs in right here."""
    return LEXICON.get(word.lower())


# ---------------------------------------------------------------------------
# 3. LETTER RULES - the fallback, for regular words only
# ---------------------------------------------------------------------------

_RULES: list[tuple[str, str]] = [
    # longest first; order matters
    ("ough", "AH F"), ("augh", "AE F"), ("tion", "SH AH N"),
    ("sion", "ZH AH N"), ("ture", "CH ER"), ("ight", "AY T"),
    ("tch", "CH"), ("dge", "JH"), ("ck", "K"), ("qu", "K W"),
    ("sch", "S K"), ("ph", "F"), ("gh", ""), ("kn", "N"), ("wr", "R"),
    ("wh", "W"), ("ch", "CH"), ("sh", "SH"), ("th", "TH"), ("ng", "NG"),
    ("ee", "IY"), ("ea", "IY"), ("ie", "IY"), ("ei", "EY"),
    ("oo", "UW"), ("ou", "AW"), ("ow", "AW"), ("oi", "OY"), ("oy", "OY"),
    ("au", "AO"), ("aw", "AO"), ("ai", "EY"), ("ay", "EY"),
    ("oa", "OW"), ("oe", "OW"),
    ("ar", "AA R"), ("er", "ER"), ("ir", "ER"), ("ur", "ER"), ("or", "AO R"),
]
_LETTER = {
    "a": "AE", "b": "B", "c": "K", "d": "D", "e": "EH", "f": "F", "g": "G",
    "h": "HH", "i": "IH", "j": "JH", "k": "K", "l": "L", "m": "M", "n": "N",
    "o": "AA", "p": "P", "q": "K", "r": "R", "s": "S", "t": "T", "u": "AH",
    "v": "V", "w": "W", "x": "K S", "y": "Y", "z": "Z",
}
_LONG = {"a": "EY", "e": "IY", "i": "AY", "o": "OW", "u": "UW"}
_VOWELS = set("aeiou")


def _rules(word: str) -> list[str]:
    w = word.lower()
    # magic e: "ride" has a long I and no final vowel sound of its own
    magic = (len(w) > 3 and w.endswith("e") and w[-2] not in _VOWELS
             and any(c in _VOWELS for c in w[:-2]))
    if magic:
        w = w[:-1]
    # a short word ending in y is the "eye" diphthong (my, fly, why);
    # a longer one is the EE of "happy"
    if len(w) > 1 and w[-1] in ("y", "i"):
        # One-character sentinels: the old "i_long" / "i_ee" markers were
        # letters, so a digraph rule could eat into them ("hai" -> h + "ai"
        # + "_long" = HH EY L AA NG, "sunday" grew an extra syllable).
        w = w[:-1] + ("\x01" if len(w) <= 3 else "\x02")

    out: list[str] = []
    i = 0
    n = len(w)
    while i < n:
        if w[i] == "\x01":
            out.append("AY"); i += 1; continue
        if w[i] == "\x02":
            out.append("IY"); i += 1; continue
        for seq, ph in _RULES:
            if w.startswith(seq, i):
                out += ph.split()
                i += len(seq)
                break
        else:
            c = w[i]
            if c in _VOWELS and magic and _last_vowel_index(w) == i:
                out.append(_LONG[c])
            elif c.isalpha():
                out += _LETTER.get(c, "B").split()
            i += 1
    return [p for j, p in enumerate(out) if j == 0 or p != out[j - 1]]


def _last_vowel_index(w: str) -> int:
    for i in range(len(w) - 1, -1, -1):
        if w[i] in _VOWELS:
            return i
    return -1


def phonemes(word: str) -> list[str]:
    """Best available pronunciation for one word."""
    hit = lookup(word)
    if hit is not None:
        return list(hit)
    core = "".join(c for c in word if c.isalpha())
    if not core:
        return []
    return _rules(core)
