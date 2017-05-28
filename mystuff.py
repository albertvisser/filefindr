
class FoundItem(Exception):
    pass

class DataError(Exception):
    pass

def splitjoin(orig,zoek,vervang):
    """
    dit is een routine waarin de binnenkomende string eerst gesplitst wordt
    in woorden (gescheiden door 1 of meer spaties en/of tabs e.d.);
    tegelijkertijd worden de scheidende strings ook bepaald.
    Daarna worden de woorden die vervangen moeten worden vervangen
    en tenslotte wordt de string weer aan elkaar geplakt.
    De truuk is dat we de scheidende strings intact laten.
    Deze routine zit ook in site-packages\mystuff.py
    """
    heeftreturn = False
    if orig[-1:] == "\n":
        heeftreturn = True
    h = orig.split()
    s = orig.split(h[0]) # eerste woord eraf halen
    sp = [] # list met "split"s
    for w in h[1:]:        ## for tel in range(1,len(h)): # laatste woord hoeft niet
        s = s[1].split(w)      ## s = s[1].split(h[tel])
        sp.append(s[0])
    for i in range(len(h)):
        if h[i] == zoek:
            h[i] = vervang
    news = ""
    for i in enumerate(sp):             ## for i in range(len(sp)):
        news = h[i[0]].join((news,i[1]))    ## news = news + h[i] + sp[i]
    news = news + h[-1]
    if heeftreturn:
        news = news + "\n"
    return news

def test_splitjoin():
    orig = "Hallo, dit  is een       test"
    zoek = "is"
    vervang = "was"
    news = splitjoin(orig,zoek,vervang)
    print(orig)
    print(news)

if __name__ == "__main__":
    ## raise FoundItem
    ## raise DataError
    test_splitjoin()
