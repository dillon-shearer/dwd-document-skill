`DWD / DATA WITH DILLON`

# Repeat customers and growth

*Sales review, January to December - 3 November 2026*

Twelve months of sales data show that repeat customers drive most of the growth. This report sets out the data used, the method, and what the results mean for next year.

## 1. Data

The review covers every order placed through the online shop between January and December. Orders are grouped by customer, and a customer counts as **repeat** from their second order on. The definition follows *The Loyalty Effect* (Reichheld, 1996).

- Source: shop order export `exports/orders-2026.csv`, one row per order
- Period: 1 January to 31 December
- Excluded: test orders and staff accounts
  - Test orders: flagged in the `is_test` field
  - Staff accounts: matched on the company email domain

> **Note:** All revenue figures are in GBP and exclude refunds issued after 31 December.

## 2. Results

Repeat customers placed fewer than half the orders but brought in most of the revenue.

**Table 1. Revenue by customer type**

| Customer type | Orders | Revenue (GBP) | Share of revenue | Median days between orders |
| --- | ---: | ---: | ---: | ---: |
| Repeat | 4,120 | 312,400 | 64% | 41 |
| New | 5,380 | 175,600 | 36% | n/a |
| Total | 9,500 | 488,000 | 100% | - |

New customers have no second order, so the gap between orders does not apply to them. The median across all customers was not computed.

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

1. Export the orders for the period to `exports/orders-2026.csv`.
2. Load the export into the database with the command below.
3. Run [the query above](#3-method) and update Table 1.

```bash
sqlite3 sales.db ".import --csv exports/orders-2026.csv orders"
```

> **Warning:** A rerun on a part month undercounts repeat customers, because a second order can fall in the next month.

## 4. Sources

- Layout rules for this report: [the Markdown rules](../references/markdown.md)
- Brand skill: [the DWD document skill on GitHub](https://github.com/dillon-shearer/dwd-document-skill)
