-- =============================================
-- INSERT 15 ROWS INTO EACH TABLE
-- Using GENERATED ALWAYS AS IDENTITY - DO NOT specify ID column
-- =============================================

BEGIN TRANSACTION;

-- =============================================
-- 1. USERS (must come first for created_by references)
-- =============================================
INSERT INTO
    users (
        email,
        password_hash,
        full_name,
        role,
        is_active,
        last_login_at
    )
VALUES (
        'admin@inventory.com',
        'hashed_password_1',
        'John Smith',
        'admin',
        true,
        '2024-03-15 09:30:00'
    ),
    (
        'manager1@inventory.com',
        'hashed_password_2',
        'Sarah Johnson',
        'inventory_manager',
        true,
        '2024-03-15 10:15:00'
    ),
    (
        'manager2@inventory.com',
        'hashed_password_3',
        'Michael Chen',
        'inventory_manager',
        true,
        '2024-03-14 14:20:00'
    ),
    (
        'viewer1@inventory.com',
        'hashed_password_4',
        'Emily Davis',
        'viewer',
        true,
        '2024-03-14 11:45:00'
    ),
    (
        'viewer2@inventory.com',
        'hashed_password_5',
        'Robert Wilson',
        'viewer',
        true,
        '2024-03-13 16:30:00'
    ),
    (
        'manager3@inventory.com',
        'hashed_password_6',
        'Lisa Martinez',
        'inventory_manager',
        true,
        '2024-03-13 09:10:00'
    ),
    (
        'admin2@inventory.com',
        'hashed_password_7',
        'David Brown',
        'admin',
        true,
        '2024-03-12 13:25:00'
    ),
    (
        'viewer3@inventory.com',
        'hashed_password_8',
        'Jennifer Lee',
        'viewer',
        true,
        '2024-03-12 15:40:00'
    ),
    (
        'manager4@inventory.com',
        'hashed_password_9',
        'Thomas Anderson',
        'inventory_manager',
        false,
        '2024-02-28 10:00:00'
    ),
    (
        'viewer4@inventory.com',
        'hashed_password_10',
        'Amanda Taylor',
        'viewer',
        true,
        '2024-03-11 11:20:00'
    ),
    (
        'manager5@inventory.com',
        'hashed_password_11',
        'Kevin Rodriguez',
        'inventory_manager',
        true,
        '2024-03-10 14:55:00'
    ),
    (
        'viewer5@inventory.com',
        'hashed_password_12',
        'Jessica White',
        'viewer',
        true,
        '2024-03-09 09:45:00'
    ),
    (
        'admin3@inventory.com',
        'hashed_password_13',
        'Christopher Clark',
        'admin',
        true,
        '2024-03-08 16:10:00'
    ),
    (
        'viewer6@inventory.com',
        'hashed_password_14',
        'Michelle Lewis',
        'viewer',
        false,
        '2024-02-15 10:30:00'
    ),
    (
        'manager6@inventory.com',
        'hashed_password_15',
        'Daniel Walker',
        'inventory_manager',
        true,
        '2024-03-07 13:15:00'
    );

-- =============================================
-- 2. CATEGORIES (parent/child relationships)
-- =============================================
INSERT INTO
    categories (
        name,
        description,
        parent_id,
        is_active
    )
VALUES (
        'Electronics',
        'Electronic devices and components',
        NULL,
        true
    ),
    (
        'Computers',
        'Desktop and laptop computers',
        NULL,
        true
    ),
    (
        'Mobile Phones',
        'Smartphones and feature phones',
        NULL,
        true
    ),
    (
        'Office Supplies',
        'General office supplies',
        NULL,
        true
    ),
    (
        'Stationery',
        'Writing instruments and paper products',
        4,
        true
    ),
    (
        'Furniture',
        'Office furniture and equipment',
        NULL,
        true
    ),
    (
        'Chairs',
        'Office and conference chairs',
        6,
        true
    ),
    (
        'Tables',
        'Desks and conference tables',
        6,
        true
    ),
    (
        'Appliances',
        'Office appliances',
        NULL,
        true
    ),
    (
        'Printers',
        'Printing and scanning devices',
        1,
        true
    ),
    (
        'Networking',
        'Network equipment and accessories',
        1,
        true
    ),
    (
        'Software',
        'Software licenses and applications',
        NULL,
        true
    ),
    (
        'Operating Systems',
        'OS licenses and software',
        12,
        true
    ),
    (
        'Productivity',
        'Office productivity software',
        12,
        true
    ),
    (
        'Storage',
        'Data storage devices',
        1,
        true
    );

-- Note: We need to fix parent_id references after insertion
-- Since IDs are generated, we'll update the parent_id references
UPDATE categories
SET
    parent_id = 1
WHERE
    name IN (
        'Computers',
        'Mobile Phones',
        'Printers',
        'Networking',
        'Storage'
    );

UPDATE categories
SET
    parent_id = 6
WHERE
    name IN ('Chairs', 'Tables');

UPDATE categories SET parent_id = 4 WHERE name = 'Stationery';

UPDATE categories
SET
    parent_id = 12
WHERE
    name IN (
        'Operating Systems',
        'Productivity'
    );

-- =============================================
-- 3. SUPPLIERS (must come before products)
-- =============================================
INSERT INTO
    suppliers (
        name,
        contact_person_name,
        contact_email,
        contact_phone,
        address_line1,
        city,
        state,
        postal_code,
        country,
        is_active
    )
VALUES (
        'TechCorp Inc.',
        'Alex Johnson',
        'alex@techcorp.com',
        '+1-555-0101',
        '123 Tech Street',
        'San Francisco',
        'CA',
        '94105',
        'USA',
        true
    ),
    (
        'Global Electronics',
        'Maria Garcia',
        'maria@globalelec.com',
        '+1-555-0102',
        '456 Circuit Ave',
        'Austin',
        'TX',
        '73301',
        'USA',
        true
    ),
    (
        'OfficePlus Ltd.',
        'David Wilson',
        'david@officeplus.com',
        '+1-555-0103',
        '789 Business Blvd',
        'Chicago',
        'IL',
        '60601',
        'USA',
        true
    ),
    (
        'Furniture World',
        'Sarah Miller',
        'sarah@furnitureworld.com',
        '+1-555-0104',
        '321 Design Drive',
        'Miami',
        'FL',
        '33101',
        'USA',
        true
    ),
    (
        'PrintMaster Co.',
        'James Brown',
        'james@printmaster.com',
        '+1-555-0105',
        '654 Ink Road',
        'Denver',
        'CO',
        '80201',
        'USA',
        true
    ),
    (
        'NetSolutions',
        'Linda Davis',
        'linda@netsolutions.com',
        '+1-555-0106',
        '987 Network Lane',
        'Seattle',
        'WA',
        '98101',
        'USA',
        true
    ),
    (
        'SoftwareHub',
        'Robert Taylor',
        'robert@softwarehub.com',
        '+1-555-0107',
        '147 Code Street',
        'Boston',
        'MA',
        '02101',
        'USA',
        true
    ),
    (
        'ElectroParts',
        'Patricia Lee',
        'patricia@electroparts.com',
        '+1-555-0108',
        '258 Component Ct',
        'Atlanta',
        'GA',
        '30301',
        'USA',
        true
    ),
    (
        'SupplyChain Pro',
        'Michael Clark',
        'michael@supplypro.com',
        '+1-555-0109',
        '369 Logistic Way',
        'Dallas',
        'TX',
        '75201',
        'USA',
        true
    ),
    (
        'Quality Goods Co.',
        'Jennifer Hall',
        'jennifer@qualitygoods.com',
        '+1-555-0110',
        '741 Quality Ave',
        'Phoenix',
        'AZ',
        '85001',
        'USA',
        true
    ),
    (
        'Innovative Tech',
        'William Allen',
        'william@innotech.com',
        '+1-555-0111',
        '852 Innovation Dr',
        'San Diego',
        'CA',
        '92101',
        'USA',
        true
    ),
    (
        'Mega Suppliers',
        'Elizabeth Scott',
        'elizabeth@megasuppliers.com',
        '+1-555-0112',
        '963 Mega Plaza',
        'Houston',
        'TX',
        '77001',
        'USA',
        true
    ),
    (
        'Reliable Office',
        'Charles Young',
        'charles@reliableoffice.com',
        '+1-555-0113',
        '159 Dependable St',
        'Philadelphia',
        'PA',
        '19101',
        'USA',
        true
    ),
    (
        'Tech Innovators',
        'Karen King',
        'karen@techinnovators.com',
        '+1-555-0114',
        '357 Future Rd',
        'Portland',
        'OR',
        '97201',
        'USA',
        true
    ),
    (
        'Direct Source',
        'Brian Wright',
        'brian@directsource.com',
        '+1-555-0115',
        '753 Supply Line',
        'Las Vegas',
        'NV',
        '89101',
        'USA',
        true
    );

-- =============================================
-- 4. PRODUCTS (references categories and suppliers)
-- We need to get actual IDs for category_id and supplier_id
-- =============================================
INSERT INTO
    products (
        sku,
        name,
        description,
        category_id,
        supplier_id,
        price,
        cost_price,
        low_stock_threshold,
        reorder_point,
        reorder_quantity,
        expiry_date,
        barcode_data,
        is_active
    )
VALUES (
        'LAP-001',
        'Business Laptop Pro',
        'High-performance business laptop',
        (
            SELECT id
            FROM categories
            WHERE
                name = 'Computers'
        ),
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'TechCorp Inc.'
        ),
        1299.99,
        950.00,
        5,
        10,
        25,
        NULL,
        '8901234567890',
        true
    ),
    (
        'PHN-001',
        'SmartPhone X',
        'Latest smartphone model',
        (
            SELECT id
            FROM categories
            WHERE
                name = 'Mobile Phones'
        ),
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'Global Electronics'
        ),
        899.99,
        650.00,
        8,
        15,
        30,
        '2026-12-31',
        '8901234567891',
        true
    ),
    (
        'PEN-001',
        'Premium Ballpoint Pen',
        'Executive ballpoint pen set',
        (
            SELECT id
            FROM categories
            WHERE
                name = 'Stationery'
        ),
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'OfficePlus Ltd.'
        ),
        24.99,
        12.50,
        50,
        100,
        200,
        NULL,
        '8901234567892',
        true
    ),
    (
        'CHA-001',
        'Ergonomic Office Chair',
        'Adjustable ergonomic office chair',
        (
            SELECT id
            FROM categories
            WHERE
                name = 'Chairs'
        ),
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'Furniture World'
        ),
        299.99,
        180.00,
        3,
        6,
        12,
        NULL,
        '8901234567893',
        true
    ),
    (
        'PRT-001',
        'Color Laser Printer',
        'Office color laser printer',
        (
            SELECT id
            FROM categories
            WHERE
                name = 'Printers'
        ),
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'PrintMaster Co.'
        ),
        499.99,
        320.00,
        2,
        5,
        10,
        NULL,
        '8901234567894',
        true
    ),
    (
        'ROU-001',
        'WiFi 6 Router',
        'High-speed wireless router',
        (
            SELECT id
            FROM categories
            WHERE
                name = 'Networking'
        ),
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'NetSolutions'
        ),
        199.99,
        130.00,
        6,
        12,
        24,
        NULL,
        '8901234567895',
        true
    ),
    (
        'SW-001',
        'Office Suite Pro',
        'Productivity software suite',
        (
            SELECT id
            FROM categories
            WHERE
                name = 'Productivity'
        ),
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'SoftwareHub'
        ),
        249.99,
        150.00,
        10,
        20,
        40,
        '2027-06-30',
        '8901234567896',
        true
    ),
    (
        'HDD-001',
        'External SSD 1TB',
        'Portable solid state drive',
        (
            SELECT id
            FROM categories
            WHERE
                name = 'Storage'
        ),
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'ElectroParts'
        ),
        129.99,
        85.00,
        7,
        14,
        28,
        NULL,
        '8901234567897',
        true
    ),
    (
        'TAB-001',
        'Conference Table',
        'Large conference room table',
        (
            SELECT id
            FROM categories
            WHERE
                name = 'Tables'
        ),
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'Furniture World'
        ),
        899.99,
        550.00,
        1,
        2,
        4,
        NULL,
        '8901234567898',
        true
    ),
    (
        'MON-001',
        '27" 4K Monitor',
        'Ultra HD computer monitor',
        (
            SELECT id
            FROM categories
            WHERE
                name = 'Computers'
        ),
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'TechCorp Inc.'
        ),
        399.99,
        280.00,
        4,
        8,
        16,
        NULL,
        '8901234567899',
        true
    ),
    (
        'KEY-001',
        'Wireless Keyboard',
        'Ergonomic wireless keyboard',
        (
            SELECT id
            FROM categories
            WHERE
                name = 'Computers'
        ),
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'SupplyChain Pro'
        ),
        79.99,
        45.00,
        12,
        25,
        50,
        NULL,
        '8901234567900',
        true
    ),
    (
        'BAT-001',
        'Laptop Battery',
        'Replacement laptop battery',
        (
            SELECT id
            FROM categories
            WHERE
                name = 'Computers'
        ),
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'Quality Goods Co.'
        ),
        89.99,
        55.00,
        9,
        18,
        36,
        '2025-09-30',
        '8901234567901',
        true
    ),
    (
        'CAB-001',
        'USB-C Cable Pack',
        'Multi-pack of USB-C cables',
        (
            SELECT id
            FROM categories
            WHERE
                name = 'Electronics'
        ),
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'Innovative Tech'
        ),
        29.99,
        15.00,
        20,
        40,
        80,
        NULL,
        '8901234567902',
        true
    ),
    (
        'LAM-001',
        'Desk Lamp LED',
        'Energy-efficient LED desk lamp',
        (
            SELECT id
            FROM categories
            WHERE
                name = 'Appliances'
        ),
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'Mega Suppliers'
        ),
        49.99,
        28.00,
        8,
        16,
        32,
        NULL,
        '8901234567903',
        true
    ),
    (
        'STP-001',
        'Stapler Heavy Duty',
        'Heavy-duty office stapler',
        (
            SELECT id
            FROM categories
            WHERE
                name = 'Stationery'
        ),
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'Reliable Office'
        ),
        19.99,
        10.00,
        15,
        30,
        60,
        NULL,
        '8901234567904',
        true
    );

-- =============================================
-- 5. PRODUCT_INVENTORY (references products)
-- =============================================
INSERT INTO
    product_inventory (
        product_id,
        quantity_on_hand,
        quantity_committed,
        quantity_available,
        last_restocked_at,
        last_counted_at
    )
VALUES (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'LAP-001'
        ),
        25,
        3,
        22,
        '2024-03-10 14:30:00',
        '2024-03-14 09:00:00'
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'PHN-001'
        ),
        42,
        8,
        34,
        '2024-03-12 10:15:00',
        '2024-03-14 09:00:00'
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'PEN-001'
        ),
        187,
        12,
        175,
        '2024-03-05 11:45:00',
        '2024-03-07 14:20:00'
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'CHA-001'
        ),
        8,
        1,
        7,
        '2024-03-01 13:20:00',
        '2024-03-14 09:00:00'
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'PRT-001'
        ),
        7,
        0,
        7,
        '2024-02-28 15:30:00',
        '2024-03-10 16:00:00'
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'ROU-001'
        ),
        31,
        5,
        26,
        '2024-03-08 09:45:00',
        '2024-03-14 09:00:00'
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'SW-001'
        ),
        52,
        7,
        45,
        '2024-03-11 16:20:00',
        '2024-03-14 09:00:00'
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'HDD-001'
        ),
        28,
        3,
        25,
        '2024-03-06 14:10:00',
        '2024-03-13 10:30:00'
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'TAB-001'
        ),
        3,
        0,
        3,
        '2024-02-25 11:00:00',
        '2024-03-14 09:00:00'
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'MON-001'
        ),
        15,
        2,
        13,
        '2024-03-09 10:30:00',
        '2024-03-14 09:00:00'
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'KEY-001'
        ),
        67,
        9,
        58,
        '2024-03-04 13:45:00',
        '2024-03-12 15:00:00'
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'BAT-001'
        ),
        22,
        4,
        18,
        '2024-03-07 15:20:00',
        '2024-03-14 09:00:00'
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'CAB-001'
        ),
        125,
        15,
        110,
        '2024-03-13 11:30:00',
        '2024-03-14 09:00:00'
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'LAM-001'
        ),
        40,
        6,
        34,
        '2024-03-02 09:15:00',
        '2024-03-08 14:00:00'
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'STP-001'
        ),
        92,
        11,
        81,
        '2024-03-14 08:45:00',
        '2024-03-14 09:00:00'
    );

-- =============================================
-- 6. PURCHASE_ORDERS (references suppliers and users)
-- =============================================
INSERT INTO
    purchase_orders (
        po_number,
        supplier_id,
        status,
        total_amount,
        ordered_date,
        expected_delivery_date,
        received_date,
        created_by
    )
VALUES (
        'PO-2024-001',
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'TechCorp Inc.'
        ),
        'received',
        32499.75,
        '2024-02-01 09:00:00',
        '2024-02-10 09:00:00',
        '2024-02-09 14:30:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'admin@inventory.com'
        )
    ),
    (
        'PO-2024-002',
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'Global Electronics'
        ),
        'received',
        26999.70,
        '2024-02-05 10:15:00',
        '2024-02-15 09:00:00',
        '2024-02-14 11:20:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager1@inventory.com'
        )
    ),
    (
        'PO-2024-003',
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'OfficePlus Ltd.'
        ),
        'ordered',
        2499.80,
        '2024-03-01 14:30:00',
        '2024-03-15 09:00:00',
        NULL,
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager2@inventory.com'
        )
    ),
    (
        'PO-2024-004',
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'Furniture World'
        ),
        'received',
        8999.85,
        '2024-02-15 11:45:00',
        '2024-02-25 09:00:00',
        '2024-02-24 16:10:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer1@inventory.com'
        )
    ),
    (
        'PO-2024-005',
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'PrintMaster Co.'
        ),
        'draft',
        1999.96,
        '2024-03-10 13:20:00',
        '2024-03-25 09:00:00',
        NULL,
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer2@inventory.com'
        )
    ),
    (
        'PO-2024-006',
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'NetSolutions'
        ),
        'ordered',
        5999.76,
        '2024-03-05 15:30:00',
        '2024-03-20 09:00:00',
        NULL,
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager3@inventory.com'
        )
    ),
    (
        'PO-2024-007',
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'SoftwareHub'
        ),
        'received',
        7499.70,
        '2024-02-20 09:45:00',
        '2024-03-01 09:00:00',
        '2024-02-29 10:45:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'admin2@inventory.com'
        )
    ),
    (
        'PO-2024-008',
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'ElectroParts'
        ),
        'cancelled',
        2599.86,
        '2024-02-25 16:20:00',
        '2024-03-07 09:00:00',
        NULL,
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer3@inventory.com'
        )
    ),
    (
        'PO-2024-009',
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'SupplyChain Pro'
        ),
        'ordered',
        1599.80,
        '2024-03-08 14:10:00',
        '2024-03-22 09:00:00',
        NULL,
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager4@inventory.com'
        )
    ),
    (
        'PO-2024-010',
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'Quality Goods Co.'
        ),
        'received',
        1799.82,
        '2024-02-28 11:00:00',
        '2024-03-10 09:00:00',
        '2024-03-09 13:15:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer4@inventory.com'
        )
    ),
    (
        'PO-2024-011',
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'Innovative Tech'
        ),
        'draft',
        899.85,
        '2024-03-12 10:30:00',
        '2024-03-27 09:00:00',
        NULL,
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager5@inventory.com'
        )
    ),
    (
        'PO-2024-012',
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'Mega Suppliers'
        ),
        'ordered',
        999.75,
        '2024-03-07 13:45:00',
        '2024-03-21 09:00:00',
        NULL,
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer5@inventory.com'
        )
    ),
    (
        'PO-2024-013',
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'Reliable Office'
        ),
        'received',
        399.80,
        '2024-03-03 15:20:00',
        '2024-03-13 09:00:00',
        '2024-03-12 14:40:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'admin3@inventory.com'
        )
    ),
    (
        'PO-2024-014',
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'Tech Innovators'
        ),
        'ordered',
        2999.70,
        '2024-03-09 11:30:00',
        '2024-03-23 09:00:00',
        NULL,
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer6@inventory.com'
        )
    ),
    (
        'PO-2024-015',
        (
            SELECT id
            FROM suppliers
            WHERE
                name = 'Direct Source'
        ),
        'draft',
        499.75,
        '2024-03-14 09:15:00',
        '2024-03-28 09:00:00',
        NULL,
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager6@inventory.com'
        )
    );

-- =============================================
-- 7. PURCHASE_ORDER_ITEMS (references POs and products)
-- =============================================
INSERT INTO
    purchase_order_items (
        purchase_order_id,
        product_id,
        quantity_ordered,
        quantity_received,
        unit_cost,
        line_total
    )
VALUES (
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-001'
        ),
        (
            SELECT id
            FROM products
            WHERE
                sku = 'LAP-001'
        ),
        25,
        25,
        950.00,
        23750.00
    ),
    (
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-001'
        ),
        (
            SELECT id
            FROM products
            WHERE
                sku = 'MON-001'
        ),
        15,
        15,
        280.00,
        4200.00
    ),
    (
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-002'
        ),
        (
            SELECT id
            FROM products
            WHERE
                sku = 'PHN-001'
        ),
        30,
        30,
        650.00,
        19500.00
    ),
    (
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-002'
        ),
        (
            SELECT id
            FROM products
            WHERE
                sku = 'BAT-001'
        ),
        18,
        18,
        55.00,
        990.00
    ),
    (
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-003'
        ),
        (
            SELECT id
            FROM products
            WHERE
                sku = 'PEN-001'
        ),
        100,
        0,
        12.50,
        1250.00
    ),
    (
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-003'
        ),
        (
            SELECT id
            FROM products
            WHERE
                sku = 'STP-001'
        ),
        60,
        0,
        10.00,
        600.00
    ),
    (
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-004'
        ),
        (
            SELECT id
            FROM products
            WHERE
                sku = 'CHA-001'
        ),
        12,
        12,
        180.00,
        2160.00
    ),
    (
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-004'
        ),
        (
            SELECT id
            FROM products
            WHERE
                sku = 'TAB-001'
        ),
        4,
        4,
        550.00,
        2200.00
    ),
    (
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-005'
        ),
        (
            SELECT id
            FROM products
            WHERE
                sku = 'PRT-001'
        ),
        5,
        0,
        320.00,
        1600.00
    ),
    (
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-006'
        ),
        (
            SELECT id
            FROM products
            WHERE
                sku = 'ROU-001'
        ),
        24,
        0,
        130.00,
        3120.00
    ),
    (
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-006'
        ),
        (
            SELECT id
            FROM products
            WHERE
                sku = 'KEY-001'
        ),
        50,
        0,
        45.00,
        2250.00
    ),
    (
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-007'
        ),
        (
            SELECT id
            FROM products
            WHERE
                sku = 'SW-001'
        ),
        40,
        40,
        150.00,
        6000.00
    ),
    (
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-008'
        ),
        (
            SELECT id
            FROM products
            WHERE
                sku = 'HDD-001'
        ),
        28,
        0,
        85.00,
        2380.00
    ),
    (
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-009'
        ),
        (
            SELECT id
            FROM products
            WHERE
                sku = 'CAB-001'
        ),
        80,
        0,
        15.00,
        1200.00
    ),
    (
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-010'
        ),
        (
            SELECT id
            FROM products
            WHERE
                sku = 'LAM-001'
        ),
        32,
        32,
        28.00,
        896.00
    );

-- =============================================
-- 8. STOCK_MOVEMENTS (references products and users)
-- =============================================
INSERT INTO
    stock_movements (
        product_id,
        movement_type,
        quantity_change,
        quantity_before,
        quantity_after,
        reference_type,
        reference_id,
        movement_date,
        created_by
    )
VALUES (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'LAP-001'
        ),
        'in',
        25,
        0,
        25,
        'purchase_order',
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-001'
        ),
        '2024-02-09 14:30:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'admin@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'LAP-001'
        ),
        'out',
        3,
        25,
        22,
        'sale',
        101,
        '2024-03-11 10:30:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager2@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'PHN-001'
        ),
        'in',
        30,
        0,
        30,
        'purchase_order',
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-002'
        ),
        '2024-02-14 11:20:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager1@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'PHN-001'
        ),
        'out',
        5,
        30,
        25,
        'sale',
        102,
        '2024-03-05 14:15:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer1@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'PEN-001'
        ),
        'in',
        50,
        0,
        50,
        'adjustment',
        1,
        '2024-02-20 09:00:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer2@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'CHA-001'
        ),
        'in',
        12,
        0,
        12,
        'purchase_order',
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-004'
        ),
        '2024-02-24 16:10:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager3@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'PRT-001'
        ),
        'in',
        7,
        0,
        7,
        'purchase_order',
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-007'
        ),
        '2024-02-29 10:45:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'admin2@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'ROU-001'
        ),
        'out',
        2,
        28,
        26,
        'sale',
        103,
        '2024-03-08 11:45:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer3@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'SW-001'
        ),
        'in',
        40,
        0,
        40,
        'purchase_order',
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-007'
        ),
        '2024-02-29 10:45:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager4@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'HDD-001'
        ),
        'out',
        1,
        26,
        25,
        'adjustment',
        2,
        '2024-03-10 15:30:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer4@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'TAB-001'
        ),
        'in',
        3,
        0,
        3,
        'purchase_order',
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-004'
        ),
        '2024-02-24 16:10:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager5@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'MON-001'
        ),
        'in',
        15,
        0,
        15,
        'purchase_order',
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-001'
        ),
        '2024-02-09 14:30:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer5@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'KEY-001'
        ),
        'in',
        67,
        0,
        67,
        'transfer',
        1,
        '2024-03-04 13:45:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'admin3@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'BAT-001'
        ),
        'out',
        4,
        22,
        18,
        'sale',
        104,
        '2024-03-12 16:20:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer6@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'CAB-001'
        ),
        'in',
        125,
        0,
        125,
        'purchase_order',
        (
            SELECT id
            FROM purchase_orders
            WHERE
                po_number = 'PO-2024-013'
        ),
        '2024-03-12 14:40:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager6@inventory.com'
        )
    );

-- =============================================
-- 9. STOCK_ADJUSTMENTS (references products and users)
-- =============================================
INSERT INTO
    stock_adjustments (
        product_id,
        adjustment_type,
        quantity_adjusted,
        reason,
        adjustment_date,
        created_by
    )
VALUES (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'LAP-001'
        ),
        'damaged',
        2,
        'Screen cracked during handling',
        '2024-03-01 10:15:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager1@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'PHN-001'
        ),
        'theft',
        1,
        'Missing from inventory count',
        '2024-03-05 14:30:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager2@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'PEN-001'
        ),
        'expired',
        5,
        'Ink dried out, past shelf life',
        '2024-03-02 11:45:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer1@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'CHA-001'
        ),
        'internal_use',
        1,
        'Used in office renovation',
        '2024-03-03 09:20:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer2@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'PRT-001'
        ),
        'found',
        2,
        'Found in warehouse miscount',
        '2024-03-04 15:10:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager3@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'ROU-001'
        ),
        'damaged',
        3,
        'Power supply units defective',
        '2024-03-06 13:25:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'admin2@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'SW-001'
        ),
        'returned',
        4,
        'Customer returns, damaged packaging',
        '2024-03-07 16:40:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer3@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'HDD-001'
        ),
        'theft',
        2,
        'Security incident reported',
        '2024-03-08 10:55:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager4@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'TAB-001'
        ),
        'internal_use',
        1,
        'Used in conference room setup',
        '2024-03-09 14:15:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer4@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'MON-001'
        ),
        'damaged',
        1,
        'Monitor screen broken in transit',
        '2024-03-10 11:30:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager5@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'KEY-001'
        ),
        'found',
        3,
        'Additional stock discovered in storage',
        '2024-03-11 15:45:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer5@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'BAT-001'
        ),
        'expired',
        6,
        'Batteries past expiration date',
        '2024-03-12 09:10:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'admin3@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'CAB-001'
        ),
        'theft',
        5,
        'Missing from shipping area',
        '2024-03-13 13:20:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'viewer6@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'LAM-001'
        ),
        'damaged',
        2,
        'LED lights malfunctioning',
        '2024-03-14 16:35:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'manager6@inventory.com'
        )
    ),
    (
        (
            SELECT id
            FROM products
            WHERE
                sku = 'STP-001'
        ),
        'internal_use',
        4,
        'Used by office staff',
        '2024-03-14 10:50:00',
        (
            SELECT id
            FROM users
            WHERE
                email = 'admin@inventory.com'
        )
    );

COMMIT;

-- =============================================
-- VERIFICATION
-- =============================================
-- Optional: Run these to verify the data was inserted correctly
/*
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

*/