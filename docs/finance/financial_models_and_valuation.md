# Automind Financial Models & Valuation Methodologies

## 1. Accounting Hierarchy & Financial Statements

Financial calculations adhere to GAAP / IFRS SaaS accounting standards, isolating operational tiers:

```
[Total Gross Revenue] = Subscription Revenue + Usage-Based Overages
       │
       ▼  (minus Cost of Goods Sold / COGS)
[Gross Profit] = Gross Revenue - (AI Tokens + Messaging Tariffs + Payment Fees + Usage Hosting)
       │         Gross Margin % = (Gross Profit / Revenue) * 100
       ▼  (minus Operating Expenses / OPEX)
[Operating Profit (EBIT)] = Gross Profit - (R&D + S&M + G&A Salaries, SaaS & Facilities)
       │
       ├─► [EBITDA] = EBIT + Depreciation & Amortization
       │
       ▼  (minus Corporate Income Taxes on Positive EBIT)
[Net Income (Net Profit)] = EBIT - max(0, EBIT * CorporateTaxRate)
       │         Net Margin % = (Net Income / Revenue) * 100
       ▼
[Free Cash Flow (FCF)] = Net Income + D&A - Capital Expenditures (CapEx)
       │
       ▼
[Ending Cash Balance] = Beginning Cash + FCF
```

---

## 2. Customer Cohort & Growth Dynamics

### 2.1 Saturation Damping & Retention
To prevent unrealistic unbounded exponential growth, monthly customer additions are damped as market penetration increases:
$$\text{Damping Factor} = \max\left(0.10, 1.0 - \frac{\text{Active Customers}}{\text{Target SAM Count}}\right)$$
$$\text{Gross New Customers} = \left\lceil \text{Prior Customers} \times \text{Growth Rate} \times \text{Damping Factor} \right\rceil$$

### 2.2 Annualized Churn & Lifetime Value (LTV)
Customer churn is tracked monthly ($c_m$) and compounded annually ($c_a$):
$$c_a = 1 - (1 - c_m)^{12}$$
$$\text{Customer Lifetime (Months)} = \frac{1}{c_m}$$
$$\text{LTV} = \frac{\text{ARPU} \times \text{Gross Margin %}}{c_m}$$
$$\text{CAC Payback Period (Months)} = \frac{\text{CAC}}{\text{ARPU} \times \text{Gross Margin %}}$$

---

## 3. Five Independent Valuation Methodologies

Automind calculates five distinct, decoupled company valuations without hardcoded blending:

### 3.1 ARR Multiple Valuation
$$\text{EV}_{\text{ARR}} = \text{Forward ARR} \times \text{Multiple}_{\text{ARR}} \quad (\text{Benchmark: 6.0× – 10.0×})$$

### 3.2 Trailing Revenue Multiple Valuation
$$\text{EV}_{\text{Rev}} = \text{Annualized Revenue} \times \text{Multiple}_{\text{Rev}} \quad (\text{Benchmark: 4.0× – 7.0×})$$

### 3.3 EBITDA Multiple Valuation
*Strict Guardrail*: If annualized EBITDA $\le 0$, the EBITDA multiple is mathematically **inapplicable** and reported as \$0.00 / N/A.
$$\text{EV}_{\text{EBITDA}} = \text{EBITDA} \times \text{Multiple}_{\text{EBITDA}} \quad (\text{Benchmark: 12.0× – 20.0× if profitable})$$

### 3.4 Discounted Cash Flow (DCF) Valuation
Evaluates intrinsic value by discounting 5-year Free Cash Flow (FCF) and terminal value:
$$\text{EV}_{\text{DCF}} = \sum_{t=1}^{5} \frac{\text{FCF}_t}{(1 + \text{WACC})^t} + \frac{\text{FCF}_5 \times (1 + g)}{(\text{WACC} - g) \times (1 + \text{WACC})^5}$$
*Constraint*: Perpetual terminal growth rate $g$ must strictly remain $< \text{WACC}$ (default $g = 3.0\%$, $\text{WACC} = 12.0\%$).

### 3.5 Comparable Precedent Transactions (Comps)
Benchmarked against comparable B2B SaaS and conversational AI acquisition transactions (e.g., Gorgias, ManyChat, Zendesk):
$$\text{EV}_{\text{Comps}} = \text{Forward ARR} \times \text{Sector Transaction Multiple} \quad (\text{Benchmark: 5.5× – 8.0×})$$

### 3.6 Enterprise Value vs Equity Value
For each methodology, equity value reflects liquid company reserves:
$$\text{Equity Value} = \text{Enterprise Value} + \text{Cash Balance} - \text{Total Debt}$$
