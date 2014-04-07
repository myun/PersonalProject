Edibles
===============

Edibles is a personalized recipe recommendation system designed using machine learning techniques. The recommendation algorithm predicts how much the user would like a new recipe based on how much the user has liked each ingredient of the recipe in the past. This ingredient data is gleaned from the user's rating history from prior recipes, and if unavailable, it is assumed that the user has neutral feelings toward the ingredient. Only the top predicted recipes are ultimately shown to the user. 

To showcase the recommendation system, when the recommendations are presented to the user, each recipe's thumbnail is scaled according to its predicted rating. Those with relatively higher predicted ratings are larger than those with relatively lower predicted ratings. 

![Example of recipe recommendation page.](static/images/demo/recommendation_page.jpeg)

On the individual recipe pages, users are able to rate, save, and annotate the recipe through a user-friendly interface. The page includes stars for user rating input and for displaying recipe ratings.

![Example of recipe page.](static/images/demo/recipe.jpeg)

Now, what if a user wants to view more recipes than what is recommended to them? Additional recipes can always be accessed through the "Browse Recipes" page. There, he or she can search through the whole database of recipes.  

Edibles is written using Python, SQLite, SQLAlchemy, Flask, Jinja, and HTML, CSS and Javascript. 