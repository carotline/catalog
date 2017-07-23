from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Recipe, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Recipe for Appetizer
appetizzer = Category(name="Appetizer")

session.add(appetizzer)
session.commit()

recipe1 = Recipe(user_id=1, name="Lentil and red bell pepper soup", ingredients="-2 red bell peppers, seeded and diced\n-1 onion, chopped\n-2 tablespoons (30 ml) olive oil\n-1/2 teaspoon (2.5 ml) ground turmeric\n-1/4 teaspoon (1 ml) ground cumin seeds\n-1/4 teaspoon (1 ml) ground coriander seeds\n-5 cups (1.25 litres) beef or chicken broth\n-1 cup (250 ml) red lentils, rinsed and drained\n-1 tablespoon (15 ml) tomato paste\n-2 tablespoons (30 ml) chopped cilantro\n-2 green onions, chopped\n-Salt and pepper",preparation="In a large saucepan, soften the bell peppers and onion in the oil. Season with salt and pepper. Add the spices and cook for 1 to 2 minutes. Add the broth, lentils, and tomato paste. Season with salt and pepper. Bring to a boil. Cover and simmer gently for about 20 minutes or until the lentils are cooked. Add broth, if needed. Add the cilantro and green onion. Adjust the seasoning. Serve with whole-grain bread.", image="https://images.ricardocuisine.com/services/recipes/260x351_5214.jpg", category=appetizzer)

session.add(recipe1)
session.commit()




# Recipe for Main Dishes
maindishes = Category(name="Main Dishes")

session.add(maindishes)
session.commit()


recipe1 = Recipe(user_id=1, name="Greek Chicken - Paleo", ingredients="-4 chicken breast halves\n-1/2 olive oil (a cup of)\n-3 cloves chopped garlic\n-1 tablespoon fresh rosemary\n-1 tablespoon chopped fresh thyme\n-1 tablespoon fresh oregano\n-4 lemon (2 juiced, 2 cut in half)", preparation="Pound the chicken until it's uniformly thin. In a glass dish mix olive oil, garlic, rosemary, thyme, oregano and juice of 2 lemons juice. Place the chicken pieces in the mixture and cover. Marinated the chicken for 2 days, or at least overnight. Preheat the grill for high heat. Oil the grill grates well. Cut the remaining 2 lemons in half. Grilled the chicken for 3 1/2 minutes per side. Discard the marinade. Place the 4 lemon halfs fruit side down on the grill and serve with the chicken.", image="http://www.jessyandmelissa.com/wp/wp-content/uploads/Greek-Chicken-Paleo.jpg", category=maindishes)

session.add(recipe1)
session.commit()

recipe2 = Recipe(user_id=1, name="Crock Pot Santa Fe Chicken", ingredients="-24 ounces chicken breasts (1 1/2 lbs)\n-14 2/5 ounces diced tomatoes\n-15 ounces black beans\n-8 ounces frozen corn\n-1/4 cups chopped fresh cilantro\n-14 2/5 ounces fat-free chicken broth\n-3 scallions\n-1 teaspoon garlic powder\n-1 teaspoon onion powder\n-1 teaspoon cumin\n-1 teaspoon cayenne pepper", preparation="Combine chicken broth, beans (drained), corn, tomatoes, cilantro, scallions, garlic powder, onion powder, cumin, cayenne pepper and salt in the crockpot. Season chicken breast with salt and lay on top. Cook on low for 10 hours or on high for 6 hours. Half hour before serving, remove chicken and shred. Return chicken to slow cooker and stir in. Adjust salt and seasoning to taste. Serve over rice or tortillas and with your favorite toppings.", image="https://lh5.ggpht.com/_BizpeaUzxq8/SaS8B-jZQaI/AAAAAAAAA5w/DShsZLVMhNA/s800/crock-pot-santa-fe-chicken.jpg", category=maindishes)

session.add(recipe2)
session.commit()


# Menu for Panda Garden
desert = Category(name="Desert")

session.add(desert)
session.commit()


recipe1 = Recipe(user_id=1, name="No-Bake Cheesecake Bites", ingredients="-8oz cream cheese, room temperature\n-4 tablespoons butter, room temperature\n-1/2 cup crushed graham cracker crumbs\n-4 cups powdered sugar\n-10 oz chocolate chips", preparation="In a large bowl, mix the cream cheese and butter together until combined. Add in the graham cracker crumbs and mix well. Add in the powdered sugar, 1 cup at a time, until it is all mixed in. Cover and chill in the fridge for at least 1 hour. I usually let it sit overnight. Place a piece of wax paper on the counter and remove batter form the fridge. Scoop into balls and roll in between palms if necessary. Place on wax paper. Place in fridge for 10-20 minutes if they are too soft to dip. Melt the chocolate in the microwave, stirring every 15 seconds to make sure it doesn't harden up. It should take about 1 minute for the chocolate to completely melt. Dip balls into chocolate, covering completely.  Place back on wax paper and let cool until chocolate has hardened. Store in the fridge for the best taste.", image="http://www.centercutcook.com/wp-content/uploads/2015/07/no-bake-cheesecake-bites-2.jpg", category=desert)

session.add(recipe1)
session.commit()


print "added menu items!"