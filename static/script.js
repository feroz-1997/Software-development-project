document.getElementById('search-button').addEventListener('click', function() {
    const ingredients = document.getElementById('ingredients').value;
    const numRecipes = document.getElementById('num-recipes').value;
    const mealType = document.getElementById('meal-type').value;

    const data = {
        ingredients: ingredients.split(',').map(item => item.trim()),
        num_recipes: numRecipes,
        meal_type: mealType,
    };

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
        if (data.recipes && data.recipes.length > 0) {
            resultDiv.innerHTML = ""; // Clear previous results
            data.recipes.forEach(recipe => {
                const ingredientsList = recipe.ingredients.map(ingredient => `<li>${ingredient}</li>`).join('');
                resultDiv.innerHTML += `
                    <div class="recipe">
                        <h2>"${recipe.label}"</h2>
                        <p>Ingredients:</p>
                        <ul>
                            ${ingredientsList}
                        </ul>
                        <p><a href="${recipe.url}" target="_blank">Link</a></p>
                    </div>
                `;
            });
        } else {
            resultDiv.innerHTML = "No recipes found.";
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Handle the error, e.g., display an error message to the user
    });
});
