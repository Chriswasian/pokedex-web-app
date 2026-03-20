from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

def build_chain(chain, indent=0):
    name = chain['species']['name'].capitalize()
    details = chain.get('evolution_details', [])
    detail = details[0] if details else {}
    level = detail.get('min_level')
    item = detail.get('item')
    happiness = detail.get('min_happiness')
    trigger = (detail.get('trigger') or {}).get('name', '')
    location = detail.get('location')
    move_type = detail.get('known_move_type')
    time_of_day = detail.get('time_of_day', '')
    condition = ""
    if level:
        condition = f" (level {level})"
    elif item:
        condition = f" ({item['name'].replace('-', ' ').title()})"
    elif happiness and time_of_day == 'day':
        condition = " (happiness, day)"
    elif happiness and time_of_day == 'night':
        condition = " (happiness, night)"
    elif happiness:
        condition = " (happiness)"
    elif trigger == 'trade':
        condition = " (trade)"
    elif location:
        condition = f" (level up near {location['name'].replace('-', ' ').title()})"
    elif move_type:
        condition = f" (know {move_type['name']} move)"
    result = " " * indent + "→ " + name + condition + "\n"
    for evo in chain.get('evolves_to', []):
        result += build_chain(evo, indent + 1)
    return result

@app.route('/')
def index():
        return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return redirect('/')
    pokemon_name = request.form.get('pokemon_name')
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        species_url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_name.lower()}"
        species_response = requests.get(species_url)
        species_data = species_response.json()
        evo_url = species_data['evolution_chain']['url']
        evo_response = requests.get(evo_url)
        evo_data = evo_response.json()
        evolution_chain = build_chain(evo_data['chain'])
        encounters_url = f"https://pokeapi.co/api/v2/pokemon/{data['id']}/encounters"
        encounters_response = requests.get(encounters_url)
        encounters_data = encounters_response.json()
        locations = []
        for loc in encounters_data:
            area = loc['location_area']['name'].replace('-', ' ').title()
            games = []
            for v in loc['version_details']:
                games.append(v['version']['name'].replace('-', ' ').title())
            locations.append({'area': area, 'games': ', '.join(games)})
        flavor_text = ""
        for entry in species_data['flavor_text_entries']:
                if entry['language']['name'] == 'en':
                    flavor_text = entry['flavor_text'] 
                break
        return render_template('result.html', pokemon=data, species=species_data, flavor_text=flavor_text, evolution_chain=evolution_chain, encounters=encounters_data, locations=locations)
    else:
        return render_template('index.html', error="Pokémon not found!")
    
if __name__ == '__main__':
    app.run(debug=True)
    

          
    

    

