import duckdb

suburb = "Redfern"  # Change this to any suburb name.

avg_med_twelve_months = f"""
WITH classified AS (
    SELECT
        "Property locality" AS suburb,
        CASE 
            WHEN "Strata lot number" IS NULL OR trim(CAST("Strata lot number" AS VARCHAR)) = '' THEN 'House'
            ELSE 'Unit'
        END AS property_type,
        "Purchase price"
    FROM 'cleaned.csv'
    WHERE lower("Property locality") = lower('{suburb}')
      AND "Contract date" >= (current_date - INTERVAL 12 MONTH)
)
SELECT
    suburb,
    printf('%,.0f', AVG(CASE WHEN property_type = 'House' THEN "Purchase price" END)) AS avg_price_house,
    printf('%,.0f', percentile_cont(0.5) WITHIN GROUP (ORDER BY CASE WHEN property_type = 'House' THEN "Purchase price" END)) AS median_price_house,
    COUNT(CASE WHEN property_type = 'House' THEN 1 END) AS house_sales,
    printf('%,.0f', AVG(CASE WHEN property_type = 'Unit' THEN "Purchase price" END)) AS avg_price_unit,
    printf('%,.0f', percentile_cont(0.5) WITHIN GROUP (ORDER BY CASE WHEN property_type = 'Unit' THEN "Purchase price" END)) AS median_price_unit,
    COUNT(CASE WHEN property_type = 'Unit' THEN 1 END) AS unit_sales
FROM classified
GROUP BY suburb;
"""


q = duckdb.query(avg_med_twelve_months).df()
print(q)
