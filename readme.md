# 📊 CSV to SQLite Migrator

---

# 📚 Get Started

```
from db_maker import DBMaker
migrator = DBMaker("data.db", "users", "id INT, name TEXT")

result = migrator.extend(
    csv_path="users.csv",
    from_=["UserID", "FullName"],
    target=["id", "name"],
    batch_size=100
)
print(f"{result['inserted']} rows migrated")
```
---

# ✨ Feuters:

### 🔄 Transactions Automatic rollback on errors
### ⚡ Batch Processing 16-1000 rows per insert
### 📝 Smart Logging Track every migration step
### 🎯 Column Mapping Rename CSV → DB columns freely
### 🔘 Poor Python

---

# 📦 Installation

wget https://github.com/Mikelpy/CSV_to_SQL.git

Requirements: Python 3.8+

---

# 🛡️ Safety

These will raise ValueError:
migrator = DBMaker("db", "users; DROP TABLE", ...)  # ❌ Invalid name
migrator.extend(csv, ["id"], ["id", "extra"])        # ❌ Column mismatch
migrator.extend("missing.csv", ...)                  # ❌ File not found

---

# 📈 Performance Tips

## Faster for large files
migrator.extend(..., batch_size=500)  # ⚡ 500 rows/insert

## Disable logs for speed
migrator = DBMaker(..., log_enabled=False)

---

# 📄 License

## omg  — Free to use, modify, share

---