import sqlite3
import os

DB_DIR = "database"
DB_NAME = "chatbot.db"
DB_PATH = os.path.join(DB_DIR, DB_NAME)

class Database:
    def __init__(self):
        # Create database directory if it doesn't exist
        if not os.path.exists(DB_DIR):
            os.makedirs(DB_DIR)
        
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.migrate_database()

    def create_tables(self):
        # Users Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Chat History Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        # Notes Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                content TEXT,
                category TEXT DEFAULT 'General',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        # To-Do Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                task_text TEXT NOT NULL,
                is_completed BOOLEAN DEFAULT 0,
                priority TEXT DEFAULT 'Medium',
                due_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        self.conn.commit()

    def migrate_database(self):
        # Migrate notes table
        self.cursor.execute("PRAGMA table_info(notes)")
        notes_columns = [col[1] for col in self.cursor.fetchall()]
        if 'category' not in notes_columns:
            self.cursor.execute("ALTER TABLE notes ADD COLUMN category TEXT DEFAULT 'General'")
        if 'updated_at' not in notes_columns:
            self.cursor.execute("ALTER TABLE notes ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            
        # Migrate tasks table
        self.cursor.execute("PRAGMA table_info(tasks)")
        tasks_columns = [col[1] for col in self.cursor.fetchall()]
        if 'priority' not in tasks_columns:
            self.cursor.execute("ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'Medium'")
        if 'due_date' not in tasks_columns:
            self.cursor.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")
        if 'completed_at' not in tasks_columns:
            self.cursor.execute("ALTER TABLE tasks ADD COLUMN completed_at TIMESTAMP")
            
        self.conn.commit()

    # --- User Management ---
    def add_user(self, username, password_hash):
        try:
            self.cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, username):
        self.cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        return self.cursor.fetchone()

    def update_user_password(self, user_id, new_password_hash):
        try:
            self.cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_password_hash, user_id))
            self.conn.commit()
            return True
        except Exception:
            return False

    # --- Chat History ---
    def add_chat_message(self, user_id, sender, message):
        self.cursor.execute('INSERT INTO chat_history (user_id, sender, message) VALUES (?, ?, ?)', (user_id, sender, message))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_chat_history(self, user_id):
        self.cursor.execute('SELECT id, sender, message, timestamp FROM chat_history WHERE user_id = ? ORDER BY id ASC', (user_id,))
        return self.cursor.fetchall()
        
    def clear_chat_history(self, user_id):
        self.cursor.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
        self.conn.commit()

    def delete_chat_message(self, message_id):
        self.cursor.execute('DELETE FROM chat_history WHERE id = ?', (message_id,))
        self.conn.commit()

    # --- Notes Management ---
    def add_note(self, user_id, title, content, category="General"):
        self.cursor.execute('INSERT INTO notes (user_id, title, content, category) VALUES (?, ?, ?, ?)', (user_id, title, content, category))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_notes(self, user_id, search_query=None, category_filter=None):
        query = 'SELECT id, title, content, category, created_at, updated_at FROM notes WHERE user_id = ?'
        params = [user_id]
        
        if category_filter and category_filter != "All":
            query += ' AND category = ?'
            params.append(category_filter)
            
        if search_query:
            query += ' AND (title LIKE ? OR content LIKE ?)'
            params.extend([f'%{search_query}%', f'%{search_query}%'])
            
        query += ' ORDER BY updated_at DESC'
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def update_note(self, note_id, title, content, category="General"):
        self.cursor.execute('''
            UPDATE notes 
            SET title = ?, content = ?, category = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (title, content, category, note_id))
        self.conn.commit()

    def delete_note(self, note_id):
        self.cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        self.conn.commit()

    # --- Task Management ---
    def add_task(self, user_id, task_text, priority="Medium", due_date=None):
        self.cursor.execute('INSERT INTO tasks (user_id, task_text, priority, due_date) VALUES (?, ?, ?, ?)', (user_id, task_text, priority, due_date))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_tasks(self, user_id):
        self.cursor.execute('SELECT id, task_text, is_completed, priority, due_date FROM tasks WHERE user_id = ? ORDER BY is_completed ASC, created_at DESC', (user_id,))
        return self.cursor.fetchall()

    def toggle_task(self, task_id, is_completed):
        completed_at = 'CURRENT_TIMESTAMP' if is_completed else 'NULL'
        self.cursor.execute(f'UPDATE tasks SET is_completed = ?, completed_at = {completed_at} WHERE id = ?', (is_completed, task_id))
        self.conn.commit()

    def delete_task(self, task_id):
        self.cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()

    # --- Analytics & Statistics ---
    def get_user_stats(self, user_id):
        self.cursor.execute('SELECT COUNT(*) FROM chat_history WHERE user_id = ? AND sender = "You"', (user_id,))
        chats_count = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM notes WHERE user_id = ?', (user_id,))
        notes_count = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM tasks WHERE user_id = ?', (user_id,))
        total_tasks = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM tasks WHERE user_id = ? AND is_completed = 1', (user_id,))
        completed_tasks = self.cursor.fetchone()[0]
        
        return {
            "chats_count": chats_count,
            "notes_count": notes_count,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": total_tasks - completed_tasks
        }

    def close(self):
        self.conn.close()

# Initialize global DB instance
db = Database()
