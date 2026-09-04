import sqlite3
import datetime

conn = sqlite3.connect('dispute_sentinel.db')
c = conn.cursor()

now = datetime.datetime.utcnow().isoformat()

# Update existing
c.execute("UPDATE disputes SET status = 'NEEDS_REVIEW' WHERE id = 'disp_StagingFixt001'")

# Insert some mock ones
disputes = [
    ("disp_Ok98xYt2Rn41Qa", "pay_test1", "order_test1", 4599900, "INR", "chargeback_fraud", "NEEDS_REVIEW", 68, "MANUAL", now, now),
    ("disp_Pq11zLm8Vt02Bd", "pay_test2", "order_test2", 1289900, "INR", "product_not_delivered", "CONTESTED", 91, "AUTO_CONTEST", now, now),
    ("disp_Wq58mAe4Jr93Tn", "pay_test3", "order_test3", 349900, "INR", "product_not_as_described", "NEEDS_REVIEW", 52, "MANUAL", now, now)
]

for d in disputes:
    try:
        c.execute("""
            INSERT INTO disputes (id, payment_id, order_id, amount, currency, reason_code, status, win_probability, decision_route, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, d)
    except sqlite3.IntegrityError:
        pass

conn.commit()
print("Database seeded successfully!")
