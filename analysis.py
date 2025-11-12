import duckdb

suburb = "Box Hill"  # Change this to any suburb name.

# Default query to get the 10 most recent sales in a suburb.
query = f"""
SELECT
    "Property unit number" AS unit_no,
    "Property house number" AS house_no,
    "Property street name"  AS street,
    "Property locality"     AS suburb,
    "Contract date"         AS contract_date,
    printf('%,.0f', "Purchase price")  AS price,
    "Area"                  AS land_area,
    "Zoning"                AS zoning
FROM 'cleaned.csv'
WHERE "Property locality" = '{suburb}'
ORDER BY "Contract date" DESC
LIMIT 10;
"""

q = duckdb.query(query)
print(q)

print()

avg_query = f"""
SELECT 
    "Property locality" AS suburb,
    printf('%,.0f', AVG("Purchase price")) AS avg_price_12m,
    COUNT(*) AS sales_count
FROM 'cleaned.csv'
WHERE lower("Property locality") = lower('{suburb}')
  AND "Contract date" >= (current_date - INTERVAL 12 MONTH)
GROUP BY "Property locality";
"""

q = duckdb.query(avg_query)
print(q)
