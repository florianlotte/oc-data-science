-- ALL group by order_id
--------------------------------------------------------
WITH
-- PRODUCTS aggregation
products_update AS (
	SELECT
		product_id,
		COALESCE(product_category_name, 'other') AS product_category_name,
		COALESCE(product_name_lenght, 0) AS product_name_lenght,
		COALESCE(product_description_lenght, 0) AS product_description_lenght,
		COALESCE(product_photos_qty, 0) AS product_photos_qty,
		COALESCE(product_weight_g, 0) AS product_weight_g,
		(
			COALESCE(product_length_cm, 0) *
			COALESCE(product_height_cm, 0) *
			COALESCE(product_width_cm, 0)
		) AS product_volume_cm3
	FROM products
),
-- ITEMS group by order_item_id
order_items_update AS (
	SELECT
		oi.order_id,
		COUNT(*) AS order_items_count, 
		COUNT(DISTINCT p.product_category_name) AS product_category_name_distinct_count,
		AVG(p.product_name_lenght) AS product_name_lenght_mean,
		AVG(p.product_description_lenght) AS product_description_lenght_mean,
		AVG(p.product_photos_qty) AS product_photos_qty_mean,
		AVG(p.product_weight_g) AS product_weight_g_mean,
		AVG(p.product_volume_cm3) AS product_volume_cm3_mean,
		group_concat(s.seller_zip_code_prefix) AS seller_zip_code_prefix_list,
		COUNT(DISTINCT s.seller_zip_code_prefix) AS seller_zip_code_prefix_distinct_count,
		AVG(CAST(strftime('%s', shipping_limit_date) AS INT)) AS shipping_limit_date_mean,
		AVG(oi.price) AS price_mean,
		SUM(oi.price) AS price_sum,
		AVG(oi.freight_value) AS freight_value_mean
	FROM order_items oi
	INNER JOIN products_update p ON oi.product_id = p.product_id
	INNER JOIN sellers s ON oi.seller_id = s.seller_id
	GROUP BY order_id
),
-- REVIEWS group by order_id
order_reviews_update AS (
	SELECT order_id,
		COUNT(*) AS reviews_count,
		AVG(review_score) AS review_score_mean,
		AVG(LENGTH(COALESCE(review_comment_message, ''))) AS review_message_mean
	FROM order_reviews
	GROUP BY order_id
),
-- PAYMENTS group by order_id
order_payments_update AS (
	SELECT order_id,
		COUNT(*) AS payments_count,
		SUM(CASE WHEN payment_type = "credit_card" THEN 1 ELSE 0 END) AS payment_credit_card,
		SUM(CASE WHEN payment_type = "debit_card" THEN 1 ELSE 0 END) AS payment_debit_card,
		SUM(CASE WHEN payment_type = "boleto" THEN 1 ELSE 0 END) AS payment_boleto,
		SUM(CASE WHEN payment_type = "voucher" THEN 1 ELSE 0 END) AS payment_voucher,
		SUM(CASE WHEN payment_type = "not_defined" THEN 1 ELSE 0 END) AS payment_not_defined,
		AVG(payment_installments) AS payment_installments_mean,
		AVG(payment_value) AS payment_value_mean,
		SUM(payment_value) AS payment_value_sum
	FROM order_payments
	GROUP BY order_id
),
-- CUSTOMERS by customer_unique_id
customers_update AS (
	SELECT c.*,
		g.geolocation_city,
		g.geolocation_state
	FROM customers c
	INNER JOIN geolocation g ON g.geolocation_zip_code_prefix = c.customer_zip_code_prefix
),
-- ORDERS format 1
orders_update AS (
	SELECT
		order_id,
		customer_unique_id,
		order_status,
		CAST(strftime('%s', date('now')) AS INT)-CAST(strftime('%s', order_purchase_timestamp) AS INT) AS order_diff_now_purchase_date,
		CAST(strftime('%s', order_purchase_timestamp) AS INT) AS order_purchase_date,
		CAST(COALESCE(strftime('%s', order_approved_at), strftime('%s', order_purchase_timestamp)) AS INT) AS order_approved_date,
		CAST(COALESCE(strftime('%s', order_delivered_carrier_date), strftime('%s', date(order_purchase_timestamp, '+1 year'))) AS INT) AS order_delivered_carrier_date,
		CAST(COALESCE(strftime('%s', order_delivered_customer_date), strftime('%s', date(order_purchase_timestamp, '+2 year'))) AS INT) AS order_delivered_customer_date,
		CAST(COALESCE(strftime('%s', order_estimated_delivery_date), strftime('%s', date(order_purchase_timestamp, '+1 year'))) AS INT) AS order_estimated_delivery_date
	FROM orders
),
-- ORDERS format 2 and group all by order_id
orders_update2 AS (
	SELECT
		o.order_id,
		o.customer_unique_id,
		o.order_status,
		o.order_diff_now_purchase_date,
		o.order_purchase_date,
		o.order_approved_date,
		o.order_delivered_carrier_date,
		o.order_delivered_customer_date,
		o.order_estimated_delivery_date,
		(o.order_delivered_carrier_date-o.order_purchase_date) AS order_diff_purchase_delivered_date,
		(o.order_delivered_carrier_date-o.order_estimated_delivery_date) AS order_diff_estimated_delivered_date,
		-- items
		oiu.order_items_count,
		oiu.product_category_name_distinct_count,
		oiu.product_name_lenght_mean,
		oiu.product_description_lenght_mean,
		oiu.product_photos_qty_mean,
		oiu.product_weight_g_mean,
		oiu.product_volume_cm3_mean,
		oiu.seller_zip_code_prefix_list,
		oiu.seller_zip_code_prefix_distinct_count,
		oiu.shipping_limit_date_mean,
		oiu.price_mean,
		oiu.price_sum,
		oiu.freight_value_mean,
		-- reviews
		oru.reviews_count,
		oru.review_score_mean,
		oru.review_message_mean,
		-- payments
		opu.payments_count,
		opu.payment_credit_card,
		opu.payment_debit_card,
		opu.payment_boleto,
		opu.payment_voucher,
		opu.payment_not_defined,
		opu.payment_installments_mean,
		opu.payment_value_mean,
		opu.payment_value_sum
	FROM orders_update o
	INNER JOIN order_items_update oiu ON oiu.order_id = o.order_id
	INNER JOIN order_reviews_update oru ON oru.order_id = o.order_id
	INNER JOIN order_payments_update opu ON opu.order_id = o.order_id
)
-- ORDERS groupe by customer_unique_id
SELECT
	-- orders
	o.customer_unique_id,
	count(*) AS order_id_count,
	SUM(CASE WHEN o.order_status = "delivered" THEN 1 ELSE 0 END) AS order_status_delivered,
	SUM(CASE WHEN o.order_status = "invoiced" THEN 1 ELSE 0 END) AS order_status_invoiced,
	SUM(CASE WHEN o.order_status = "shipped" THEN 1 ELSE 0 END) AS order_status_shipped,
	SUM(CASE WHEN o.order_status = "processing" THEN 1 ELSE 0 END) AS order_status_processing,
	SUM(CASE WHEN o.order_status = "unavailable" THEN 1 ELSE 0 END) AS order_status_unavailable,
	SUM(CASE WHEN o.order_status = "canceled" THEN 1 ELSE 0 END) AS order_status_canceled,
	SUM(CASE WHEN o.order_status = "created" THEN 1 ELSE 0 END) AS order_status_created,
	SUM(CASE WHEN o.order_status = "approved" THEN 1 ELSE 0 END) AS order_status_approved,
	MIN(o.order_diff_now_purchase_date) AS order_diff_now_purchase_date_min,
	MAX(o.order_diff_now_purchase_date) AS order_diff_now_purchase_date_max,
	AVG(o.order_diff_now_purchase_date) AS order_diff_now_purchase_date_mean,
	MIN(o.order_diff_purchase_delivered_date) AS order_diff_purchase_delivered_date_min,
	MAX(o.order_diff_purchase_delivered_date) AS order_diff_purchase_delivered_date_max,
	AVG(o.order_diff_purchase_delivered_date) AS order_diff_purchase_delivered_date_mean,
	MIN(o.order_diff_estimated_delivered_date) AS order_diff_estimated_delivered_date_min,
	MAX(o.order_diff_estimated_delivered_date) AS order_diff_estimated_delivered_date_max,
	AVG(o.order_diff_estimated_delivered_date) AS order_diff_estimated_delivered_date_mean,
	-- items
	SUM(o.order_items_count) AS order_items_count_sum,
	AVG(o.order_items_count) AS order_items_count_mean,
	AVG(o.product_category_name_distinct_count) AS product_category_name_distinct_count_mean,
	AVG(o.product_name_lenght_mean) AS product_name_lenght_mean_mean,
	AVG(o.product_description_lenght_mean) AS product_description_lenght_mean_mean,
	AVG(o.product_photos_qty_mean) AS product_photos_qty_mean_mean,
	AVG(o.product_weight_g_mean) AS product_weight_g_mean_mean,
	AVG(o.product_volume_cm3_mean) AS product_volume_cm3_mean_mean,
	group_concat(o.seller_zip_code_prefix_list) AS seller_zip_code_prefix_list,
	AVG(o.seller_zip_code_prefix_distinct_count) AS seller_zip_code_prefix_distinct_count_mean,
	AVG(o.shipping_limit_date_mean) AS shipping_limit_date_mean_mean,
	AVG(o.price_mean) AS price_mean_mean,
	SUM(o.price_sum) AS price_sum,
	AVG(o.freight_value_mean) AS freight_value_mean_mean,
	-- reviews
	SUM(o.reviews_count) AS reviews_count_sum,
	AVG(o.reviews_count) AS reviews_count_mean,
	AVG(o.review_score_mean) AS review_score_mean_mean,
	AVG(o.review_message_mean) AS review_message_mean_mean,
	-- payments
	SUM(o.payments_count) AS payments_count_sum,
	AVG(o.payments_count) AS payments_count_mean,
	SUM(o.payment_credit_card) AS payment_credit_card_sum,
	AVG(o.payment_credit_card) AS payment_credit_card_mean,
	SUM(o.payment_debit_card) AS payment_debit_sum,
	AVG(o.payment_debit_card) AS payment_debit_mean,
	SUM(o.payment_boleto) AS payment_boleto_sum,
	AVG(o.payment_boleto) AS payment_boleto_mean,
	SUM(o.payment_voucher) AS payment_voucher_sum,
	AVG(o.payment_voucher) AS payment_voucher_mean,
	SUM(o.payment_not_defined) AS payment_not_defined_sum,
	AVG(o.payment_not_defined) AS payment_not_defined_mean,
	AVG(o.payment_installments_mean) AS payment_installments_mean_mean,
	AVG(o.payment_value_mean) AS payment_value_mean_mean,
	SUM(o.payment_value_sum) AS payment_value_sum,
	-- customers
	c.customer_unique_id,
	c.customer_zip_code_prefix,
	c.geolocation_city,
	c.geolocation_state
FROM orders_update2 o
INNER JOIN customers_update c ON c.customer_unique_id = o.customer_unique_id
GROUP BY o.customer_unique_id
