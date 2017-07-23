from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Recipe, User

from flask import session as login_session
import random, string

# IMPORTS FOR APP LOGIN
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps

app = Flask(__name__)

# load secret id for facebook from json file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "My Favorite Recipe Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# login page
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

    
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


# facebook api connection
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?'
    url += 'grant_type=fb_exchange_token&client_id=%s&client_secret=%s&'
    url += 'fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    data = json.loads(result)
    token = 'access_token=' + data['access_token']

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)

    if 'email' not in data:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session  
    # in order to properly logout, let's strip out the 
    # information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?'
    url += '%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])

    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


# Disconect from Facebook
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?'
    url += 'access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Connect to Google+ Api
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    login_session['access_token'] = access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px; '
    output += ' -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# Disconnect from Google +
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token'] 
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Recipe Information
@app.route('/myfavoriterecipes/<int:category_id>/recipe/JSON')
def restaurantMenuJSON(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    recipes = session.query(Recipe).filter_by(category_id = category_id).all()
    return jsonify(Recipes=[i.serialize for i in recipes])


@app.route('/myfavoriterecipes/<int:category_id>/recipe/<int:recipe_id>/JSON')
def menuItemJSON(category_id, recipe_id):
    recipe = session.query(Recipe).filter_by(id = recipe_id).one()
    return jsonify(recipe = recipe.serialize)


@app.route('/myfavoriterecipes/JSON')
def restaurantsJSON():
    categories = session.query(Category).all()
    return jsonify(categories= [r.serialize for r in categories])


# Show all categories
@app.route('/')
@app.route('/myfavoriterecipes/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session:
        return render_template('publicmyfavoriterecipes.html', categories = categories)
    else:
        return render_template('myfavoriterecipes.html', categories = categories)

    
# Show all recipes in a category
@app.route('/myfavoriterecipes/<int:category_id>/')
@app.route('/myfavoriterecipes/<int:category_id>/recipe/')
def showRecipes(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    recipes = session.query(Recipe).filter_by(category_id = category_id).all()
    if 'username' not in login_session:
        return render_template('publicrecipes.html', recipes = recipes, 
                               category = category)
    else:
        return render_template('recipes.html', recipes = recipes, 
                               category = category)

    
# Create a new recipe
@app.route('/myfavoriterecipes/<int:category_id>/recipe/new/',methods=['GET','POST'])
@login_required
def newRecipe(category_id):
    if request.method == 'POST':
        newRecipe = Recipe(name = request.form['name'], 
                           ingredients = request.form['ingredients'], 
                           preparation = request.form['preparation'], 
                           image = request.form['image'], 
                           category_id = category_id, 
                           user_id=login_session['user_id'])
        session.add(newRecipe)
        session.commit()
        flash('Recipe %s Successfully Created' % (newRecipe.name))
        return redirect(url_for('showRecipes', category_id = category_id))
    else:
        return render_template('newrecipe.html', category_id = category_id)


# Show recipe
@app.route('/myfavoriterecipes/<int:category_id>/recipe/<int:recipe_id>')
def showRecipe(category_id,recipe_id):
    category = session.query(Category).filter_by(id = category_id).one()
    recipe = session.query(Recipe).filter_by(id = recipe_id).one()
    ingredients_list = recipe.ingredients.split('\n')
    creator = getUserInfo(recipe.user_id)
    if 'username' not in login_session or creator.email != login_session['email']:
        return render_template('publicrecipe.html', recipe = recipe, creator = creator, 
                               category = category, ingredients_list = ingredients_list)
    else:
        return render_template('recipe.html', recipe = recipe, 
                               category = category, creator = creator, 
                               ingredients_list = ingredients_list)


# Edit a recipe
@app.route('/myfavoriterecipes/<int:category_id>/recipe/<int:recipe_id>/edit', methods=['GET','POST'])
@login_required
def editRecipe(category_id, recipe_id):
    recipe = session.query(Recipe).filter_by(id = recipe_id).one()
    creator = getUserInfo(recipe.user_id)
    category = session.query(Category).filter_by(id = category_id).one()
    
    if not recipe:
        flash('This recipe does not exist')
        return redirect(url_for('showCategories'))
    
    if creator.email != login_session['email']:
        flash('Only Owner of recipe can edit  %s' % (recipe.name))
        return redirect(url_for('showRecipes', category_id = category.id))
    
    if request.method == 'POST':
        if request.form['name']:
            recipe.name = request.form['name']
        if request.form['ingredients']:
            recipe.ingredients = request.form['ingredients']
        if request.form['preparation']:
            recipe.preparation = request.form['preparation']
        if request.form['image']:
            recipe.image = request.form['image']
        session.add(recipe)
        session.commit() 
        flash('Recipe Successfully Edited')
        return redirect(url_for('showRecipe', category_id = category.id, recipe_id = recipe.id))
    else:
        return render_template('editrecipe.html', category = category, recipe = recipe)


# Delete a menu item
@app.route('/myfavoriterecipes/<int:category_id>/recipe/<int:recipe_id>/delete', methods = ['GET','POST'])
@login_required
def deleteRecipe(category_id, recipe_id):
    recipe = session.query(Recipe).filter_by(id = recipe_id).one()
    creator = getUserInfo(recipe.user_id)
    
    if not recipe:
        flash('This recipe does not exist')
        return redirect(url_for('showCategories'))
    
    if creator.email != login_session['email']:
        flash('Only Owner of recipe can delete s%' % (recipe.name))
        return redirect(url_for('showRecipes', category_id = category.id))
    
    category = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        session.delete(recipe)
        session.commit()
        flash('Recipe Successfully Deleted')
        return redirect(url_for('showRecipes', category_id = category.id))
    else:
        return render_template('deleteRecipe.html', category = category, recipe = recipe)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
