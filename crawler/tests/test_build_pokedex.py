from crawler.build_pokedex import bulbapedia_url


def test_bulbapedia_url_for_single_word_species():
    assert bulbapedia_url("pikachu") == "https://bulbapedia.bulbagarden.net/wiki/Pikachu_(Pok%C3%A9mon)"


def test_bulbapedia_url_for_hyphenated_paradox_species():
    # 앞글자만 대문자로 바꾸면 "Great-tusk"가 되어 실제 문서(Great_Tusk)를 못 찾던 버그
    assert bulbapedia_url("great-tusk") == "https://bulbapedia.bulbagarden.net/wiki/Great_Tusk_(Pok%C3%A9mon)"
    assert bulbapedia_url("iron-valiant") == "https://bulbapedia.bulbagarden.net/wiki/Iron_Valiant_(Pok%C3%A9mon)"
