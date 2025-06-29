-- Average performance of ads and natural
SELECT
    type,
    COUNT(*) AS num_products, 
    ROUND(AVG(trade), 1) AS avg_trade,
    ROUND(AVG(price), 2) AS avg_price,
    ROUND(AVG(rating), 2) AS avg_rating
FROM cleaned_products
GROUP BY type;

-- Distribution of sales by type
SELECT
    type,
    trade
FROM cleaned_products;

-- Top Selling Products: Ads vs Natural
SELECT
    type,
    title,
    price,
    trade,
    rating,
    url
FROM cleaned_products
ORDER BY trade DESC
LIMIT 20;

-- Keyword Breakdown
SELECT
    type,
    SUBSTRING_INDEX(title, ' ', 1) AS first_word,
    COUNT(*) AS count,
    ROUND(AVG(trade), 0) AS avg_trade
FROM cleaned_products
GROUP BY type, first_word
ORDER BY count DESC
LIMIT 20;
