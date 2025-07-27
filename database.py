import sqlite3
import os
from datetime import datetime, timedelta
import random
from contextlib import asynccontextmanager
import uuid
import aiosqlite
from typing import Optional, Dict, Any, List

class DatabaseManager:
    def __init__(self, db_path="banking_system.db"):
        self.db_path = db_path
        self.init_database()
        self.populate_demo_data()

    def init_database(self):
        """Initialize database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            monthly_income REAL,
            employment_status TEXT,
            credit_score INTEGER DEFAULT 790,
            date_of_birth TEXT DEFAULT '1990-01-01',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Accounts table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            account_number TEXT UNIQUE NOT NULL,
            account_type TEXT NOT NULL,
            balance REAL DEFAULT 0.0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        """)

        # Cards table with additional blocking fields
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            card_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            account_id TEXT NOT NULL,
            card_number TEXT UNIQUE NOT NULL,
            card_type TEXT NOT NULL,
            card_status TEXT DEFAULT 'active',
            credit_limit REAL DEFAULT 0,
            available_credit REAL DEFAULT 0,
            blocked_at TEXT,
            block_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (account_id) REFERENCES accounts (account_id)
        )
        """)

        # Transactions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            merchant_name TEXT,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'completed',
            FOREIGN KEY (account_id) REFERENCES accounts (account_id)
        )
        """)

        # Loan applications table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS loan_applications (
            application_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            loan_type TEXT NOT NULL,
            loan_amount REAL NOT NULL,
            loan_purpose TEXT,
            application_status TEXT DEFAULT 'pending',
            interest_rate REAL,
            loan_term_months INTEGER,
            monthly_payment REAL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        """)

        # Bill payments table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bill_payments (
            payment_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            bill_type TEXT NOT NULL,
            amount REAL NOT NULL,
            due_date DATE,
            payment_date TIMESTAMP,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        """)

        conn.commit()
        conn.close()
        print("Database initialized successfully")

    def populate_demo_data(self):
        """Populate database with single demo user data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if demo data already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = 'user_demo1'")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return

        # Insert demo user
        cursor.execute("""
        INSERT INTO users (user_id, full_name, email, phone, monthly_income, employment_status, credit_score, date_of_birth)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("user_demo1", "John Smith", "john.smith@email.com", "+1-555-0123", 5500.0, "employed", 790, "1990-01-01"))

        # Insert demo accounts
        cursor.execute("""
        INSERT INTO accounts (account_id, user_id, account_number, account_type, balance, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """, ("acc_001", "user_demo1", "ACC-123456789", "checking", 2500.75, "active"))

        cursor.execute("""
        INSERT INTO accounts (account_id, user_id, account_number, account_type, balance, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """, ("acc_002", "user_demo1", "ACC-987654321", "savings", 15000.00, "active"))

        # Insert demo cards
        cursor.execute("""
        INSERT INTO cards (card_id, user_id, account_id, card_number, card_type, card_status, credit_limit, available_credit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("card_001", "user_demo1", "acc_001", "4532-1234-5678-9012", "debit", "active", 0, 0))

        cursor.execute("""
        INSERT INTO cards (card_id, user_id, account_id, card_number, card_type, card_status, credit_limit, available_credit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("card_002", "user_demo1", "acc_002", "5678-9012-3456-7890", "credit", "active", 10000, 8500))

        cursor.execute("""
        INSERT INTO cards (card_id, user_id, account_id, card_number, card_type, card_status, credit_limit, available_credit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("card_003", "user_demo1", "acc_001", "6789-0123-4567-8901", "credit", "blocked", 5000, 4200))

        # Insert sample transactions
        transactions_data = [
            ("txn_001", "acc_001", "debit", 85.50, "Grocery Store Purchase", "FreshMart Grocery", "2024-01-15 14:30:00"),
            ("txn_002", "acc_001", "debit", 45.20, "Gas Station", "Shell Gas Station", "2024-01-14 09:15:00"),
            ("txn_003", "acc_001", "credit", 2500.00, "Salary Deposit", "ABC Corporation", "2024-01-01 00:01:00"),
            ("txn_004", "acc_002", "debit", 1200.00, "Rent Payment", "Property Management Co", "2024-01-01 08:00:00"),
            ("txn_005", "acc_002", "credit", 500.00, "Transfer from Checking", "Internal Transfer", "2024-01-10 16:45:00"),
        ]

        for txn in transactions_data:
            cursor.execute("""
            INSERT INTO transactions (transaction_id, account_id, transaction_type, amount, description, merchant_name, transaction_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, txn)

        # Insert demo loan applications
        cursor.execute("""
        INSERT INTO loan_applications (application_id, user_id, loan_type, loan_amount, loan_purpose, application_status, interest_rate, loan_term_months, monthly_payment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("loan_001", "user_demo1", "personal", 15000.0, "Home renovation", "approved", 8.5, 36, 475.50))

        conn.commit()
        conn.close()
        print("Demo data populated successfully")

    @asynccontextmanager
    async def get_connection(self):
        """Get async database connection with proper error handling"""
        conn = None
        try:
            conn = await aiosqlite.connect(self.db_path)
            conn.row_factory = aiosqlite.Row
            yield conn
        except Exception as e:
            if conn:
                try:
                    await conn.rollback()
                except:
                    pass
            raise e
        finally:
            if conn:
                await conn.close()

class UserService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

class CardService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def get_user_cards(self, user_id: str) -> List[Dict[str, Any]]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute("""
            SELECT c.*, a.account_number
            FROM cards c
            JOIN accounts a ON c.account_id = a.account_id
            WHERE c.user_id = ?
            ORDER BY c.created_at DESC
            """, (user_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def block_card(self, card_id: str, reason: str = None) -> Dict[str, Any]:
        """Block a card with guaranteed database persistence"""
        try:
            async with self.db.get_connection() as conn:
                # Enable WAL mode for better concurrency
                await conn.execute("PRAGMA journal_mode=WAL")
                
                # Start immediate transaction
                await conn.execute("BEGIN IMMEDIATE")
                
                try:
                    # First verify card exists and get current status
                    cursor = await conn.execute(
                        "SELECT card_id, card_status, card_number FROM cards WHERE card_id = ?", 
                        (card_id,)
                    )
                    result = await cursor.fetchone()
                    
                    if not result:
                        await conn.execute("ROLLBACK")
                        return {"success": False, "error": "Card not found"}
                    
                    current_status = result[1]
                    card_number = result[2]
                    
                    if current_status == 'blocked':
                        await conn.execute("ROLLBACK")
                        return {"success": False, "error": "Card is already blocked"}
                    
                    # Update card status with timestamp
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    await conn.execute("""
                        UPDATE cards 
                        SET card_status = 'blocked', 
                            blocked_at = ?,
                            block_reason = ?,
                            updated_at = ?
                        WHERE card_id = ?
                    """, (timestamp, reason or "User requested block", timestamp, card_id))
                    
                    # Verify the update actually happened
                    cursor = await conn.execute(
                        "SELECT card_status, blocked_at FROM cards WHERE card_id = ?", 
                        (card_id,)
                    )
                    verify_result = await cursor.fetchone()
                    
                    if not verify_result or verify_result[0] != 'blocked':
                        await conn.execute("ROLLBACK")
                        return {"success": False, "error": "Failed to update card status in database"}
                    
                    # Force commit and sync to disk
                    await conn.execute("COMMIT")
                    await conn.execute("PRAGMA synchronous=FULL")
                    
                    # Double-check with fresh query
                    cursor = await conn.execute(
                        "SELECT card_status FROM cards WHERE card_id = ?", 
                        (card_id,)
                    )
                    final_check = await cursor.fetchone()
                    
                    if final_check and final_check[0] == 'blocked':
                        return {
                            "success": True, 
                            "message": f"Card {card_number} has been successfully blocked",
                            "card_id": card_id,
                            "new_status": "blocked",
                            "blocked_at": timestamp
                        }
                    else:
                        return {"success": False, "error": "Card status verification failed after commit"}
                        
                except Exception as inner_e:
                    await conn.execute("ROLLBACK")
                    raise inner_e
                    
        except Exception as e:
            return {"success": False, "error": f"Database error: {str(e)}"}


    async def create_card(self, user_id: str, account_id: str, card_type: str, credit_limit: float = 0) -> str:
        async with self.db.get_connection() as conn:
            card_id = f"card_{uuid.uuid4().hex[:8]}"
            card_number = f"{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}"
            
            await conn.execute("""
            INSERT INTO cards (card_id, user_id, account_id, card_number, card_type, credit_limit, available_credit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (card_id, user_id, account_id, card_number, card_type, credit_limit, credit_limit))
            await conn.commit()
            return card_id

    async def get_card_by_id(self, card_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute("SELECT * FROM cards WHERE card_id = ? AND user_id = ?", (card_id, user_id))
            row = await cursor.fetchone()
            return dict(row) if row else None

class LoanService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def create_loan_application(self, application_data: Dict[str, Any]) -> str:
        async with self.db.get_connection() as conn:
            app_id = f"LOAN-{uuid.uuid4().hex[:8].upper()}"
            await conn.execute("""
            INSERT INTO loan_applications
            (application_id, user_id, loan_type, loan_amount, loan_purpose, application_status)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (app_id, application_data["user_id"], application_data["loan_type"],
                  application_data["loan_amount"], application_data["loan_purpose"], "pending"))
            await conn.commit()
            return app_id

    async def get_user_loan_applications(self, user_id: str) -> List[Dict[str, Any]]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute("""
            SELECT * FROM loan_applications
            WHERE user_id = ?
            ORDER BY applied_at DESC
            """, (user_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def process_loan_approval(self, app_id: str, user_income: float, loan_amount: float) -> Dict[str, Any]:
        debt_ratio = (loan_amount / 12) / user_income if user_income > 0 else 1.0
        
        if debt_ratio <= 0.3 and user_income >= 3000:
            status = "approved"
            interest_rate = 7.5
            term_months = 60
            monthly_payment = (loan_amount * (interest_rate/100/12)) / (1 - (1 + interest_rate/100/12)**(-term_months))
            
            async with self.db.get_connection() as conn:
                await conn.execute("""
                UPDATE loan_applications
                SET application_status = ?, interest_rate = ?, loan_term_months = ?, monthly_payment = ?
                WHERE application_id = ?
                """, (status, interest_rate, term_months, monthly_payment, app_id))
                await conn.commit()
                
            return {
                "status": status,
                "approved_amount": loan_amount,
                "interest_rate": interest_rate,
                "term_months": term_months,
                "monthly_payment": round(monthly_payment, 2)
            }
        else:
            async with self.db.get_connection() as conn:
                await conn.execute("""
                UPDATE loan_applications
                SET application_status = 'declined'
                WHERE application_id = ?
                """, (app_id,))
                await conn.commit()
                
            return {"status": "declined", "reason": "High debt-to-income ratio"}

class AccountService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def get_user_accounts(self, user_id: str) -> List[Dict[str, Any]]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute("SELECT * FROM accounts WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_account_transactions(self, account_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute("""
            SELECT * FROM transactions
            WHERE account_id = ?
            ORDER BY transaction_date DESC
            LIMIT ?
            """, (account_id, limit))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

# Initialize services
db_manager = DatabaseManager()
user_service = UserService(db_manager)
card_service = CardService(db_manager)
loan_service = LoanService(db_manager)
account_service = AccountService(db_manager)
