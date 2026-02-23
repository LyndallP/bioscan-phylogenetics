# EPA-ng: Phylogenetic Placement

## 🎯 What is EPA-ng?

**Evolutionary Placement Algorithm - next generation**

Places new sequences onto an existing phylogenetic tree **without rebuilding it**.

---

## 🔧 How It Works
```
     Fixed Reference Tree              New Query Sequences
            (802 tips)                  (347 BIOSCAN + 6 DTOL)
                 │                              │
                 ├──────────────────────────────┤
                 │                              │
                 │    Likelihood Calculation    │
                 │   "Where does this sequence  │
                 │    fit best on the tree?"    │
                 │                              │
                 └──────────────┬───────────────┘
                                │
                         EPA-ng Placement
                      (tests all branches)
                                │
                         Placed Tree + Confidence
                         (LWR scores 0-1)
```

---

## ✅ Why Use EPA-ng Here?

### Problem
Building phylogenetic trees from scratch is **slow** for large datasets
- 1,156 sequences × alignment × tree search = hours/days

### EPA-ng Solution
1. **Reference tree is fixed** (already optimized by Ben)
2. **Queries placed individually** (fast, parallelizable)
3. **Confidence scores provided** (LWR = likelihood weight ratio)
4. **Scalable** (can add thousands of queries quickly)

---

## 📊 Our Results

- **353 query sequences** placed in **1 second**
- **LWR scores**: All placements have confidence 0.5-1.0
- **Modular**: Can add more datasets without re-running everything
- **Quality control**: Short branch lengths (mean pendant ~0.02) indicate good fit

---

## 🔬 Perfect For Our Use Case

✅ High-quality reference tree (Ben's 802-tip Sciaridae)  
✅ Large query dataset (BIOSCAN + DTOL)  
✅ Need confidence metrics (LWR for validation)  
✅ Future extensibility (add more families/datasets)

**EPA-ng = Fast + Reliable + Scalable**
