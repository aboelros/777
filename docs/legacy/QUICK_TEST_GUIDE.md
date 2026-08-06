# Quick Test Guide - Product & Bot Enhancements

## 🎯 Quick Start Testing

### Step 1: Verify API Fixes (Solve 404 Errors)

**Test the new product endpoint:**
```bash
# Replace with your actual project_id and product_id
curl http://localhost:8000/api/v1/products/{project_id}/{product_id}
```

**Expected:** 200 OK with product details (not 404)

---

### Step 2: Test Bot Product Knowledge

**Send these messages via WhatsApp:**

1. **Test Inventory Check:**
   ```
   "Do you have laptops?"
   ```
   **Expected:** Bot checks inventory and shows available laptops with stock info

2. **Test Low Stock Urgency:**
   ```
   "Show me your bestsellers"
   ```
   **Expected:** Bot highlights low-stock items with urgency messages

3. **Test Out of Stock:**
   ```
   "Do you have [out-of-stock-item]?"
   ```
   **Expected:** Bot apologizes and suggests alternatives

4. **Test Order Creation:**
   ```
   "I want to buy the Premium Headphones"
   ```
   **Expected:** Bot asks for shipping details and creates order

---

### Step 3: Add Test Products

**Via API or Admin Panel, add products with:**

```json
{
  "name": "Premium Wireless Headphones",
  "description": "High-quality noise-canceling headphones",
  "price": 99.99,
  "currency": "USD",
  "stock_quantity": 5,
  "reorder_point": 10,
  "safety_stock": 3,
  "in_stock": true,
  "category": "Electronics"
}
```

**Create 3 scenarios:**
- ✅ **Normal Stock:** stock_quantity = 50
- ⚠️ **Low Stock:** stock_quantity = 5 (below reorder_point)
- ❌ **Out of Stock:** stock_quantity = 0

---

### Step 4: Monitor Bot Behavior

**Watch for these bot features:**

✅ **Stock Awareness:**
- "📦 Stock: 50 units available" (normal)
- "⚠️ Only 5 left - Low stock!" (urgency)
- "Currently out of stock" (with alternatives)

✅ **Sales Tactics:**
- "🔥 Limited quantity available"
- "This is one of our bestsellers!"
- "Hurry! These are selling fast!"

✅ **Professional Presentation:**
```
✨ **Premium Wireless Headphones** - $99.99
📦 Stock: Only 5 left!
🌟 Features: Noise cancellation, 30-hour battery
⚠️ Hurry! These are selling fast!
```

---

## 🔍 Troubleshooting

### Issue: Still getting 404 errors
**Solution:** Restart the backend server
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Issue: Bot doesn't show stock info
**Solution:** Ensure products have stock_quantity set
```sql
UPDATE products SET stock_quantity = 10 WHERE stock_quantity IS NULL;
```

### Issue: Bot doesn't create urgency
**Solution:** Set reorder_point and safety_stock
```sql
UPDATE products SET reorder_point = 10, safety_stock = 5;
```

---

## ✅ Success Checklist

- [ ] No 404 errors on product endpoints
- [ ] Bot checks inventory before responding
- [ ] Bot shows stock quantities
- [ ] Bot creates urgency for low-stock items
- [ ] Bot suggests alternatives for out-of-stock
- [ ] Bot can create orders
- [ ] Bot uses sales tactics (emojis, urgency, social proof)
- [ ] Bot responds in customer's language

---

## 📊 Expected Improvements

**Before:**
- Generic responses
- No stock awareness
- Poor conversion

**After:**
- Detailed product info
- Stock-aware responses
- Urgency tactics
- Higher conversion rates

---

## 🚀 Next Actions

1. ✅ Test all endpoints
2. ✅ Add products with stock info
3. ✅ Test bot conversations
4. ✅ Monitor sales performance
5. ✅ Adjust tactics as needed

---

**Quick Support:** Check `PRODUCT_INVENTORY_ENHANCEMENTS.md` for detailed documentation
