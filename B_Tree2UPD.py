"""
Project: B-ChainDB - A Hybrid Blockchain-Database System
-----------------------------------------------------------------------------
 Architecture Overview:
-----------------------------------------------------------------------------
    1. Blockchain (The "Source of Truth"):
       - A chronological, append-only list of blocks.
       - Each block is cryptographically linked to the previous one using SHA-256.
       - Ensures data integrity and provides a verifiable audit trail.

    2. B-Tree (The "Fast Index"):
       - A balanced search tree that does NOT store the full transaction data.
       - It stores pointers in the format: (transaction_id, block_index).
       - This index allows for logarithmic time complexity for search operations.

-----------------------------------------------------------------------------
 Time Complexity Analysis of Implemented Functions:
 (Let 'n' be the total number of transactions and 't' be the B-Tree's degree)
-----------------------------------------------------------------------------
    1. insertTransaction(): O(log n)
       - The dominant cost is traversing the B-Tree to find the correct leaf.

    2. splitBlock() (implemented as split_child): O(t) or O(1)
       - This internal B-Tree operation's runtime depends on the fixed degree 't',
         not the total number of items 'n'. It's considered constant time.

    3. searchTransaction(): O(log n)
       - B-Tree search traverses a path from the root to a leaf, which is
         logarithmic in height.

    4. displayTransactions(): O(n)
       - Requires a full in-order traversal of the B-Tree to visit all 'n'
         transaction pointers.

    5. rangeQuery(): O(n)
       - This implementation is based on a full traversal to collect and then
         filter the items.

    6. get_total_transactions(): O(n)
       - Requires traversing all 'n' pointers in the B-Tree to get a count.

    7. get_average_value(): O(n)
       - Requires visiting all 'n' transactions to sum their values.

    8. get_max_transaction(): O(n)
       - Requires visiting all 'n' transactions to find the maximum value.

    9. get_min_transaction(): O(n)
       - Requires visiting all 'n' transactions to find the minimum value.
       
    10. get_range_sum(): O(n)
        - Relies on rangeQuery, which in this implementation traverses all 'n' items.

    11. validateChain(): O(n)
        - Must iterate through every block in the chronological chain and perform
          a hash calculation.
=============================================================================
"""
import hashlib
import json
from datetime import datetime

# =============================================================================
# COMPONENT 1: THE SECURE BLOCKCHAIN (The Logbook)
# =============================================================================

class Transaction:
    """Represents a single transaction."""
    def __init__(self, tx_id, amount, data=""):
        self.tx_id = tx_id
        self.amount = amount
        self.data = data
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        """Helper function to convert transaction data to a dictionary."""
        return self.__dict__

    def __repr__(self):
        """How the transaction object is printed."""
        return f"Txn(ID={self.tx_id}, Amt={self.amount})"

class Block:
    """Represents a block, which is a container for transactions."""
    def __init__(self, transactions, previous_hash=''):
        self.timestamp = datetime.now().isoformat()
        self.transactions = transactions
        self.previous_hash = previous_hash
        # The block's hash is calculated based on its content
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Calculates a secure SHA-256 hash for the block."""
        # The block's data is converted to a sorted string to get a consistent hash
        block_string = json.dumps({
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    """Manages the list of blocks in chronological order."""
    def __init__(self):
        # The chain starts with a "Genesis Block"
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        """Creates the very first block in the chain."""
        return Block(transactions=[], previous_hash="0")

    def get_latest_block(self):
        """Returns the most recent block in the chain."""
        return self.chain[-1]

    def add_block(self, transactions):
        """Adds a new block to the chain, linking it to the previous one."""
        previous_hash = self.get_latest_block().hash
        new_block = Block(transactions, previous_hash)
        self.chain.append(new_block)
        return len(self.chain) - 1  # Returns the position (index) of the new block

    def validateChain(self):
        """Checks if the blockchain has been tampered with."""
        # Loop from the second block to the end
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Check 1: Does the block's hash match its content?
            if current_block.hash != current_block.calculate_hash():
                return False
            # Check 2: Is the block correctly linked to the previous one?
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

# =============================================================================
# COMPONENT 2: THE B-TREE (The Fast Index)
# =============================================================================

class BTreeNode:
    """A node in the B-Tree. It stores pointers, not the full transaction."""
    def __init__(self, t, leaf=False):
        self.t = t
        self.leaf = leaf
        self.keys = []  # Stores (tx_id, block_index) pointers
        self.children = []

class BTree:
    """The B-Tree class, which manages the index for fast searching."""
    def __init__(self, t):
        self.root = BTreeNode(t, True)
        self.t = t

    def search(self, tx_id, node=None):
        """Finds the pointer for a given transaction ID."""
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and tx_id > node.keys[i][0]:
            i += 1
        if i < len(node.keys) and tx_id == node.keys[i][0]:
            return node.keys[i]  # Return the pointer
        if node.leaf:
            return None
        return self.search(tx_id, node.children[i])
        
    def insert(self, pointer):
        """Inserts a new pointer into the B-Tree."""
        root = self.root
        # If the root is full, the tree grows taller
        if len(root.keys) == (2 * self.t) - 1:
            new_node = BTreeNode(self.t, False)
            new_node.children.insert(0, root)
            self.split_child(new_node, 0)
            self.root = new_node
            self._insert_non_full(new_node, pointer)
        else:
            self._insert_non_full(root, pointer)

    def _insert_non_full(self, node, pointer):
        """Helper function to insert a pointer into a node that is not full."""
        i = len(node.keys) - 1
        tx_id_to_insert = pointer[0]
        if node.leaf:
            node.keys.append(None) # Make space
            while i >= 0 and tx_id_to_insert < node.keys[i][0]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = pointer
        else:
            while i >= 0 and tx_id_to_insert < node.keys[i][0]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == (2 * self.t) - 1:
                self.split_child(node, i)
                if tx_id_to_insert > node.keys[i][0]:
                    i += 1
            self._insert_non_full(node.children[i], pointer)

    # This is your 'splitBlock' function, renamed for clarity
    def split_child(self, parent, i):
        """This is the core logic that keeps the B-Tree balanced."""
        t = self.t
        full_child = parent.children[i]
        new_sibling = BTreeNode(t, full_child.leaf)
        
        # The middle key is promoted up to the parent
        parent.keys.insert(i, full_child.keys[t - 1])
        parent.children.insert(i + 1, new_sibling)
        
        # Keys and children are distributed between the old and new nodes
        new_sibling.keys = full_child.keys[t:]
        full_child.keys = full_child.keys[:t - 1]
        if not full_child.leaf:
            new_sibling.children = full_child.children[t:]
            full_child.children = full_child.children[:t]

    def get_all_pointers(self, node=None):
        """Gets all pointers in sorted order (in-order traversal)."""
        if node is None:
            node = self.root
        pointers = []
        for i in range(len(node.keys)):
            if not node.leaf:
                pointers.extend(self.get_all_pointers(node.children[i]))
            pointers.append(node.keys[i])
        if not node.leaf:
            pointers.extend(self.get_all_pointers(node.children[-1]))
        return pointers

# =============================================================================
# COMPONENT 3: THE MAIN DATABASE (BChainDB)
# =============================================================================

class BChainDB:
    """The main class that combines the Blockchain and B-Tree."""
    def __init__(self, btree_degree=3):
        self.blockchain = Blockchain()
        self.btree = BTree(t=btree_degree)
        self.tx_counter = 0

    def insertTransaction(self, amount, data=""):
        """Creates a transaction, adds it to a block, and indexes it."""
        self.tx_counter += 1
        tx = Transaction(self.tx_counter, amount, data)
        # 1. Add the transaction to the secure, chronological blockchain
        block_index = self.blockchain.add_block([tx])
        # 2. Add a fast pointer to the B-Tree index
        self.btree.insert((tx.tx_id, block_index))
        print(f"✅ Transaction {tx.tx_id} inserted into Block {block_index}.")

    def searchTransaction(self, tx_id):
        """Searches for a transaction using the B-Tree index."""
        # 1. Find the pointer in the fast B-Tree
        pointer = self.btree.search(tx_id)
        if pointer:
            # 2. Use the pointer to get the data from the slow blockchain
            block_index = pointer[1]
            block = self.blockchain.chain[block_index]
            for tx in block.transactions:
                if tx.tx_id == tx_id:
                    return tx
        return None

    def displayTransactions(self):
        """Displays all transactions, sorted by their ID."""
        pointers = self.btree.get_all_pointers()
        transactions = []
        for tx_id, block_index in pointers:
            # Retrieve each transaction using its pointer
            block = self.blockchain.chain[block_index]
            for tx in block.transactions:
                if tx.tx_id == tx_id:
                    transactions.append(tx)
        return transactions

    def rangeQuery(self, start_id, end_id):
        """Finds all transactions within a range of IDs."""
        all_txns = self.displayTransactions()
        return [tx for tx in all_txns if start_id <= tx.tx_id <= end_id]

    # --- Statistical Functions ---
    def get_total_transactions(self): return len(self.btree.get_all_pointers())
    def get_average_value(self):
        txns = self.displayTransactions()
        if not txns: return 0
        return sum(tx.amount for tx in txns) / len(txns)
    def get_min_transaction(self):
        txns = self.displayTransactions()
        return min(txns, key=lambda tx: tx.amount) if txns else None
    def get_max_transaction(self):
        txns = self.displayTransactions()
        return max(txns, key=lambda tx: tx.amount) if txns else None
    def get_range_sum(self, start_id, end_id):
        txns = self.rangeQuery(start_id, end_id)
        return sum(tx.amount for tx in txns)
    def validateChain(self):
        """Calls the blockchain's validation method."""
        return self.blockchain.validateChain()

# =============================================================================
# DEMONSTRATION MENU
# =============================================================================
if __name__ == "__main__":
    # Initialize our database. `t=3` means each node can hold 2 to 5 keys.
    db = BChainDB(btree_degree=3)

    while True:
        print("\n--- B-ChainDB Menu ---")
        print("1. Insert Transaction")
        print("2. Search Transaction by ID")
        print("3. Display All Transactions (Sorted)")
        print("4. Range Query")
        print("5. Transaction Statistics")
        print("6. Validate Blockchain")
        print("7. Exit")
        print("8. (Demo) Tamper with Blockchain")

        try:
            choice = int(input("Enter choice: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if choice == 1:
            try:
                amt = float(input("Enter Amount: "))
                db.insertTransaction(amt)
            except ValueError:
                print("Invalid amount.")
        
        elif choice == 2:
            try:
                tx_id = int(input("Enter Transaction ID to Search: "))
                res = db.searchTransaction(tx_id)
                print("Result:", res if res else "Transaction not found.")
            except ValueError:
                print("Invalid ID.")
        
        elif choice == 3:
            print("--- All Transactions (sorted by ID) ---")
            print(db.displayTransactions())
        
        elif choice == 4:
            try:
                start = int(input("Enter Start ID: "))
                end = int(input("Enter End ID: "))
                print("--- Transactions in Range ---")
                print(db.rangeQuery(start, end))
            except ValueError:
                print("Invalid ID.")
        
        elif choice == 5:
            print("--- Transaction Statistics ---")
            print("Total Transactions:", db.get_total_transactions())
            print("Average Amount:", db.get_average_value())
            print("Min Transaction:", db.get_min_transaction())
            print("Max Transaction:", db.get_max_transaction())
        
            try:
                s = int(input("Enter Range Start ID for Sum: "))
                e = int(input("Enter Range End ID for Sum: "))
                range_sum = db.get_range_sum(s, e)
                print(f"Sum of amounts for transactions [{s}-{e}]: {range_sum}")
            except (ValueError, TypeError):
                 print("Invalid ID for range sum.")

        elif choice == 6:
            print("--- Validating chain... ---")
            is_valid = db.validateChain()
            print("✅ Blockchain Valid:", is_valid)
            
        elif choice == 7:
            break
            
        elif choice == 8:
            if len(db.blockchain.chain) > 1:
                print("\n🔴 TAMPERING with Block 1...")
                # We change data in a past block. This should break the hash chain.
                db.blockchain.chain[1].transactions[0].amount = 99999.99
                print("Block 1 data changed. Run validation (Option 6) to see the effect.")
            else:
                print("Not enough blocks to tamper with. Insert more transactions first.")
        
        else:
            print("Invalid choice!")