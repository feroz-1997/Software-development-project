// Event listener for the "Search" button
document.getElementById('search-button').addEventListener('click', function() {
    const ingredients = document.getElementById('ingredients').value;
    const numRecipes = document.getElementById('num-recipes').value;
    const mealType = document.getElementById('meal-type').value;

    // Prepare data for the POST request
    const data = {
        ingredients: ingredients,
        num_recipes: numRecipes,
        meal_type: mealType,
    };

    // Make a POST request to the Flask route
    fetch('/search-recipes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = ''; // Clear any previous results

        if (data.recipes.length === 0) {
            resultDiv.textContent = "No recipes found.";
        } else {
            data.recipes.forEach(recipe => {
                const recipeDiv = document.createElement('div');
                recipeDiv.classList.add('recipe');

                const h2 = document.createElement('h2');
                h2.textContent = recipe.label;

                const ingredientsP = document.createElement('p');
                ingredientsP.textContent = 'Ingredients: ' + recipe.ingredients;

                const linkP = document.createElement('p');
                const linkA = document.createElement('a');
                linkA.textContent = 'Link';
                linkA.href = recipe.url;
                linkA.target = '_blank';
                linkP.appendChild(linkA);

                recipeDiv.appendChild(h2);
                recipeDiv.appendChild(ingredientsP);
                recipeDiv.appendChild(linkP);

                resultDiv.appendChild(recipeDiv);
            });
        }
    });
});
