"""Text-related stuff I meant to put in site-packages
"""


class FoundItem(Exception):
    pass


class DataError(Exception):
    pass


def splitjoin(orig, zoek, vervang):
    """
    dit is een routine waarin de binnenkomende string eerst gesplitst wordt
    in woorden (gescheiden door 1 of meer spaties en/of tabs e.d.);
    tegelijkertijd worden de scheidende strings ook bepaald.
    Daarna worden de woorden die vervangen moeten worden vervangen
    en tenslotte wordt de string weer aan elkaar geplakt.
    De truc is dat we de scheidende strings intact laten.
    Deze routine zit ook in site-packages\mystuff.py
    """
    heeftreturn = False
    if orig[-1:] == "\n":
        heeftreturn = True
    h = orig.split()
    s = orig.split(h[0])  # eerste woord eraf halen
    sp = []  # list met "split's
    for w in h[1:]:
        s = s[1].split(w)
        sp.append(s[0])
    for i in enumerate(h):
        if h[i[0]] == zoek:
            h[i[0]] = vervang
    news = ""
    for i in enumerate(sp):
        news = h[i[0]].join((news, i[1]))
    news = news + h[-1]
    if heeftreturn:
        news = news + "\n"
    return news


def test_splitjoin():
    """testing the previous
    """
    orig = "Hallo, dit  is een       test"
    zoek = "is"
    vervang = "was"
    news = splitjoin(orig, zoek, vervang)
    print(orig)
    print(news)

if __name__ == "__main__":
    ## raise FoundItem
    ## raise DataError
    test_splitjoin()
