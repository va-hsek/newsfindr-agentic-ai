import sqlite3, os

DB_PATH = "customer.db"
ROWS = [
    (1,  "F8641860-7", "Kevin",  "kevin.f8641860-7@gmail.com",   '["Politics", "Startups", "Travel"]',            "2025-03-26 06:46:15"),
    (2,  "203631A0-B", "Ian",    "ian.203631a0-b@gmail.com",     '["Startups", "Travel"]',                        "2025-03-26 06:46:15"),
    (3,  "D77D96F3-3", "Julia",  "julia.d77d96f3-3@gmail.com",   '["India", "Automobile", "Business"]',           "2025-03-26 06:46:15"),
    (4,  "6EB33C45-5", "Alice",  "alice.6eb33c45-5@gmail.com",   '["Politics", "Technology", "Business"]',        "2025-03-26 06:46:15"),
    (5,  "EDD38E10-6", "Oscar",  "oscar.edd38e10-6@gmail.com",   '["Automobile", "India", "Sports"]',             "2025-03-26 06:46:15"),
    (6,  "4770B814-2", "Hannah", "hannah.4770b814-2@gmail.com",  '["Entertainment", "Business", "Technology"]',   "2025-03-26 06:46:15"),
    (7,  "5483CB53-8", "George", "george.5483cb53-8@gmail.com",  '["India", "Politics", "Science"]',              "2025-03-26 06:46:15"),
    (8,  "FA8FE05B-7", "Lily",   "lily.fa8fe05b-7@gmail.com",    '["India", "Science"]',                          "2025-03-26 06:46:15"),
    (9,  "C63FA237-E", "Nora",   "nora.c63fa237-e@gmail.com",    '["Entertainment", "Business"]',                 "2025-03-26 06:46:15"),
    (10, "45E01919-0", "Lily",   "lily.45e01919-0@gmail.com",    '["India", "India", "Politics"]',                "2025-03-26 06:46:15"),
    (11, "B5A14512-C", "Julia",  "julia.b5a14512-c@gmail.com",   '["India", "Entertainment"]',                    "2025-03-26 06:46:15"),
    (12, "A88FEC03-C", "Emma",   "emma.a88fec03-c@gmail.com",    '["Technology", "Automobile"]',                  "2025-03-26 06:46:15"),
    (13, "AEE37571-7", "Ian",    "ian.aee37571-7@gmail.com",     '["Entertainment", "Automobile", "Startups"]',   "2025-03-26 06:46:15"),
    (14, "CF4D1EDB-9", "Julia",  "julia.cf4d1edb-9@gmail.com",   '["Sports", "Entertainment", "International"]',  "2025-03-26 06:46:15"),
    (15, "D56E53B6-1", "Alice",  "alice.d56e53b6-1@gmail.com",   '["International", "Technology"]',               "2025-03-26 06:46:15"),
]

if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        interests TEXT,
                        last_updated TEXT)""")
    conn.executemany("INSERT INTO customers (id, customer_id, name, email, interests, last_updated)"
                     " VALUES (?,?,?,?,?,?)", ROWS)
    conn.commit()
    conn.close()
    print("customer.db created")
else:
    print("customer.db already exists")
