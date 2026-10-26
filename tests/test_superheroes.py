import pytest
from app.main import get_tallest_hero
import requests

test_all_combinations_data = [
    ("Male", True, "Utgard-Loki"),
    ("Male", False, "Ymir"),
    ("Female", True, "Giganta"),
    ("Female", False, "Ardina"),
    ("-", True, "Living Brain"),
    ("-", False, "Godzilla")
]

@pytest.mark.parametrize("gender, has_work, expected_name", test_all_combinations_data)
def test_get_tallest_hero_all_combinations(gender, has_work, expected_name):
    hero = get_tallest_hero(gender, has_work)

    assert hero is not None
    assert hero["name"] == expected_name
    assert hero["appearance"]["gender"].lower() == gender.lower()

    if has_work:
        assert hero["work"]["occupation"].strip() != "-"
    else:
        assert hero["work"]["occupation"].strip() == "-"


@pytest.mark.parametrize("variant_of_gender", ["male", "MALE", "Male", "mALE", "  male  "])
def test_gender_case(variant_of_gender):
    hero = get_tallest_hero(variant_of_gender, False)
    assert hero is not None
    assert hero["name"] == "Ymir"

@pytest.mark.parametrize(
    "invalid_gender_value", ["", "   ", "unknown", "alien", "мужской"]
)
def test_invalid_gender_value_raises_error(invalid_gender_value):
    with pytest.raises(ValueError):
        get_tallest_hero(invalid_gender_value, True)

@pytest.mark.parametrize("invalid_gender_type", [None, 123, True, ["Male"], {}])
def test_invalid_gender_type_raises_error(invalid_gender_type):
    with pytest.raises(TypeError):
        get_tallest_hero(invalid_gender_type, True)

@pytest.mark.parametrize(
    "invalid_has_work_type", [None, "True", "False", 1, 0, [True], {}]
)
def test_invalid_has_work_type_raises_error(invalid_has_work_type):
    with pytest.raises(TypeError):
        get_tallest_hero("Male", invalid_has_work_type)

def test_empty_or_invalid_heights_returns_none(monkeypatch):
    fake_heroes = [
        {
            "name": "Zero Height Hero",
            "appearance": {"gender": "Female", "height": ["-", "0 cm"]},
            "work": {"occupation": "Reporter"},
        },
        {
            "name": "Dagger",
            "appearance": {"gender": "Female", "height": ["5'5", "52 kg"]},
            "work": {"occupation": "Vigilante"},
        },
        {
            "name": "Broken Format Hero",
            "appearance": {"gender": "Female", "height": ["-", "-"]},
            "work": {"occupation": "Scientist"},
        },
    ]
    monkeypatch.setattr("app.main.get_all_heroes", lambda: fake_heroes)

    result = get_tallest_hero("Female", True)
    assert result is None


def test_meters_vs_cm_comparison(monkeypatch):
    fake_heroes = [
        {
            "name": "Hero In Cm",
            "appearance": {"gender": "Male", "height": ["6'6", "198 cm"]},
            "work": {"occupation": "-"},
        },
        {
            "name": "Hero In Meters",
            "appearance": {"gender": "Male", "height": ["6'7", "2.0 meters"]},
            "work": {"occupation": "-"},
        },
    ]
    monkeypatch.setattr("app.main.get_all_heroes", lambda: fake_heroes)

    result = get_tallest_hero("Male", False)
    assert result is not None
    assert result["name"] == "Hero In Meters"

def test_empty_list_returns_none(monkeypatch):
    monkeypatch.setattr("app.main.get_all_heroes", lambda: [])

    result = get_tallest_hero("Male", True)
    assert result is None

def test_no_matching_heroes_returns_none(monkeypatch):
    fake_heroes = [
        {
            "name": "Working Male",
            "appearance": {"gender": "Male", "height": ["6'0", "183 cm"]},
            "work": {"occupation": "Engineer"},
        },
        {
            "name": "Unemployed Female",
            "appearance": {"gender": "Female", "height": ["5'7", "170 cm"]},
            "work": {"occupation": "-"},
        },
    ]
    monkeypatch.setattr("app.main.get_all_heroes", lambda: fake_heroes)

    result = get_tallest_hero("Female", True)
    assert result is None

def test_equal_max_height_returns_first_hero(monkeypatch):
    fake_heroes = [
        {
            "name": "Bliznets1",
            "appearance": {"gender": "Male", "height": ["6'2", "188 cm"]},
            "work": {"occupation": "-"},
        },
        {
            "name": "Bliznets2",
            "appearance": {"gender": "Male", "height": ["6'2", "188 cm"]},
            "work": {"occupation": "-"},
        },
    ]
    monkeypatch.setattr("app.main.get_all_heroes", lambda: fake_heroes)

    result = get_tallest_hero("Male", False)
    assert result is not None
    assert result["name"] == "Bliznets1"

def test_height_boundary_values_and_empty_occupation(monkeypatch):
    fake_heroes = [
        {
            "name": "Negative Height Hero",
            "appearance": {"gender": "Male", "height": ["-", "-5 cm"]},
            "work": {"occupation": ""},
        },
        {
            "name": "Zero Height Hero",
            "appearance": {"gender": "Male", "height": ["-", "0 cm"]},
            "work": {"occupation": "   "},
        },
        {
            "name": "Min Valid Height Hero",
            "appearance": {"gender": "Male", "height": ["-", "1 cm"]},
            "work": {"occupation": ""},
        },
    ]
    monkeypatch.setattr("app.main.get_all_heroes", lambda: fake_heroes)

    result = get_tallest_hero("Male", False)
    assert result is not None
    assert result["name"] == "Min Valid Height Hero"


def test_api_error_raises_request_exception(monkeypatch):
    def mock_failed_get(*args, **kwargs):
        raise requests.exceptions.ConnectionError("API недоступно")

    monkeypatch.setattr("app.main.requests.get", mock_failed_get)

    with pytest.raises(requests.exceptions.RequestException):
        get_tallest_hero("Male", True)