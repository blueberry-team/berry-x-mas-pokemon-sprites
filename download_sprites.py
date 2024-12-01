import requests
import os
import time

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
KR_SPRITES_FOLDER = "sprites/kr"
EN_SPRITES_FOLDER = "sprites/en"

# 한글 및 영어 스프라이트 폴더 생성
os.makedirs(KR_SPRITES_FOLDER, exist_ok=True)
os.makedirs(EN_SPRITES_FOLDER, exist_ok=True)

def get_generation_pokemon(generation_id):
    """특정 세대의 포켓몬 데이터를 가져옴."""
    url = f"{POKEAPI_BASE_URL}/generation/{generation_id}/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["pokemon_species"]
    else:
        print(f"Failed to fetch generation {generation_id}: {response.status_code}")
        return []

def get_pokemon_species_data(species_url):
    """포켓몬 종 데이터를 가져옴 (한글 이름 포함)."""
    response = requests.get(species_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch species data: {response.status_code}")
        return None

def get_korean_name(species_data):
    """한글 이름 추출."""
    for name_entry in species_data["names"]:
        if name_entry["language"]["name"] == "ko":
            return name_entry["name"]
    return None

def download_sprite(sprite_folder, pokemon_name, sprite_url):
    """포켓몬 스프라이트를 다운로드."""
    if not sprite_url:
        print(f"Sprite for {pokemon_name} not available.")
        return

    filename = os.path.join(sprite_folder, f"{pokemon_name}.png")
    response = requests.get(sprite_url)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
            print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download {pokemon_name}: {response.status_code}")

def main():
    print("Fetching Pokémon from generations 1 to 3...")
    
    # 1세대, 2세대, 3세대 포켓몬 가져오기
    generations = [1, 2, 3]
    all_pokemon_species = []
    for gen_id in generations:
        all_pokemon_species.extend(get_generation_pokemon(gen_id))

    print(f"Found {len(all_pokemon_species)} Pokémon in generations 1 to 3. Downloading sprites...")
    for species in all_pokemon_species:
        species_url = species["url"]

        # 포켓몬 종 데이터를 가져와 한글 이름 추출
        species_data = get_pokemon_species_data(species_url)
        korean_name = get_korean_name(species_data)

        # 영어 이름
        english_name = species["name"]

        # 스프라이트 URL 가져오기
        pokemon_url = species_url.replace("pokemon-species", "pokemon")
        response = requests.get(pokemon_url)
        if response.status_code == 200:
            pokemon_data = response.json()
            sprite_url = pokemon_data["sprites"]["front_default"]

            # 한글 이름으로 저장
            if korean_name:
                download_sprite(KR_SPRITES_FOLDER, korean_name, sprite_url)
            else:
                print(f"Korean name not found for {english_name}")

            # 영어 이름으로 저장
            download_sprite(EN_SPRITES_FOLDER, english_name, sprite_url)
        else:
            print(f"Failed to fetch data for {english_name}: {response.status_code}")

        # API 호출 속도 제한을 위해 대기
        time.sleep(0.2)

if __name__ == "__main__":
    main()
