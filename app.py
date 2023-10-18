from flask import Flask, render_template, request, jsonify
import asyncio
import aiohttp

app = Flask(__name__, static_folder='static')

# Replace with your Edamam API credentials
APP_ID = '9a291c98'
APP_KEY = 'a6d2008620692aa8a57bdd6594ef5b8b'

async def fetch_recipe(session, ingredient, num_recipes, meal_type):
    base_url = 'https://api.edamam.com/search'

    # Construct the API request parameters
    params = {
        'q': ingredient,  # Single ingredient
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'from': 0,  # Start from the first result
        'to': num_recipes,  # Get the specified number of recipes
    }

    if meal_type:
        params['mealType'] = meal_type  # Add meal_type as a filter

    async with session.get(base_url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            return data
        return None

async def fetch_recipes(ingredients, num_recipes, meal_type):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        tasks = [fetch_recipe(session, ingredient, num_recipes, meal_type) for ingredient in ingredients]
        results = await asyncio.gather(*tasks)
        return results

def process_recipes(recipes):
    processed_recipes = []

    for recipe_data in recipes:
        if recipe_data and 'hits' in recipe_data:
            hits = recipe_data['hits']
            for hit in hits:
                recipe = hit['recipe']
                label = recipe['label']
                ingredients = recipe.get('ingredientLines', [])  # Handle missing 'ingredientLines' gracefully
                url = recipe.get('url', '')  # Handle missing 'url' gracefully
                processed_recipes.append({
                    'label': label,
                    'ingredients': ingredients,
                    'url': url
                })

    return processed_recipes

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search-recipes', methods=['POST'])
def search_recipes():
    data = request.get_json()
    ingredients = data.get('ingredients', [])
    num_recipes = data.get('num_recipes', 10)
    meal_type = data.get('meal_type', None)  # Optional meal type

    # Fetch recipes asynchronously
    recipes = asyncio.run(fetch_recipes(ingredients, num_recipes, meal_type))

    # Process the recipes as needed
    processed_recipes = process_recipes(recipes)

    return jsonify({'recipes': processed_recipes})

if __name__ == '__main__':
    app.run(debug=True)
