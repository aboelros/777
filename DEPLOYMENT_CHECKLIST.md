# 🚀 DEPLOYMENT CHECKLIST - Critical Fixes

## ✅ Pre-Deployment

- [x] Fixed Gemini API FunctionDeclaration error
- [x] Fixed product endpoint route ordering
- [x] Enhanced inventory checking system
- [x] Updated sales agent prompt
- [x] Created documentation

## 📋 Deployment Steps

### **1. Restart Backend Service**
```bash
# If using Docker
docker-compose restart backend

# If running locally
# Stop the current process (Ctrl+C)
cd backend
python -m uvicorn app.main:app --reload
```

### **2. Verify Gemini API Fix**
Check logs for this error (should be GONE):
```
❌ OLD: "module 'google.generativeai.types' has no attribute 'FunctionDeclaration'"
✅ NEW: No errors, function calling works
```

### **3. Test Product Endpoints**
```bash
# Test GET single product (should return 200, not 404)
curl http://localhost:8000/api/v1/products/{project_id}/{product_id}

# Test POST create product (should return 200, not 404)
curl -X POST http://localhost:8000/api/v1/products/{project_id} \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Product", "price": 99.99, "stock_quantity": 10}'
```

### **4. Test Bot Function Calling**
Send WhatsApp message:
```
"Do you have laptops?"
```

Expected behavior:
- ✅ Bot calls `check_inventory` function
- ✅ Bot receives product data with stock info
- ✅ Bot responds with detailed product presentation
- ✅ No errors in logs

### **5. Monitor Logs**
Watch for successful operations:
```
✅ "Gemini response generated successfully"
✅ "AI function executed" function=check_inventory
✅ "Product created"
✅ "WhatsApp message sent and saved"
```

## 🧪 Testing Checklist

### **API Tests:**
- [ ] GET /api/v1/products/{project_id} - List products
- [ ] POST /api/v1/products/{project_id} - Create product
- [ ] GET /api/v1/products/{project_id}/{product_id} - Get product
- [ ] PUT /api/v1/products/{project_id}/{product_id} - Update product
- [ ] DELETE /api/v1/products/{project_id}/{product_id} - Delete product
- [ ] POST /api/v1/products/{project_id}/bulk-upload - Bulk upload

### **Bot Tests:**
- [ ] Product inquiry: "Do you have X?"
- [ ] Stock check: "Is X in stock?"
- [ ] Order creation: "I want to buy X"
- [ ] Low stock urgency: Bot creates urgency for low-stock items
- [ ] Out of stock: Bot suggests alternatives

### **Function Calling Tests:**
- [ ] check_inventory works
- [ ] create_order works
- [ ] schedule_followup works
- [ ] No FunctionDeclaration errors

## 📊 Success Criteria

### **Must Have:**
- ✅ No 404 errors on product endpoints
- ✅ No Gemini API errors
- ✅ Bot can check inventory
- ✅ Bot can create orders
- ✅ All CRUD operations work

### **Nice to Have:**
- ✅ Bot creates urgency for low stock
- ✅ Bot suggests alternatives
- ✅ Professional product presentation
- ✅ Multi-language support

## 🔍 Troubleshooting

### **If 404 errors persist:**
1. Check route order in `products.py`
2. Verify more specific routes come first
3. Restart backend service
4. Clear any API gateway cache

### **If Gemini errors persist:**
1. Check `google-generativeai` version
2. Verify API keys are set
3. Check internet connectivity
4. Review error logs

### **If bot doesn't respond:**
1. Check WhatsApp integration status
2. Verify webhook is receiving messages
3. Check Gemini API quota
4. Review bot activity logs

## 📝 Rollback Plan

If issues occur:
```bash
# Revert to previous version
git revert HEAD

# Or restore from backup
git checkout <previous-commit-hash>

# Restart service
docker-compose restart backend
```

## ✅ Post-Deployment

### **Monitor for 24 hours:**
- [ ] Check error logs
- [ ] Monitor API response times
- [ ] Track bot conversation success rate
- [ ] Verify product operations
- [ ] Check customer feedback

### **Performance Metrics:**
- Response time < 2 seconds
- Error rate < 1%
- Bot response rate > 95%
- Customer satisfaction > 4/5

## 🎉 Deployment Complete

Once all tests pass:
- ✅ Update status to "Production Ready"
- ✅ Notify team
- ✅ Document any issues
- ✅ Plan next improvements

---

**Deployment Date:** _____________
**Deployed By:** _____________
**Status:** ⬜ Pending | ⬜ In Progress | ⬜ Complete | ⬜ Rolled Back
