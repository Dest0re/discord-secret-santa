SELECT COUNT(*) AS Человеки
FROM (
	SELECT user_id, SUM(price)
    FROM 
		GamePackage
        INNER JOIN Present
	WHERE is_paid = 1
    GROUP BY user_id
    HAVING SUM(price) >= 500
) AS t
