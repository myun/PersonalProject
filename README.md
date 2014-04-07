Edibles
===============

Edibles is a personalized recipe recommendation system designed using machine learning techniques. To showcase the recommendation system, when the recommendations are presented to the user, each recipe's thumbnail is scaled according to its predicted rating. Those with higher predicted ratings are larger than those with lower predicted ratings. 

![Example of recipe recommendation page.](static/images/demo/recommendation_page.jpeg)

On the individual recipe pages, users are able to rate, save, and annotate the recipe through a user-friendly interface.

![Example of recipe page.](static/images/demo/recipe.jpeg)

Additional recipes can be accessed through the "Browse Recipes" page. Edibles is written using Python, SQLite, SQLAlchemy, Flask, Jinja, and HTML, CSS and Javascript. One of the most challenging parts of the project, in addition to the recipe recommendation algorithm, was figuring out how to create stars for user rating input and for displaying recipe ratings. This was ultimately accomplished through custom CSS and HTML.  