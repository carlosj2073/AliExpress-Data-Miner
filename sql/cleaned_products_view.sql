-- cleaned_products view
CREATE OR REPLACE VIEW cleaned_products AS
SELECT
    id,
    type,
    thumbnail,
    title,
    price,
    currency,
    selling_points,
    rating,
    CAST(REPLACE(SUBSTRING_INDEX(SUBSTRING_INDEX(trade, ' ', 1), '+', 1), ',', '') AS UNSIGNED) AS trade,
    url
FROM products
WHERE
	id IS NOT NULL AND
    type IS NOT NULL AND
    thumbnail IS NOT NULL AND
    title IS NOT NULL AND
    price IS NOT NULL AND
    currency IS NOT NULL AND
    rating IS NOT NULL AND
    trade IS NOT NULL AND
    url IS NOT NULL AND
    selling_points IS NOT NULL AND selling_points != '';

-- incomplete_products view
CREATE OR REPLACE VIEW incomplete_products AS
SELECT
    id,
    type,
    thumbnail,
    title,
    price,
    currency,
    selling_points,
    rating,
    CAST(REPLACE(SUBSTRING_INDEX(SUBSTRING_INDEX(trade, ' ', 1), '+', 1), ',', '') AS UNSIGNED) AS trade,
    url
FROM products
WHERE
	id IS NULL OR
    type IS NULL OR
    thumbnail IS NULL OR
    title IS NULL OR
    price IS NULL OR
    currency IS NULL OR
    rating IS NULL OR
    trade IS NULL OR
    url IS NULL OR
    selling_points IS NULL OR selling_points = '';
