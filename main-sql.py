import random
import settings
import json

from flask import Flask, render_template, abort, redirect, request, jsonify

app = Flask(__name__)
app.config.from_object(settings)

from flask.ext.sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/littlecalc.db'
app.config['S3_ENDPOINT'] = '/load'
app.config['DEBUG'] = True
db = SQLAlchemy(app)

class Sheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(16), unique=True)
    contents = db.Column(db.Text)

    def __init__(self, key):
        self.key = key

    def __repr__(self):
        return '<Key %r>' % self.key

@app.route('/api/sheets/<sheet_id>', methods=['PUT'])
def save_sheet(sheet_id):
    data = request.get_json()
    if len(data['cells']) > 99 or len(data['cells'][0]) > 20:
        abort(406)

    sheet = {
        'cells': data['cells']
    }

    instance = Sheet.query.filter_by(key=sheet_id).first()
    if instance is None:
        instance = Sheet(sheet_id)

    instance.contents = json.dumps(sheet)
    db.session.add(instance)
    db.session.commit()

    return 'ok'

@app.route('/load/<sheet_id>.json', methods=['GET'])
@app.route('/api/sheets/<sheet_id>', methods=['GET'])
def load_sheet(sheet_id):
    instance = Sheet.query.filter_by(key=sheet_id).first()
    if instance is None: return ""
    jdata = json.loads(instance.contents)
    return jsonify(jdata)

@app.route('/<sheet_id>')
def edit_sheet(sheet_id):
    return render_template('index.html', sheet_id=sheet_id)

@app.route('/')
def index():
    charset = 'zaqxswyawcdevfrkbgtenhaymuiujkilop'
    random_id = ''.join(random.choice(charset) for _ in range(8))
    return redirect('/' + random_id)

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0')
