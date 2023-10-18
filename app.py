from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Replace with your Edamam API credentials
APP_ID = '9a291c98'
APP_KEY = 'a6d2008620692aa8a57bdd6594ef5b8b'

def get_recipes(ingredients, num_recipes, meal_type):
    base_url = 'https://api.edamam.com/search'
    
    # Construct the API request parameters
    params = {
        'q': ','.join(ingredients),  # Comma-separated list of ingredients
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'from': 0,  # Start from the first result
        'to': num_recipes,  # Get the specified number of recipes
    }

    # Add meal_type as a filter if specified
    if meal_type:
        params['mealType'] = meal_type

    try:
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()

            if 'hits' in data:
                recipes = data['hits']
                recipe_info = ""
                for i, recipe in enumerate(recipes):
                    recipe_data = recipe['recipe']
                    recipe_info += f"Recipe {i + 1}: {recipe_data['label']}\n"
                    recipe_info += f"Ingredients: {', '.join(recipe_data['ingredientLines'])}\n"
                    recipe_info += f"Link: {recipe_data['url']}\n\n"

                return recipe_info
            else:
                return "No recipes found."

        else:
            return f"Failed to retrieve recipes. Status code: {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def home():
    # You can pass data to the template, e.g., recipes
    recipes = [{'label': 'Recipe 1', 'ingredients': 'Ingredient 1, Ingredient 2', 'url': 'https://example.com/recipe1'},
               {'label': 'Recipe 2', 'ingredients': 'Ingredient A, Ingredient B', 'url': 'https://example.com/recipe2'}]

    return render_template('index.html', recipes=recipes)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search-recipes', methods=['POST'])
def search_recipes():
    data = request.get_json()
    ingredients = data.get('ingredients', [])
    num_recipes = data.get('num_recipes', 10)
    meal_type = data.get('meal_type', None)  # Optional meal type

    result = get_recipes(ingredients, num_recipes, meal_type)
    return jsonify({'recipes': result})

if __name__ == '__main__':
    app.run(debug=True)
