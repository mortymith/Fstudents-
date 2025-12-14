-- =============================================
-- INSERT 15 ROWS INTO EACH TABLE
-- Using GENERATED ALWAYS AS IDENTITY - DO NOT specify ID column
-- =============================================

INSERT INTO users (email, password_hash, full_name, role, is_active, last_login_at, created_at, updated_at) VALUES
('admin1@company.com', '$2a$10$hash1', 'John Admin', 'admin', true, '2025-01-15 10:30:00', '2024-01-01 09:00:00', '2024-01-15 10:30:00'),
('admin2@company.com', '$2a$10$hash2', 'Sarah Manager', 'admin', true, '2025-01-14 14:20:00', '2024-01-02 09:00:00', '2024-01-14 14:20:00'),
('admin3@company.com', '$2a$10$hash3', 'Michael Director', 'admin', true, '2025-01-13 16:45:00', '2024-01-03 09:00:00', '2024-01-13 16:45:00'),
('inventory1@company.com', '$2a$10$hash4', 'Robert Wilson', 'inventory_manager', true, '2025-01-15 11:10:00', '2024-01-04 09:00:00', '2024-01-15 11:10:00'),
('inventory2@company.com', '$2a$10$hash5', 'Lisa Thompson', 'inventory_manager', true, '2025-01-14 13:30:00', '2024-01-05 09:00:00', '2024-01-14 13:30:00'),
('inventory3@company.com', '$2a$10$hash6', 'David Chen', 'inventory_manager', true, '2025-01-13 15:20:00', '2024-01-06 09:00:00', '2024-01-13 15:20:00'),
('inventory4@company.com', '$2a$10$hash7', 'Maria Garcia', 'inventory_manager', true, '2025-01-12 10:15:00', '2024-01-07 09:00:00', '2024-01-12 10:15:00'),
('inventory5@company.com', '$2a$10$hash8', 'James Miller', 'inventory_manager', true, '2025-01-11 09:45:00', '2024-01-08 09:00:00', '2024-01-11 09:45:00'),
('viewer1@company.com', '$2a$10$hash9', 'Jennifer Lee', 'viewer', true, '2025-01-10 08:30:00', '2024-01-09 09:00:00', '2024-01-10 08:30:00'),
('viewer2@company.com', '$2a$10$hash10', 'Thomas Brown', 'viewer', true, '2025-01-09 14:10:00', '2024-01-10 09:00:00', '2024-01-19 14:10:00'),
('viewer3@company.com', '$2a$10$hash11', 'Emily Davis', 'viewer', true, '2025-01-08 11:25:00', '2024-01-11 09:00:00', '2024-01-13 11:25:00'),
('viewer4@company.com', '$2a$10$hash12', 'William Johnson', 'viewer', true, '2025-01-07 16:40:00', '2024-01-12 09:00:00', '2024-01-22 16:40:00'),
('viewer5@company.com', '$2a$10$hash13', 'Patricia Smith', 'viewer', true, '2025-01-06 10:50:00', '2024-01-13 09:00:00', '2024-01-30 10:50:00'),
('viewer6@company.com', '$2a$10$hash14', 'Richard Wilson', 'viewer', false, '2025-01-05 09:15:00', '2024-01-14 09:00:00', '2024-01-15 10:00:00'),
('viewer7@company.com', '$2a$10$hash15', 'Susan Taylor', 'viewer', true, '2025-01-04 13:20:00', '2024-01-15 09:00:00', '2024-01-16 09:00:00');



-- First insert root categories
INSERT INTO categories (name, description, parent_id, is_active, created_at, updated_at) VALUES
('Electronics', 'Electronic devices and components', NULL, true, '2024-01-01 10:00:00', '2024-01-01 10:00:00'),
('Clothing', 'Apparel and accessories', NULL, true, '2024-01-01 10:05:00', '2024-01-01 10:05:00'),
('Home & Garden', 'Home improvement and garden supplies', NULL, true, '2024-01-01 10:10:00', '2024-01-01 10:10:00'),
('Office Supplies', 'Office equipment and stationery', NULL, true, '2024-01-01 10:15:00', '2024-01-01 10:15:00');


WITH root_cats AS (
    SELECT id, name FROM categories WHERE parent_id IS NULL
)
INSERT INTO categories (name, description, parent_id, is_active, created_at, updated_at)
SELECT 
    subcat.name,
    subcat.description,
    rc.id,
    true,
    subcat.created_at::timestamp,
    subcat.created_at::timestamp
FROM (
    VALUES
    ('Laptops', 'Portable computers and accessories', 'Electronics', '2024-01-01 10:20:00'::timestamp),
    ('Smartphones', 'Mobile phones and accessories', 'Electronics', '2024-01-01 10:25:00'::timestamp),
    ('Audio Equipment', 'Speakers, headphones, and audio devices', 'Electronics', '2024-01-01 10:30:00'::timestamp),
    ('Men''s Clothing', 'Clothing for men', 'Clothing', '2024-01-01 10:35:00'::timestamp),
    ('Women''s Clothing', 'Clothing for women', 'Clothing', '2024-01-01 10:40:00'::timestamp),
    ('Accessories', 'Fashion accessories', 'Clothing', '2024-01-01 10:45:00'::timestamp),
    ('Furniture', 'Home furniture', 'Home & Garden', '2024-01-01 10:50:00'::timestamp),
    ('Tools', 'Hand and power tools', 'Home & Garden', '2024-01-01 10:55:00'::timestamp),
    ('Lighting', 'Indoor and outdoor lighting', 'Home & Garden', '2024-01-01 11:00:00'::timestamp),
    ('Paper Products', 'Paper, notebooks, and planners', 'Office Supplies', '2024-01-01 11:05:00'::timestamp),
    ('Writing Instruments', 'Pens, pencils, and markers', 'Office Supplies', '2024-01-01 11:10:00'::timestamp),
    ('Desk Organizers', 'Desktop organization solutions', 'Office Supplies', '2024-01-01 11:15:00'::timestamp)
) AS subcat(name, description, parent_name, created_at)
JOIN root_cats rc ON rc.name = subcat.parent_name;

-- Insert 15 suppliers (no dependencies)
INSERT INTO suppliers (name, contact_person_name, contact_email, contact_phone, address_line1, address_line2, city, state, postal_code, country, is_active, created_at, updated_at) VALUES
('TechGlobal Inc.', 'Mark Johnson', 'mark@techglobal.com', '+1-555-0101', '123 Tech Blvd', 'Suite 100', 'San Jose', 'CA', '95101', 'USA', true, '2024-01-01 12:00:00', '2024-01-01 12:00:00'),
('GadgetWorld Ltd.', 'Sarah Chen', 'sarah@gadgetworld.com', '+1-555-0102', '456 Gadget St', NULL, 'Austin', 'TX', '73301', 'USA', true, '2024-01-02 12:00:00', '2024-01-02 12:00:00'),
('FashionHub Corp.', 'Robert Miller', 'robert@fashionhub.com', '+1-555-0103', '789 Fashion Ave', 'Floor 5', 'New York', 'NY', '10001', 'USA', true, '2024-01-03 12:00:00', '2024-01-03 12:00:00'),
('OfficeMax Supplies', 'Lisa Wong', 'lisa@officemax.com', '+1-555-0104', '321 Office Rd', NULL, 'Chicago', 'IL', '60601', 'USA', true, '2024-01-04 12:00:00', '2024-01-04 12:00:00'),
('HomeEssentials Co.', 'David Brown', 'david@homeessentials.com', '+1-555-0105', '654 Home St', 'Building B', 'Miami', 'FL', '33101', 'USA', true, '2024-01-05 12:00:00', '2024-01-05 12:00:00'),
('ElectroParts Inc.', 'Jennifer Lee', 'jennifer@electroparts.com', '+1-555-0106', '987 Circuit Ln', NULL, 'Seattle', 'WA', '98101', 'USA', true, '2024-01-06 12:00:00', '2024-01-06 12:00:00'),
('TextileMasters Ltd.', 'Thomas Wilson', 'thomas@textilemasters.com', '+1-555-0107', '147 Fabric St', 'Warehouse 3', 'Los Angeles', 'CA', '90001', 'USA', true, '2024-01-07 12:00:00', '2024-01-07 12:00:00'),
('ToolCrafters Inc.', 'Maria Garcia', 'maria@toolcrafters.com', '+1-555-0108', '258 Tool Ave', NULL, 'Denver', 'CO', '80201', 'USA', true, '2024-01-08 12:00:00', '2024-01-08 12:00:00'),
('StationeryPro Co.', 'James Taylor', 'james@stationerypro.com', '+1-555-0109', '369 Paper Rd', 'Suite 200', 'Boston', 'MA', '02101', 'USA', true, '2024-01-09 12:00:00', '2024-01-09 12:00:00'),
('LightingExperts Ltd.', 'Patricia Clark', 'patricia@lightingexperts.com', '+1-555-0110', '741 Light Blvd', NULL, 'Phoenix', 'AZ', '85001', 'USA', true, '2024-01-10 12:00:00', '2024-01-10 12:00:00'),
('AudioMasters Inc.', 'Richard Martinez', 'richard@audiomasters.com', '+1-555-0111', '852 Sound St', 'Unit 50', 'Dallas', 'TX', '75201', 'USA', true, '2024-01-11 12:00:00', '2024-01-11 12:00:00'),
('FurnitureCraft Co.', 'Susan Anderson', 'susan@furniturecraft.com', '+1-555-0112', '963 Wood Rd', NULL, 'Atlanta', 'GA', '30301', 'USA', true, '2024-01-12 12:00:00', '2024-01-12 12:00:00'),
('AccessoryWorld Ltd.', 'William Thomas', 'william@accessoryworld.com', '+1-555-0113', '159 Accessory Ave', 'Floor 2', 'San Francisco', 'CA', '94101', 'USA', true, '2024-01-13 12:00:00', '2024-01-13 12:00:00'),
('GlobalElectronics Co.', 'Nancy White', 'nancy@globalelectronics.com', '+1-555-0114', '753 Global St', NULL, 'Houston', 'TX', '77001', 'USA', true, '2024-01-14 12:00:00', '2024-01-14 12:00:00'),
('PremiumSupplies Inc.', 'Charles Harris', 'charles@premiumsupplies.com', '+1-555-0115', '852 Premium Blvd', 'Suite 300', 'Philadelphia', 'PA', '19101', 'USA', true, '2024-01-15 12:00:00', '2024-01-15 12:00:00');


WITH cat_supp AS (
    SELECT 
        c.id AS cat_id, 
        c.name AS cat_name,
        s.id AS supp_id,
        s.name AS supp_name
    FROM categories c
    CROSS JOIN suppliers s
    WHERE c.name IN (
        'Laptops','Smartphones','Audio Equipment','Men''s Clothing','Women''s Clothing',
        'Accessories','Furniture','Tools','Lighting','Paper Products',
        'Writing Instruments','Desk Organizers'
    )
    AND s.name IN (
        'TechGlobal Inc.','GadgetWorld Ltd.','FashionHub Corp.','OfficeMax Supplies',
        'HomeEssentials Co.','ElectroParts Inc.','TextileMasters Ltd.',
        'ToolCrafters Inc.','StationeryPro Co.','LightingExperts Ltd.',
        'AudioMasters Inc.','FurnitureCraft Co.','AccessoryWorld Ltd.',
        'GlobalElectronics Co.','PremiumSupplies Inc.'
    )
)
INSERT INTO products (
    sku, name, description, category_id, supplier_id, price, cost_price,
    low_stock_threshold, reorder_point, reorder_quantity,
    expiry_date, barcode_data, qr_code_data,
    is_active, created_at, updated_at
)
SELECT 
    NULL,
    prod.name,
    prod.description,
    cs.cat_id,
    cs.supp_id,
    prod.price,
    prod.cost_price,
    prod.low_stock_threshold,
    prod.reorder_point,
    prod.reorder_quantity,
    prod.expiry_date::date,
    prod.barcode_data,
    prod.qr_code_data,
    true,
    prod.created_at::timestamp,
    prod.created_at::timestamp
FROM (
    VALUES
    ('Premium Laptop Pro', 'High-performance laptop with 16GB RAM, 512GB SSD', 'Laptops', 'TechGlobal Inc.', 1299.99, 950.00, 5, 10, 20, NULL, '8901234567890', 'data:image/qr;base64,ABC123', '2024-01-01 13:00:00'),
    ('Smartphone X10', 'Latest smartphone with 128GB storage, triple camera', 'Smartphones', 'GadgetWorld Ltd.', 899.99, 650.00, 10, 20, 30, NULL, '8901234567891', 'data:image/qr;base64,ABC124', '2024-01-02 13:00:00'),
    ('Wireless Headphones', 'Noise-cancelling wireless headphones', 'Audio Equipment', 'AudioMasters Inc.', 199.99, 120.00, 15, 25, 40, NULL, '8901234567892', 'data:image/qr;base64,ABC125', '2024-01-03 13:00:00'),
    ('Men''s Casual Shirt', '100% cotton casual shirt, multiple colors', 'Men''s Clothing', 'FashionHub Corp.', 29.99, 15.00, 20, 50, 100, NULL, '8901234567893', 'data:image/qr;base64,ABC126', '2024-01-04 13:00:00'),
    ('Women''s Dress', 'Elegant evening dress, various sizes', 'Women''s Clothing', 'TextileMasters Ltd.', 89.99, 45.00, 10, 30, 60, NULL, '8901234567894', 'data:image/qr;base64,ABC127', '2024-01-05 13:00:00'),
    ('Leather Belt', 'Genuine leather belt with metal buckle', 'Accessories', 'AccessoryWorld Ltd.', 39.99, 18.00, 25, 60, 120, NULL, '8901234567895', 'data:image/qr;base64,ABC128', '2024-01-06 13:00:00'),
    ('Office Chair', 'Ergonomic office chair with adjustable height', 'Furniture', 'FurnitureCraft Co.', 249.99, 150.00, 8, 15, 30, NULL, '8901234567896', 'data:image/qr;base64,ABC129', '2024-01-07 13:00:00'),
    ('Power Drill Kit', 'Cordless power drill with multiple attachments', 'Tools', 'ToolCrafters Inc.', 129.99, 75.00, 12, 25, 50, NULL, '8901234567897', 'data:image/qr;base64,ABC130', '2024-01-08 13:00:00'),
    ('LED Desk Lamp', 'Adjustable LED desk lamp with touch controls', 'Lighting', 'LightingExperts Ltd.', 49.99, 25.00, 30, 75, 150, NULL, '8901234567898', 'data:image/qr;base64,ABC131', '2024-01-09 13:00:00'),
    ('Premium Notebook', 'Hardcover notebook with 200 pages', 'Paper Products', 'StationeryPro Co.', 12.99, 6.00, 50, 100, 200, '2025-12-31', '8901234567899', 'data:image/qr;base64,ABC132', '2024-01-10 13:00:00'),
    ('Executive Pen Set', 'Set of 3 premium ballpoint pens', 'Writing Instruments', 'OfficeMax Supplies', 24.99, 12.00, 40, 80, 160, NULL, '8901234567900', 'data:image/qr;base64,ABC133', '2024-01-11 13:00:00'),
    ('Desktop Organizer', 'Multi-compartment desktop organizer', 'Desk Organizers', 'OfficeMax Supplies', 19.99, 10.00, 35, 70, 140, NULL, '8901234567901', 'data:image/qr;base64,ABC134', '2024-01-12 13:00:00'),
    ('Tablet Air', 'Lightweight tablet with 10-inch display', 'Laptops', 'TechGlobal Inc.', 499.99, 350.00, 8, 15, 30, NULL, '8901234567902', 'data:image/qr;base64,ABC135', '2024-01-13 13:00:00'),
    ('Bluetooth Speaker', 'Portable Bluetooth speaker with 10-hour battery', 'Audio Equipment', 'AudioMasters Inc.', 79.99, 40.00, 25, 50, 100, NULL, '8901234567903', 'data:image/qr;base64,ABC136', '2024-01-14 13:00:00'),
    ('Smartwatch Pro', 'Fitness tracking smartwatch with GPS', 'Smartphones', 'GadgetWorld Ltd.', 299.99, 180.00, 12, 25, 50, NULL, '8901234567904', 'data:image/qr;base64,ABC137', '2024-01-15 13:00:00')
) AS prod(
    name, description, cat_name, supp_name,
    price, cost_price,
    low_stock_threshold, reorder_point, reorder_quantity,
    expiry_date, barcode_data, qr_code_data, created_at
)
JOIN cat_supp cs
  ON cs.cat_name = prod.cat_name
 AND cs.supp_name = prod.supp_name;


-- =============================================
-- INVENTORY TRACKING TABLES
-- =============================================
-- Insert product inventory for all products
WITH product_list AS (
    SELECT id, created_at 
    FROM products 
    ORDER BY id
    LIMIT 15
)
INSERT INTO product_inventory (
    product_id, quantity_on_hand, quantity_committed, quantity_available, 
    last_restocked_at, last_counted_at, created_at, updated_at
)
SELECT 
    pl.id,
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 1 THEN 50
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 2 THEN 100
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 3 THEN 200
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 4 THEN 150
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 5 THEN 80
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 6 THEN 300
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 7 THEN 40
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 8 THEN 120
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 9 THEN 250
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 10 THEN 500
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 11 THEN 400
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 12 THEN 180
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 13 THEN 60
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 14 THEN 350
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 15 THEN 90
    END,
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 1 THEN 5
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 2 THEN 15
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 3 THEN 30
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 4 THEN 10
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 5 THEN 8
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 6 THEN 50
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 7 THEN 3
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 8 THEN 12
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 9 THEN 25
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 10 THEN 40
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 11 THEN 35
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 12 THEN 18
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 13 THEN 6
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 14 THEN 45
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 15 THEN 9
    END,
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 1 THEN 45
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 2 THEN 85
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 3 THEN 170
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 4 THEN 140
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 5 THEN 72
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 6 THEN 250
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 7 THEN 37
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 8 THEN 108
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 9 THEN 225
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 10 THEN 460
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 11 THEN 365
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 12 THEN 162
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 13 THEN 54
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 14 THEN 305
        WHEN ROW_NUMBER() OVER (ORDER BY pl.id) = 15 THEN 81
    END,
    pl.created_at + INTERVAL '9 days',
    pl.created_at + INTERVAL '14 days',
    pl.created_at + INTERVAL '1 hour',
    pl.created_at + INTERVAL '14 days'
FROM product_list pl;




-- Insert purchase orders with proper user and supplier references
WITH user_supplier_combinations AS (
    SELECT 
        u.id as user_id,
        u.email,
        s.id as supplier_id,
        s.name as supplier_name,
        ROW_NUMBER() OVER (ORDER BY u.id, s.id) as rn
    FROM users u
    CROSS JOIN suppliers s
    WHERE u.email LIKE '%inventory%' OR u.email LIKE '%admin%'
    LIMIT 15
)
INSERT INTO purchase_orders (
    po_number, supplier_id, status, total_amount, ordered_date, 
    expected_delivery_date, received_date, created_by, created_at, updated_at
)
SELECT 
    NULL,
    usc.supplier_id,
    CASE 
        WHEN usc.rn <= 2 THEN 'draft'
        WHEN usc.rn <= 5 THEN 'ordered'
        WHEN usc.rn <= 10 THEN 'received'
        WHEN usc.rn = 11 THEN 'cancelled'
        ELSE 'ordered'
    END,
    CASE 
        WHEN usc.rn = 3 THEN 1500.00
        WHEN usc.rn = 4 THEN 800.50
        WHEN usc.rn = 5 THEN 2200.75
        WHEN usc.rn = 6 THEN 3200.00
        WHEN usc.rn = 7 THEN 950.25
        WHEN usc.rn = 8 THEN 1800.00
        WHEN usc.rn = 9 THEN 1250.50
        WHEN usc.rn = 10 THEN 750.00
        WHEN usc.rn = 11 THEN 1600.00
        WHEN usc.rn = 12 THEN 2900.00
        WHEN usc.rn = 13 THEN 1100.75
        WHEN usc.rn = 14 THEN 850.25
        WHEN usc.rn = 15 THEN 1950.00
        ELSE NULL
    END,
    CASE 
        WHEN usc.rn >= 3 THEN CURRENT_DATE - INTERVAL '30 days' + (usc.rn * INTERVAL '1 day')
        ELSE NULL
    END,
    CASE 
        WHEN usc.rn >= 3 THEN CURRENT_DATE - INTERVAL '30 days' + (usc.rn * INTERVAL '1 day') + INTERVAL '7 days'
        ELSE NULL
    END,
    CASE 
        WHEN usc.rn BETWEEN 6 AND 10 THEN CURRENT_DATE - INTERVAL '30 days' + (usc.rn * INTERVAL '1 day') + INTERVAL '7 days'
        ELSE NULL
    END,
    usc.user_id,
    CURRENT_DATE - INTERVAL '30 days' + (usc.rn * INTERVAL '1 day'),
    CURRENT_DATE - INTERVAL '30 days' + (usc.rn * INTERVAL '1 day')
FROM user_supplier_combinations usc;

-- Insert purchase order items with proper references
WITH po_product_combinations AS (
    SELECT 
        po.id as po_id,
        po.status,
        p.id as product_id,
        p.cost_price,
        ROW_NUMBER() OVER (PARTITION BY po.id ORDER BY p.id) as item_num,
        ROW_NUMBER() OVER (ORDER BY po.id, p.id) as global_rn
    FROM purchase_orders po
    CROSS JOIN products p
    WHERE po.status IN ('ordered', 'received', 'cancelled')
    AND EXISTS (SELECT 1 FROM purchase_orders po2 WHERE po2.id = po.id)
    ORDER BY po.id, p.id
    LIMIT 15
)
INSERT INTO purchase_order_items (
    purchase_order_id, product_id, quantity_ordered, quantity_received, 
    unit_cost, line_total, created_at, updated_at
)
SELECT 
    ppc.po_id,
    ppc.product_id,
    CASE 
        WHEN ppc.global_rn <= 2 THEN 10
        WHEN ppc.global_rn <= 4 THEN 5
        WHEN ppc.global_rn <= 6 THEN 20
        WHEN ppc.global_rn <= 8 THEN 15
        WHEN ppc.global_rn <= 10 THEN 25
        WHEN ppc.global_rn <= 12 THEN 30
        WHEN ppc.global_rn <= 14 THEN 8
        ELSE 12
    END,
    CASE 
        WHEN ppc.status = 'received' THEN 
            CASE 
                WHEN ppc.global_rn <= 2 THEN 10
                WHEN ppc.global_rn <= 4 THEN 5
                WHEN ppc.global_rn <= 6 THEN 20
                WHEN ppc.global_rn <= 8 THEN 15
                WHEN ppc.global_rn <= 10 THEN 25
                WHEN ppc.global_rn <= 12 THEN 30
                WHEN ppc.global_rn <= 14 THEN 8
                ELSE 12
            END
        ELSE 0
    END,
    ppc.cost_price,
    CASE 
        WHEN ppc.global_rn <= 2 THEN 10 * ppc.cost_price
        WHEN ppc.global_rn <= 4 THEN 5 * ppc.cost_price
        WHEN ppc.global_rn <= 6 THEN 20 * ppc.cost_price
        WHEN ppc.global_rn <= 8 THEN 15 * ppc.cost_price
        WHEN ppc.global_rn <= 10 THEN 25 * ppc.cost_price
        WHEN ppc.global_rn <= 12 THEN 30 * ppc.cost_price
        WHEN ppc.global_rn <= 14 THEN 8 * ppc.cost_price
        ELSE 12 * ppc.cost_price
    END,
    po.created_at,
    CASE 
        WHEN ppc.status = 'received' THEN po.updated_at
        ELSE po.created_at
    END
FROM po_product_combinations ppc
JOIN purchase_orders po ON po.id = ppc.po_id;


-- =============================================
-- STOCK MOVEMENT AND TRANSACTION TABLES
-- =============================================
-- Insert stock movements with proper references
WITH product_user_combinations AS (
    SELECT 
        p.id as product_id,
        u.id as user_id,
        ROW_NUMBER() OVER (ORDER BY p.id, u.id) as rn
    FROM products p
    CROSS JOIN users u
    WHERE u.email LIKE '%inventory%' OR u.email LIKE '%admin%'
    ORDER BY p.id, u.id
    LIMIT 15
)
INSERT INTO stock_movements (
    product_id, movement_type, quantity_change, quantity_before, 
    quantity_after, reference_type, reference_id, movement_date, 
    created_by, created_at, updated_at
)
SELECT 
    puc.product_id,
    CASE 
        WHEN puc.rn <= 5 THEN 'in'
        WHEN puc.rn <= 10 THEN 'out'
        ELSE 'adjustment'
    END,
    CASE 
        WHEN puc.rn <= 5 THEN 100 - (puc.rn * 10)
        WHEN puc.rn <= 10 THEN -((puc.rn - 5) * 5)
        ELSE CASE WHEN puc.rn % 2 = 0 THEN 10 ELSE -10 END
    END,
    CASE 
        WHEN puc.rn <= 5 THEN 0
        WHEN puc.rn <= 10 THEN 200 - ((puc.rn - 6) * 20)
        ELSE 100
    END,
    CASE 
        WHEN puc.rn <= 5 THEN 100 - (puc.rn * 10)
        WHEN puc.rn <= 10 THEN 200 - ((puc.rn - 6) * 20) - ((puc.rn - 5) * 5)
        ELSE CASE WHEN puc.rn % 2 = 0 THEN 110 ELSE 90 END
    END,
    CASE 
        WHEN puc.rn <= 5 THEN 'purchase_order'
        WHEN puc.rn <= 10 THEN 'sale'
        ELSE 'adjustment'
    END,
    CASE 
        WHEN puc.rn <= 5 THEN puc.rn + 100
        WHEN puc.rn <= 10 THEN puc.rn + 200
        ELSE puc.rn + 300
    END,
    CURRENT_DATE - INTERVAL '15 days' + (puc.rn * INTERVAL '1 day'),
    puc.user_id,
    CURRENT_DATE - INTERVAL '15 days' + (puc.rn * INTERVAL '1 day'),
    CURRENT_DATE - INTERVAL '15 days' + (puc.rn * INTERVAL '1 day')
FROM product_user_combinations puc;





-- Insert stock adjustments with proper references
WITH adjustment_combinations AS (
    SELECT 
        p.id as product_id,
        u.id as user_id,
        ROW_NUMBER() OVER (ORDER BY p.id, u.id) as rn
    FROM products p
    CROSS JOIN users u
    WHERE u.email LIKE '%inventory%' OR u.email LIKE '%admin%'
    ORDER BY p.id, u.id
    LIMIT 15
)
INSERT INTO stock_adjustments (
    product_id, adjustment_type, quantity_adjusted, reason, 
    adjustment_date, created_by, created_at, updated_at
)
SELECT 
    ac.product_id,
    CASE 
        WHEN ac.rn <= 3 THEN 'damaged'
        WHEN ac.rn = 4 THEN 'expired'
        WHEN ac.rn <= 6 THEN 'theft'
        WHEN ac.rn <= 8 THEN 'found'
        WHEN ac.rn <= 10 THEN 'returned'
        ELSE 'internal_use'
    END,
    CASE 
        WHEN ac.rn <= 3 THEN -ac.rn
        WHEN ac.rn = 4 THEN -20
        WHEN ac.rn <= 6 THEN -(ac.rn * 2)
        WHEN ac.rn <= 8 THEN ac.rn - 6
        WHEN ac.rn <= 10 THEN ac.rn - 8
        ELSE -(ac.rn - 10)
    END,
    CASE 
        WHEN ac.rn <= 3 THEN 'Damage reported during quality inspection'
        WHEN ac.rn = 4 THEN 'Product expired past shelf life date'
        WHEN ac.rn <= 6 THEN 'Inventory discrepancy identified during audit'
        WHEN ac.rn <= 8 THEN 'Found in unexpected location during reorganization'
        WHEN ac.rn <= 10 THEN 'Customer return in good condition'
        ELSE 'Internal use for company operations'
    END,
    CURRENT_DATE - INTERVAL '10 days' + (ac.rn * INTERVAL '1 day'),
    ac.user_id,
    CURRENT_DATE - INTERVAL '10 days' + (ac.rn * INTERVAL '1 day'),
    CURRENT_DATE - INTERVAL '10 days' + (ac.rn * INTERVAL '1 day')
FROM adjustment_combinations ac;


-- =============================================
-- VERIFICATION
-- =============================================
-- Optional: Run these to verify the data was inserted correctly
SELECT 'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL SELECT 'categories', COUNT(*) FROM categories
UNION ALL SELECT 'suppliers', COUNT(*) FROM suppliers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'product_inventory', COUNT(*) FROM product_inventory
UNION ALL SELECT 'purchase_orders', COUNT(*) FROM purchase_orders
UNION ALL SELECT 'purchase_order_items', COUNT(*) FROM purchase_order_items
UNION ALL SELECT 'stock_movements', COUNT(*) FROM stock_movements
UNION ALL SELECT 'stock_adjustments', COUNT(*) FROM stock_adjustments
ORDER BY table_name;














