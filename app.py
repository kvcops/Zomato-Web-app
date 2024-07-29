from flask import Flask, jsonify, render_template, request
import sqlite3
import csv

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def load_country_codes(filename='Country_code.csv'):
    country_codes = {}
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            country_codes[row['Country Code']] = row['Country']
    return country_codes

@app.route('/api/restaurant/<int:id>')
def get_restaurant(id):
    conn = get_db_connection()
    restaurant = conn.execute('SELECT * FROM restaurants WHERE id = ?', (id,)).fetchone()
    conn.close()
    if restaurant is None:
        return jsonify({"error": "Restaurant not found"}), 404
    return jsonify(dict(restaurant))

@app.route('/api/restaurants')
def get_restaurants():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    conn = get_db_connection()
    offset = (page - 1) * per_page
    restaurants = conn.execute('SELECT * FROM restaurants LIMIT ? OFFSET ?', 
                               (per_page, offset)).fetchall()
    total = conn.execute('SELECT COUNT(*) FROM restaurants').fetchone()[0]
    conn.close()
    return jsonify({
        "restaurants": [dict(r) for r in restaurants],
        "total": total,
        "page": page,
        "per_page": per_page
    })

@app.route('/')
def restaurant_list():
    conn = get_db_connection()
    country_codes = load_country_codes()

    country = request.args.get('country', '')
    min_cost = request.args.get('min_cost', type=float)
    max_cost = request.args.get('max_cost', type=float)
    cuisines = request.args.get('cuisines', '')
    search = request.args.get('search', '')

    query = 'SELECT * FROM restaurants WHERE 1=1'
    params = []

    if country:
        query += ' AND country_code = ?'
        params.append(country)
    if min_cost is not None:
        query += ' AND average_cost_for_two >= ?'
        params.append(min_cost)
    if max_cost is not None:
        query += ' AND average_cost_for_two <= ?'
        params.append(max_cost)
    if cuisines:
        query += ' AND cuisines LIKE ?'
        params.append(f'%{cuisines}%')
    if search:
        query += ' AND (name LIKE ? OR cuisines LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])

    page = request.args.get('page', 1, type=int)
    per_page = 12
    offset = (page - 1) * per_page
    query += ' LIMIT ? OFFSET ?'
    params.extend([per_page, offset])

    restaurants = conn.execute(query, params).fetchall()

    count_query = f'SELECT COUNT(*) FROM ({query.replace("LIMIT ? OFFSET ?", "")})'
    total = conn.execute(count_query, params[:-2]).fetchone()[0]

    all_cuisines = set()
    for row in conn.execute('SELECT cuisines FROM restaurants'):
        all_cuisines.update(cuisine.strip() for cuisine in row[0].split(','))

    conn.close()

    return render_template('restaurant_list.html', 
                           restaurants=restaurants, 
                           page=page, 
                           per_page=per_page, 
                           total=total,
                           countries=sorted(country_codes.items()), 
                           cuisines=sorted(all_cuisines),
                           current_filters={
                               'country': country,
                               'min_cost': min_cost,
                               'max_cost': max_cost,
                               'cuisines': cuisines,
                               'search': search
                           })

@app.route('/restaurant/<int:id>')
def restaurant_detail(id):
    conn = get_db_connection()
    restaurant = conn.execute('SELECT * FROM restaurants WHERE id = ?', (id,)).fetchone()
    conn.close()
    if restaurant is None:
        return "Restaurant not found", 404
    return render_template('restaurant_detail.html', restaurant=restaurant)

if __name__ == '__main__':
    app.run(debug=True)