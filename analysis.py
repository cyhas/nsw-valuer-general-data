import duckdb

suburb = "Redfern"  # Change this to any suburb name.

# Default query to get the 10 most recent sales in a suburb.
query = f"""
SELECT
    "Property unit number" AS unit_no,
    "Property house number" AS house_no,
    "Property street name"  AS street,
    "Property locality"     AS suburb,
    "Contract date"         AS contract_date,
    "Purchase price"        AS price,
    "Area"                  AS land_area,
    "Zoning"                AS zoning
FROM 'cleaned.csv'
WHERE "Property locality" = '{suburb}'
ORDER BY "Contract date" DESC
LIMIT 10;
"""

df = duckdb.query(query).df()
print(df)

print()

avg_query = f"""
SELECT 
    "Property locality" AS suburb,
    AVG("Purchase price") AS avg_price_12m,
    COUNT(*) AS sales_count
FROM 'cleaned.csv'
WHERE lower("Property locality") = lower('{suburb}')
  AND "Contract date" >= (current_date - INTERVAL 12 MONTH)
GROUP BY "Property locality";
"""

df_avg = duckdb.query(avg_query).df()
print(df_avg)