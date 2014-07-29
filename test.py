from historical_relevance import HistoricalRelevance

relevance = HistoricalRelevance()

# American Civil War
def test_1():
    #relevance.summarize('American Civil War')
    relevance.plot_keywords('American Civil War', ['McPherson', 'McClellan', 'secessionists', 'McDowell', 'Chattanooga'], [1850, 1880])
    relevance.plot_all_methods('McPherson', [1840, 1900], 2)
    relevance.plot_all_methods('McClellan', [1840, 1900], 2)

# World War II
def test_2():
    #relevance.summarize('World War II')
    relevance.plot_keywords('World War II', ['Yenangyaung', 'Karelian', 'Gona', 'Narvik', 'Alamein'], [1930, 1960])
    relevance.plot_all_methods('Yenangyaung', [1920, 1970], 2)
    relevance.plot_all_methods('Karelian', [1920, 1970], 2)

# World War I
def test_3():
    relevance.summarize('World War I')
    relevance.plot_keywords('World War I', ['Caporetto', 'Allenby', 'Scapa', 'Clemenceau', 'Belgian'], [1910, 1940])
    relevance.plot_all_methods('Caporetto', [1910, 1940], 2)
    relevance.plot_all_methods('Allenby', [1910, 1940], 2)

# Korean War
def test_4():
    #relevance.summarize('Korean War')
    relevance.plot_keywords('Korean War', ['Malenkov', 'rotorcraft', 'NPA', 'USAMGIK', 'Munsan'], [1940, 1960])
    relevance.plot_all_methods('Malenkov', [1930, 1970], 2)
    relevance.plot_all_methods('rotorcraft', [1930, 1970], 2)

if __name__ == "__main__":
    test_1()
    test_2()
    test_3()
    test_4()