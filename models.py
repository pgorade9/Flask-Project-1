from app import db,login_manager
from flask_login import UserMixin,AnonymousUserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin,AnonymousUserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(100),nullable=False)
    password = db.Column(db.String(60),nullable=False)
    invoices = db.relationship('Invoice',backref='user',lazy=True)
    def __repr__(self):
        return "User(username={}, email={})".format(self.username,self.email)

class Product(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20),nullable=False)
    img = db.Column(db.String(20),nullable=False)
    price = db.Column(db.Integer,nullable=False)

    def __repr__(self):
        return f'product(name={self.name},img={self.img},price={self.price})'

class Order(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.String,nullable=False)
    name = db.Column(db.String(20),nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    price = db.Column(db.Float,nullable=False)
    total = db.Column(db.Float,nullable=False)
    invoice_id = db.Column(db.Integer,db.ForeignKey('invoice.id'))

    def __repr__(self):
        return f'Order(name={self.name},user={self.user_id},price={self.price},total={self.total},invoice={self.invoice_id})'

class Invoice(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime,nullable=False)
    total = db.Column(db.Float,nullable=False)
    orders = db.relationship('Order',backref='invoice',lazy=True)
    payment_status = db.Column(db.String,nullable=False)
    order_status = db.Column(db.String,nullable=False)

    def __repr__(self):
        return f'Invoice(timestamp={self.timestamp},total={self.total},orders={self.orders},id={self.id})'