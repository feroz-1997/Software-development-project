from flask import Flask, render_template, request, jsonify
import asyncio # handles multiple requests in a single event loop
import aiohttp # python library that makes multiple HTTP requests, and allows handling a large nr of simultaneous coonections efficiently
#render_template --> used to render HTML templates
#request --> is an object representing the upcoming HTTP requests
#jsonify --> converts a python object into a JSON response


app = Flask(__name__, static_folder='static') #we create a flask application instance 


#assigning values of your Edamam API credentials 
APP_ID = '9a291c98'
APP_KEY = 'a6d2008620692aa8a57bdd6594ef5b8b'
#these two values are crucial for making authenticated requests to the Edamam API



# we define a asynchronous function that helps us fetch recipes based on given ingredients and other filters 
async def fetch_recipe(session, ingredient, num_recipes, meal_type):
   
    base_url = 'https://api.edamam.com/search' #this is the base url for Edamam API

    # Construct the API request parameters
    # create a dictionary containing the params sent with the API request 
    params = {
        'q': ingredient,  # Single ingredient
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'from': 0,  # Start from the first result
        'to': num_recipes,  # Get the specified number of recipes
    }

    if meal_type:
        params['mealType'] = meal_type  # Add meal_type as a parameyter to filter recipes based on meal type

    async with session.get(base_url, params=params) as response: #the response object represents serve's response 
        #HTTP GET request to URL with the params.
        if response.status == 200: #in HTTP a status code of 200 indicates succesful response 
            data = await response.json() #data contains the parsed JSON data retrived from the HTTP response & the wait part ensures that the execution of the fct. is not blocked while waiting for the JSON parsing to complete
            return data #returns the fetched recipe or not if it's unsuccessful
        return None


#define another asynchronous function that orchestrates the current fetching of recipes for a list of ingredients 
async def fetch_recipes(ingredients, num_recipes, meal_type):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session: #creates a contex manager for aiohttp 
        #ClinetSession --> is a class used for managing connections, cookies and providing interface for making HTTP requests
        #TCPConnector --> is used to manage TCP connections for the HTTP client, and for configuring  SSL settings 
        tasks = [fetch_recipe(session, ingredient, num_recipes, meal_type) for ingredient in ingredients] #creates a list of tasks for fetching recipes for each ingredient and uses syncio.gather to concurrently execute those tasks and collect the results 
        results = await asyncio.gather(*tasks) #*arg tasks is used to unpack the list of tasks as separate arguments to 'asyncio.gather'
        return results #returns a list of results, where each result corresponds to the fetched recipes for a specific ingredient


#
def process_recipes(recipes): #takes a list of recipes a parameter

    processed_recipes = [] #here we store the processed recipe data

    for recipe_data in recipes: #we iterate over each element in recipes

        if recipe_data and 'hits' in recipe_data: #we check if recipe data is not empty, to ensure expected structure of the recipe data
            hits = recipe_data['hits'] #hits --> list of search results (each one being a dictionaru containing info about specific recipe )

            for hit in hits: #iterate over each hit aka search result
                recipe = hit['recipe'] # we access the value of the recipe itself from the dictionary 
                label = recipe['label'] # the title of the recipe
                ingredients = recipe.get('ingredientLines', [])  # Handle missing 'ingredientLines' gracefully
                url = recipe.get('url', '')  # Handle missing 'url' gracefully
                processed_recipes.append({
                    'label': label,
                    'ingredients': ingredients,
                    'url': url
                }) #at the end we have a list, each element of the list is a dictionary containing processed information from above

    return processed_recipes #returns the list of processed recipes


#this section is a part of a Flask Web Application that includes routes for rendering an HTML and handling POST requests for searching recipes

#we define a route for root URL 
@app.route('/')
def home():
    return render_template('index.html') # renders index.html template

@app.route('/search-recipes', methods=['POST']) #defining a route for handling POST requests, this is requesting JSON data
def search_recipes():
    data = request.get_json() #retriving JSON data from request payload
    #we extract variables from JSON data to capture user's input when handling POST requests to the endpoint
    ingredients = data.get('ingredients', [])
    num_recipes = data.get('num_recipes', 10)
    meal_type = data.get('meal_type', None)  # If the key is not present it defaults to 'None'

    # Fetch recipes asynchronously
    recipes = asyncio.run(fetch_recipes(ingredients, num_recipes, meal_type))

    # Process the recipes as needed
    processed_recipes = process_recipes(recipes)

    return jsonify({'recipes': processed_recipes}) #retunrs a JSON respons containing the processed data

if __name__ == '__main__':
    app.run(debug=True) #checks if the c=script is being run direclty and starts the Flask Development server 
