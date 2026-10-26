import requests

BASE_URL = "https://akabab.github.io/superhero-api/api"

GET_ALL_URL = f"{BASE_URL}/all.json"

VALID_GENDERS = {"male", "female", "-"}

def get_all_heroes():
    response = requests.get(GET_ALL_URL, timeout=10)
    response.raise_for_status()
    return response.json()

def get_tallest_hero(gender: str, has_work: bool):
    if type(has_work) is not bool:
        raise TypeError(f"has_work должен быть bool")
        
    if not isinstance(gender, str):
        raise TypeError(f"gender должен быть строкой")

    gender=gender.strip().lower()
    if gender not in VALID_GENDERS:
        raise ValueError(f"Невалидный gender: '{gender}'. Допустимые: {VALID_GENDERS}")

    data = get_all_heroes()

    tallest_hero = None
    max_height = 0.0

    for hero in data:
        occupation = hero["work"]["occupation"].strip()
        hero_has_work = occupation != "-" and occupation != ""
        hero_gender = hero['appearance']['gender'].strip().lower()

        if  hero_gender == gender and hero_has_work==has_work:
            height_parts = hero["appearance"]["height"][1].split(" ")
            if len(height_parts) != 2:
                continue

            try:
                height = float(height_parts[0])
            except ValueError:
                continue
            type_of_measurements = str(height_parts[1])
            
            if type_of_measurements == 'meters':
                height *= 100
            elif type_of_measurements != 'cm':
                continue
                
            if max_height < height:
                max_height = height
                tallest_hero = hero

    return tallest_hero

if __name__ == "__main__":
    print(f'Самый высокий герой: {get_tallest_hero(gender="-", has_work=False)}')
