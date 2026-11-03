`DWD / DATA WITH DILLON`

# Repeat customers and growth

*Sales review, January to December - 3 November 2026*

Twelve months of sales data show that repeat customers drive most of the growth. This report sets out the data used, the method, and what the results mean for next year.

## 1. Data

The review covers every order placed through the online shop between January and December. Orders are grouped by customer, and a customer counts as **repeat** from their second order on.

- Source: shop order export, one row per order
- Period: 1 January to 31 December
- Excluded: test orders and staff accounts

## 2. Results

Repeat customers placed fewer than half the orders but brought in most of the revenue.

**Table 1. Revenue by customer type**

| Customer type | Orders | Revenue (GBP) | Share of revenue |
| --- | ---: | ---: | ---: |
| Repeat | 4,120 | 312,400 | 64% |
| New | 5,380 | 175,600 | 36% |
| Total | 9,500 | 488,000 | 100% |

> **Key point:** Repeat customers made up 43% of orders and 64% of revenue.

### What customers said

The follow-up survey points the same way.

> I come back because I know what I am getting.
>
> *Survey respondent, March*

## 3. Method

The figures come from one query over the order export.

```sql
SELECT customer_type, COUNT(*) AS orders, SUM(total) AS revenue
FROM orders
WHERE is_test = 0
GROUP BY customer_type;
```

To rerun the review:

1. Export the orders for the period.
2. Load the export into the database.
3. Run [the query above](#3-method) and update Table 1.
