from flask import Flask, request
from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from raw_data import users, orders, offers
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String)
    age = db.Column(db.Integer)
    email = db.Column(db.String)
    role = db.Column(db.String)
    phone = db.Column(db.String)
    orders = relationship('Order', foreign_keys='Order.customer_id')

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'email': self.email,
            'role': self.role,
            'phone': self.phone
        }


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)
    address = db.Column(db.String)
    price = db.Column(db.Float)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    executor = relationship('User', foreign_keys=[executor_id])

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'address': self.address,
            'price': self.price,
            'customer_id': self.customer_id,
            'executor_id': self.executor_id
        }


class Offer(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    executor_id = Column(Integer, ForeignKey('users.id'))
    order = relationship('Order')
    executor = relationship('User', backref='offers')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'executor_id': self.executor_id
        }


with app.app_context():
    # db.drop_all()
    db.create_all()

    if not db.session.query(User).first():
        with db.session.begin():
            try:
                for user_data in users:
                    user = User(**user_data)
                    db.session.add(user)

                for order_data in orders:
                    order = Order(**order_data)
                    db.session.add(order)

                for offer_data in offers:
                    offer = Offer(**offer_data)
                    db.session.add(offer)

            except Exception as e:
                print(f'Error: {e}')
    else:
        print('Users table already contains data. Skipping insertion.')


@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        users_list = User.query.all()
        user_response = []
        for user in users_list:
            user_response.append(user.to_dict())
        return json.dumps(user_response), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == "POST":
        user_data = json.loads(request.data)
        new_user = User(
            id=user_data["id"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            age=user_data["age"],
            email=user_data["email"],
            role=user_data["role"],
            phone=user_data["phone"],
        )
        db.session.add(new_user)
        db.session.commit()
        return "", 201


@app.route('/users/<int:sid>', methods=['GET', 'PUT', 'DELETE'])
def get_user(sid: int):
    if request.method == 'GET':
        count = User.query.count()
        user = db.session.get(User, sid)
        if user is None or sid > count:
            return 'user is not found'
        else:
            user_response = user.to_dict()
            return json.dumps(user_response), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'PUT':
        user_data = json.loads(request.data)
        user = db.session.get(User, sid)
        user.first_name = user_data["first_name"]
        user.last_name = user_data["last_name"]
        user.age = user_data["age"]
        user.email = user_data["email"]
        user.role = user_data["role"]
        user.phone = user_data["phone"]
        db.session.add(user)
        db.session.commit()
        return "", 204
    elif request.method == 'DELETE':
        user = db.session.get(User, sid)
        db.session.delete(user)
        db.session.commit()
        return "", 204


@app.route('/orders', methods=['GET', 'POST'])
def get_orders():
    if request.method == 'GET':
        order_list = Order.query.all()
        order_response = []
        for order in order_list:
            order_response.append(order.to_dict())
        return json.dumps(order_response), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == "POST":
        order_data = json.loads(request.data)
        new_order = Order(
            id=order_data["id"],
            name=order_data["name"],
            description=order_data["description"],
            start_date=order_data["start_date"],
            end_date=order_data["end_date"],
            address=order_data["address"],
            price=order_data["price"],
            customer_id=order_data["customer_id"],
            executor_id=order_data["executor_id"],
        )
        db.session.add(new_order)
        db.session.commit()
        return "", 201


@app.route('/orders/<int:sid>', methods=['GET', 'PUT', 'DELETE'])
def get_orders_sid(sid):
    if request.method == 'GET':
        count = Order.query.count()
        order = db.session.get(Order, sid)
        if order is None or sid > count:
            return 'order is not found'
        else:
            order_response = (order.to_dict())
            return json.dumps(order_response), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'PUT':
        order_data = json.loads(request.data)
        order = db.session.get(Order, sid)
        order.name = order_data["name"]
        order.description = order_data["description"]
        order.start_date = order_data["start_date"]
        order.end_date = order_data["end_date"]
        order.address = order_data["address"]
        order.price = order_data["price"]
        order.customer_id = order_data["customer_id"]
        order.executor_id = order_data["executor_id"]
        db.session.add(order)
        db.session.commit()
        return "", 204
    elif request.method == 'DELETE':
        order = db.session.get(Order, sid)
        db.session.delete(order)
        db.session.commit()
        return "", 204


@app.route('/offers', methods=['GET', 'POST'])
def get_offers():
    if request.method == 'GET':
        offer_list = Offer.query.all()
        offer_response = []
        for offer in offer_list:
            offer_response.append(offer.to_dict())
        return json.dumps(offer_response), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == "POST":
        offer_data = json.loads(request.data)
        new_offer = Offer(
            id=offer_data["id"],
            order_id=offer_data["order_id"],
            executor_id=offer_data["executor_id"],
        )
        db.session.add(new_offer)
        db.session.commit()
        return "", 201


@app.route('/offers/<int:sid>', methods=['GET', 'PUT', 'DELETE'])
def get_offers_sid(sid):
    if request.method == 'GET':
        count = Offer.query.count()
        offer = db.session.get(Offer, sid)
        if offer is None or sid > count:
            return 'offer is not found'
        else:
            offer_response = offer.to_dict()
            return json.dumps(offer_response), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'PUT':
        offer_data = json.loads(request.data)
        offer = db.session.get(Offer, sid)
        offer.order_id = offer_data["order_id"]
        offer.executor_id = offer_data["executor_id"]
        db.session.add(offer)
        db.session.commit()
        return "", 204
    elif request.method == 'DELETE':
        offer = db.session.get(Offer, sid)
        db.session.delete(offer)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
