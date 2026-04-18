import time
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify
import logging
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure trusted hosts for Werkzeug security
app.config['SERVER_NAME'] = None
app.config['PREFERRED_URL_SCHEME'] = 'http'

# Disable Werkzeug host validation for development
os.environ['WERKZEUG_SERVER_NAME'] = ''

# Database connection
DB_HOST = os.environ.get("DB_HOST", "postgres")
DB_NAME = os.environ.get("DB_NAME", "voting_db")
DB_USER = os.environ.get("DB_USER", "voting_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "voting_password")

def get_db_connection():
    """Create a new database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

OPT_A = os.environ.get("OPTION_A", "Option A")
OPT_B = os.environ.get("OPTION_B", "Option B")

@app.route("/vote", methods=["POST"])
def vote():
    time.sleep(0.1) # Simulate load
    
    data = request.json
    tech = data.get("tech")
    
    logger.info(f"Received vote request for: {tech}")
    
    if tech in [OPT_A, OPT_B]:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Use UPSERT to increment vote count
                cur.execute("""
                    INSERT INTO votes (option_name, vote_count)
                    VALUES (%s, 1)
                    ON CONFLICT (option_name)
                    DO UPDATE SET vote_count = votes.vote_count + 1
                """, (tech,))
            conn.commit()
            logger.info(f"Successfully recorded vote for: {tech}")
            return jsonify({"status": "ok", "voted_for": tech})
        except Exception as e:
            conn.rollback()
            logger.error(f"Error recording vote: {str(e)}")
            return jsonify({"error": str(e)}), 500
        finally:
            conn.close()
    
    logger.warning(f"Invalid vote option: {tech}")
    return jsonify({"error": "Invalid option. Allowed: " + OPT_A + ", " + OPT_B}), 400

@app.route("/results", methods=["GET"])
def results():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Use proper parameterized query with tuple
            cur.execute(
                "SELECT option_name, vote_count FROM votes WHERE option_name IN (%s, %s)",
                (OPT_A, OPT_B)
            )
            rows = cur.fetchall()
            
            logger.info(f"Retrieved {len(rows)} vote records")
            
            # Create a dictionary with results
            results = {row['option_name']: row['vote_count'] for row in rows}
            
            # Ensure both options are present in the response
            if OPT_A not in results:
                results[OPT_A] = 0
            if OPT_B not in results:
                results[OPT_B] = 0
            
            logger.info(f"Results: {results}")
            return jsonify(results)
    except Exception as e:
        logger.error(f"Error retrieving results: {str(e)}")
        return jsonify({OPT_A: 0, OPT_B: 0})
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)