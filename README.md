# 🚀 B-ChainDB: Blockchain Indexing with B-Trees

## 📌 Overview

**B-ChainDB** is a hybrid blockchain–database system designed to solve the **“Speed vs Trust”** problem in modern data systems.

It integrates:

* 🔐 **Blockchain** for secure, tamper-proof data storage
* ⚡ **B-Tree Indexing** for fast and efficient transaction search

This design achieves **O(log n) search performance** while maintaining strong data integrity.

---

## 🎯 Problem Statement

Traditional systems face a trade-off:

* **Databases** → fast but centralized and less secure
* **Blockchain** → secure but inefficient for searching (O(n))

👉 **B-ChainDB bridges this gap** by combining both approaches.

---

## 🏗️ System Architecture

### 🔹 Blockchain (Source of Truth)

* Stores transactions chronologically
* Uses **SHA-256 hashing**
* Ensures immutability and tamper detection

### 🔹 B-Tree (Fast Index)

* Stores pointers *(transaction_id, block_index)*
* Maintains sorted structure
* Enables **O(log n) search**

---

## ⚙️ Core Operations

### 🔸 Insert Transaction

* Adds transaction to blockchain
* Updates B-Tree index

### 🔸 Search Transaction

* Searches via B-Tree
* Retrieves data from blockchain

### 🔸 Validate Blockchain

* Verifies hash integrity
* Detects tampering

---

## ✨ Features

* Fast transaction lookup (**O(log n)**)
* Secure blockchain storage (SHA-256)
* Range queries
* Transaction statistics (min, max, average, sum)
* Tamper detection mechanism
* Modular and scalable design

---

## 📊 Complexity Analysis

| Operation            | Time Complexity |
| -------------------- | --------------- |
| Insert Transaction   | O(log n)        |
| Search Transaction   | O(log n)        |
| Display Transactions | O(n)            |
| Range Query          | O(n)            |
| Validation           | O(n)            |

---

## 🧩 Project Structure

* `Transaction` → Transaction data model
* `Block` → Stores transactions with hashing
* `Blockchain` → Maintains integrity and chain
* `BTree` → Handles indexing and search
* `BChainDB` → Core system integration

---

## 💻 Technologies Used

* Python
* Data Structures (B-Tree)
* Blockchain Concepts
* SHA-256 Hashing

---

## ▶️ How to Run

```bash
python main.py
```

---

## 🔍 Applications

* Financial systems
* Supply chain tracking
* Auditing and verification systems
* Secure data management

---

## 🛡️ Key Highlight

**Achieves fast O(log n) search on blockchain data using B-Tree indexing while preserving full data integrity.**

---

## 📌 Conclusion

B-ChainDB demonstrates how combining blockchain with efficient data structures can deliver both **high performance and strong security**, making it suitable for real-world applications.
