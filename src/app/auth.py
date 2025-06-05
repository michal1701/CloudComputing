import pyodbc
import bcrypt

def register_user(username, email, password, sql_conn_str):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        conn = pyodbc.connect(sql_conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        """, username, email, hashed_pw)
        conn.commit()
        conn.close()
        return True, "Registration successful."
    except pyodbc.IntegrityError:
        return False, "Username or email already exists."
    except Exception as e:
        return False, f"Error: {e}"


def login_user(username, password, sql_conn_str):
    try:
        conn = pyodbc.connect(sql_conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", username)
        row = cursor.fetchone()
        conn.close()
        if row:
            stored_hash = row[0]
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                return True, "Login successful."
            else:
                return False, "Incorrect password."
        else:
            return False, "Username not found."
    except Exception as e:
        return False, f"Error: {e}"
