# 🧩 Sudoku CSP Solver (AC-3 + Backtracking + MRV)

## 📌 Overview

This project implements a Sudoku solver based on Constraint Satisfaction Problem (CSP) techniques. It combines constraint propagation and search methods to efficiently solve 9×9 Sudoku puzzles of varying difficulty.

The solver integrates:

-   **AC-3 (Arc Consistency Algorithm #3)** for domain reduction
    
-   **Forward Checking** for dynamic constraint pruning
    
-   **Backtracking Search** for completeness
    
-   **MRV (Minimum Remaining Values)** heuristic for efficient variable selection
    

---

## ⚙️ Features

-   Automatic puzzle solving using CSP techniques
    
-   Step-by-step constraint propagation (AC-3)
    
-   Performance metrics tracking
    
-   Forward checking during recursion
    
-   MRV heuristic for optimized backtracking
    
-   Supports easy, medium, and hard Sudoku puzzles
    
-   Random puzzle generator (optional)
    

---

## 🚀 How It Works

1.  **Initial Setup**
    
    -   Each cell is treated as a variable
        
    -   Domains initialized to {1–9}
        
2.  **AC-3 Phase**
    
    -   Removes inconsistent values
        
    -   Enforces arc consistency across rows, columns, and subgrids
        
3.  **Forward Checking**
    
    -   Prunes invalid values after each assignment during search
        
4.  **MRV Heuristic**
    
    -   Selects the cell with the smallest remaining domain first
        
5.  **Backtracking Search**
    
    -   Recursively fills remaining cells until a solution is found
        

---

## 📊 Metrics Collected

-   Arc consistency checks
    
-   Domain reductions
    
-   Queue push/pop operations
    
-   Backtracking calls
    
-   Execution time (AC-3 and BT separately)
    

---

## 📂 Project Structure

-   `board.py` → Core Sudoku CSP implementation
    
-   `AC3.py` → AC-3 + instrumentation logic
    
-   `tester.py` → Runs performance tests on puzzles
    
-   `GUI.py` → (optional) visual solver interface
    

---

## ▶️ Running the Solver

```
Bash

```
python tester.py
```
```

or run the GUI version:

```
Bash

```
python GUI.py
```
```

---

## 📈 Notes

-   AC-3 performs well on easy/medium puzzles but is insufficient alone for hard puzzles.
    
-   MRV and Forward Checking significantly reduce backtracking complexity.
    
-   The solver demonstrates a full CSP hybrid approach commonly used in AI problem solving.
    

---

## 📚 Concepts Used

-   Constraint Satisfaction Problems (CSP)
    
-   Arc Consistency (AC-3)
    
-   Backtracking Search
    
-   Forward Checking
    
-   Heuristic Search (MRV)
