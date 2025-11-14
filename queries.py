avg_med_twelve_months = """
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

median_avg_growth_periods = """
WITH base AS (
    SELECT
        "Contract date" AS contract_date,
        "Purchase price",
        CASE 
            WHEN "Strata lot number" IS NULL 
                 OR trim(CAST("Strata lot number" AS VARCHAR)) = '' 
                THEN 'House'
            ELSE 'Unit'
        END AS property_type
    FROM 'cleaned.csv'
    WHERE lower("Property locality") = lower('{suburb}')
),
latest AS (
    SELECT MAX(contract_date) AS latest_date FROM base
),
classified AS (
    SELECT
        b.property_type,
        b."Purchase price",
        -- How many whole months ago this sale was from the latest sale
        date_diff('month', b.contract_date, l.latest_date) AS months_ago
    FROM base b
    CROSS JOIN latest l
    WHERE b.contract_date IS NOT NULL
      AND date_diff('month', b.contract_date, l.latest_date) >= 0
      AND date_diff('month', b.contract_date, l.latest_date) <= 15 * 12  -- up to 15y back
),
blocks AS (
    -- Group into 12-month blocks: 0 = last 12m, 1 = 12–24m ago, etc.
    SELECT
        property_type,
        CAST(FLOOR(months_ago / 12) AS INTEGER) AS years_ago,
        "Purchase price"
    FROM classified
),
yearly AS (
    SELECT
        years_ago,
        property_type,
        percentile_cont(0.5) WITHIN GROUP (ORDER BY "Purchase price") AS median_price
    FROM blocks
    GROUP BY years_ago, property_type
)
SELECT
    -- CURRENT MEDIANS (last 12 months)
    printf('%,.0f', (SELECT median_price FROM yearly WHERE years_ago = 0 AND property_type = 'House')) AS current_median_house,
    printf('%,.0f', (SELECT median_price FROM yearly WHERE years_ago = 0 AND property_type = 'Unit')) AS current_median_unit,

    -- HOUSE CAGR BASED ON 12-MONTH BLOCKS
    ROUND(
        100 * (
            POWER(
                (SELECT median_price FROM yearly WHERE years_ago = 0 AND property_type = 'House') /
                (SELECT median_price FROM yearly WHERE years_ago = 1 AND property_type = 'House'),
                1.0 / 1
            ) - 1
        ), 2
    ) AS house_avg_growth_1y,
    ROUND(
        100 * (
            POWER(
                (SELECT median_price FROM yearly WHERE years_ago = 0 AND property_type = 'House') /
                (SELECT median_price FROM yearly WHERE years_ago = 3 AND property_type = 'House'),
                1.0 / 3
            ) - 1
        ), 2
    ) AS house_avg_growth_3y,
    ROUND(
        100 * (
            POWER(
                (SELECT median_price FROM yearly WHERE years_ago = 0 AND property_type = 'House') /
                (SELECT median_price FROM yearly WHERE years_ago = 5 AND property_type = 'House'),
                1.0 / 5
            ) - 1
        ), 2
    ) AS house_avg_growth_5y,
    ROUND(
        100 * (
            POWER(
                (SELECT median_price FROM yearly WHERE years_ago = 0 AND property_type = 'House') /
                (SELECT median_price FROM yearly WHERE years_ago = 10 AND property_type = 'House'),
                1.0 / 10
            ) - 1
        ), 2
    ) AS house_avg_growth_10y,
    ROUND(
        100 * (
            POWER(
                (SELECT median_price FROM yearly WHERE years_ago = 0 AND property_type = 'House') /
                (SELECT median_price FROM yearly WHERE years_ago = 15 AND property_type = 'House'),
                1.0 / 15
            ) - 1
        ), 2
    ) AS house_avg_growth_15y,

    -- UNIT CAGR BASED ON 12-MONTH BLOCKS
    ROUND(
        100 * (
            POWER(
                (SELECT median_price FROM yearly WHERE years_ago = 0 AND property_type = 'Unit') /
                (SELECT median_price FROM yearly WHERE years_ago = 1 AND property_type = 'Unit'),
                1.0 / 1
            ) - 1
        ), 2
    ) AS unit_avg_growth_1y,
    ROUND(
        100 * (
            POWER(
                (SELECT median_price FROM yearly WHERE years_ago = 0 AND property_type = 'Unit') /
                (SELECT median_price FROM yearly WHERE years_ago = 3 AND property_type = 'Unit'),
                1.0 / 3
            ) - 1
        ), 2
    ) AS unit_avg_growth_3y,
    ROUND(
        100 * (
            POWER(
                (SELECT median_price FROM yearly WHERE years_ago = 0 AND property_type = 'Unit') /
                (SELECT median_price FROM yearly WHERE years_ago = 5 AND property_type = 'Unit'),
                1.0 / 5
            ) - 1
        ), 2
    ) AS unit_avg_growth_5y,
    ROUND(
        100 * (
            POWER(
                (SELECT median_price FROM yearly WHERE years_ago = 0 AND property_type = 'Unit') /
                (SELECT median_price FROM yearly WHERE years_ago = 10 AND property_type = 'Unit'),
                1.0 / 10
            ) - 1
        ), 2
    ) AS unit_avg_growth_10y,
    ROUND(
        100 * (
            POWER(
                (SELECT median_price FROM yearly WHERE years_ago = 0 AND property_type = 'Unit') /
                (SELECT median_price FROM yearly WHERE years_ago = 15 AND property_type = 'Unit'),
                1.0 / 15
            ) - 1
        ), 2
    ) AS unit_avg_growth_15y
FROM yearly
LIMIT 1;
"""
