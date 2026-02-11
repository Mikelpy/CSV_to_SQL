# 📊 CSV to SQL migration

---

## 📚 Usage

### install CSV files and expand the SQL database using them one by one.

---

## 📚 Get Started

```
migrate = CSVMigration("data.db", "users", "id INT, name TEXT")

result = migrate.extend(
    csv_path="users.csv",
    from_=["UserID", "FullName"],
    target=["id", "name"],
    batch_size=100
)
print(f"{result['inserted']} rows migrated")
```
---

## ✨ Features:

###  Transactions Automatic rollback on errors
###  Batch Processing 16-1000 rows per insert

---

## 📦 Installation

wget https://raw.githubusercontent.com/Mikelpy/CSV_to_SQL/main/src/csv_migrator.py

Requirements: Python 3.8+

---

## Enable log

    migrator = CSVMigrator(..., log_enabled=False)

---

## 📄 License

###  - Free to use, modify, share

---