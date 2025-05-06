from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration
DB_CONFIG = {
    'host': 'diana-db.clyucs4e44b4.ap-northeast-2.rds.amazonaws.com',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def validate_data(data, required_fields):
    """Validate incoming data and handle NULL values"""
    validated = {}
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
        
        # Handle NULL values for numeric fields
        if field in ['price', 'rating', 'discount'] and data[field] is None:
            validated[field] = None
        elif field in ['price', 'discount']:
            try:
                validated[field] = float(data[field])
            except (ValueError, TypeError):
                raise ValueError(f"Invalid value for {field}: must be numeric")
        elif field == 'rating':
            try:
                validated[field] = float(data[field]) if data[field] is not None else None
            except (ValueError, TypeError):
                raise ValueError(f"Invalid value for rating: must be numeric or null")
        else:
            validated[field] = str(data[field]) if data[field] is not None else None
            
    return validated

@app.route('/api/data', methods=['GET'])
def get_all_data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM synthetic_data")
        columns = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        
        # Convert NULL values to None for JSON serialization
        processed_data = []
        for row in data:
            processed_data.append([item if item is not None else None for item in row])
        
        return jsonify({
            'success': True,
            'columns': columns,
            'data': processed_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@app.route('/api/data/category/<category>', methods=['GET'])
def get_data_by_category(category):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM synthetic_data WHERE category = %s", (category,))
        columns = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        
        processed_data = []
        for row in data:
            processed_data.append([item if item is not None else None for item in row])
            
        return jsonify({
            'success': True,
            'columns': columns,
            'data': processed_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@app.route('/api/data', methods=['POST'])
def add_data():
    try:
        data = request.get_json()
        validated_data = validate_data(data, ['category', 'price', 'rating', 'stock', 'discount'])
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Handle NULL values in SQL
        cur.execute(
            """INSERT INTO synthetic_data 
            (category, price, rating, stock, discount) 
            VALUES (%s, %s, %s, %s, %s)""",
            (
                validated_data['category'],
                validated_data['price'],
                validated_data['rating'],
                validated_data['stock'],
                validated_data['discount']
            )
        )
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Data added successfully'
        }), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@app.route('/api/data', methods=['DELETE'])
def delete_data():
    try:
        data = request.get_json()
        validated_data = validate_data(data, ['category', 'price', 'rating', 'stock', 'discount'])
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Handle NULL values in the WHERE clause
        query = """
        DELETE FROM synthetic_data 
        WHERE category = %s
        AND price = %s
        AND (rating IS NULL AND %s IS NULL OR rating = %s)
        AND stock = %s
        AND discount = %s
        """
        
        params = (
            validated_data['category'],
            validated_data['price'],
            validated_data['rating'],
            validated_data['rating'],
            validated_data['stock'],
            validated_data['discount']
        )
        
        cur.execute(query, params)
        conn.commit()
        
        if cur.rowcount == 0:
            return jsonify({
                'success': False,
                'message': 'No matching record found to delete'
            }), 404
            
        return jsonify({
            'success': True,
            'deleted_count': cur.rowcount,
            'message': f'Deleted {cur.rowcount} record(s)'
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
