from crawler.build_pokedex import bulbapedia_url


def test_bulbapedia_url_for_single_word_species():
    assert bulbapedia_url("pikachu") == "https://bulbapedia.bulbagarden.net/wiki/Pikachu_(Pok%C3%A9mon)"


def test_bulbapedia_url_for_hyphenated_paradox_species():
    # 앞글자만 대문자로 바꾸면 "Great-tusk"가 되어 실제 문서(Great_Tusk)를 못 찾던 버그
    assert bulbapedia_url("great-tusk") == "https://bulbapedia.bulbagarden.net/wiki/Great_Tusk_(Pok%C3%A9mon)"
    assert bulbapedia_url("iron-valiant") == "https://bulbapedia.bulbagarden.net/wiki/Iron_Valiant_(Pok%C3%A9mon)"


def test_bulbapedia_url_for_species_with_a_real_hyphen_in_the_name():
    # 재앙의 네 몸(우행, 파오젠, 딩루, 이유이)은 PokeAPI 슬러그의 하이픈이
    # "단어 구분"이 아니라 영문 이름 자체에 있는 진짜 하이픈이라 밑줄로 바꾸면 안 된다
    assert bulbapedia_url("wo-chien") == "https://bulbapedia.bulbagarden.net/wiki/Wo-Chien_(Pok%C3%A9mon)"
    assert bulbapedia_url("chien-pao") == "https://bulbapedia.bulbagarden.net/wiki/Chien-Pao_(Pok%C3%A9mon)"
    assert bulbapedia_url("ting-lu") == "https://bulbapedia.bulbagarden.net/wiki/Ting-Lu_(Pok%C3%A9mon)"
    assert bulbapedia_url("chi-yu") == "https://bulbapedia.bulbagarden.net/wiki/Chi-Yu_(Pok%C3%A9mon)"
