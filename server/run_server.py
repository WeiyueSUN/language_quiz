from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Question, Child
from flask import send_file
app = Flask(__name__)

engine = create_engine('sqlite:///languageData.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()




@app.route('/child/JSON')
def childJSON():
    children = session.query(Child).all()
    return jsonify(MenuItems=[child.serialize for child in children])

'''
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    Menu_Item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)


@app.route('/restaurant/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants=[r.serialize for r in restaurants])
'''


@app.route("/get", methods=["GET"])
def get_my_ip():
    return jsonify(origin=request.headers.get('X-Forwarded-For', request.remote_addr)), 200

@app.route("/img", methods=["GET"])
def show_img():
    return send_file('/img/dog.jpg', mimetype='image/jpg')

@app.route('/', methods=['GET','POST'])
def showIndex():

    print 'ip: ', request.access_route
    if request.method == 'POST':
        print "post in"
        newchild = Child()
        if request.form.get('is_male'):
            newchild.is_male = 1
        if request.form.get('is_female'):
            newchild.is_female = 1
        if request.form.get('age'):
            newchild.age = request.form.get('age')
        if request.form.get('edu1'):
            newchild.edu1 = 1
        if request.form.get('edu2'):
            newchild.edu2 = 1
        if request.form.get('edu3'):
            newchild.edu3 = 1
        if request.form.get('edu4'):
            newchild.edu4 = 1
        if request.form.get('edu5'):
            newchild.edu5 = 1
        if request.form.get('edu6'):
            newchild.edu6 = 1
        if request.form.get('edu7'):
            newchild.edu7 = 1

        session.add(newchild)
        session.commit()
        print "create a new child, id = ", newchild.id
        return redirect(url_for('wordTest'))

    else:
        return render_template('index.html')



@app.route('/1/1/', methods=['GET', 'POST'])
def wordTest():
    return render_template('wordtest.html')

# Edit a restaurant


@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    editedRestaurant = session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
            return redirect(url_for('showRestaurants'))
    else:
        return render_template(
            'editRestaurant.html', restaurant=editedRestaurant)

    # return 'This page will be for editing restaurant %s' % restaurant_id

# Delete a restaurant


@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurantToDelete = session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurantToDelete)
        session.commit()
        return redirect(
            url_for('showRestaurants', restaurant_id=restaurant_id))
    else:
        return render_template(
            'deleteRestaurant.html', restaurant=restaurantToDelete)
    # return 'This page will be for deleting restaurant %s' % restaurant_id


# Show a restaurant menu
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return render_template('menu.html', items=items, restaurant=restaurant)
    # return 'This page is the menu for restaurant %s' % restaurant_id

# Create a new menu item


@app.route(
    '/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'], description=request.form[
                           'description'], price=request.form['price'], course=request.form['course'], restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()

        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)

    return render_template('newMenuItem.html', restaurant=restaurant)
    # return 'This page is for making a new menu item for restaurant %s'
    # %restaurant_id

# Edit a menu item


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:

        return render_template(
            'editmenuitem.html', restaurant=restaurant_id, menu_id=menu_id, item=editedItem)

    # return 'This page is for editing menu item %s' % menu_id

# Delete a menu item


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item=itemToDelete)
    # return "This page is for deleting menu item %s" % menu_id


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
