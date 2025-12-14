-- =============================================
-- CORE USER AND AUTHENTICATION TABLES
-- =============================================
CREATE TABLE users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (
        role IN (
            'admin',
            'inventory_manager',
            'viewer'
        )
    ),
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User indexes
CREATE UNIQUE INDEX idx_user_email ON users (email);

CREATE INDEX idx_user_role ON users (role);

CREATE INDEX idx_active_users ON users (is_active)
WHERE
    is_active;

CREATE INDEX idx_full_name ON users (full_name);

CREATE INDEX idx_role_active_status ON users (role, is_active);

CREATE INDEX idx_active_recent_login ON users (is_active, last_login_at);

CREATE INDEX idx_last_login ON users (last_login_at);

CREATE INDEX idx_created_at ON users (created_at);

CREATE INDEX idx_updated_at ON users (updated_at);

CREATE INDEX idx_user_onboarding ON users (created_at, is_active);

CREATE INDEX idx_role_growth_trends ON users (role, created_at);

CREATE INDEX idx_user_engagement ON users (
    is_active,
    role,
    last_login_at
);

-- =============================================
-- CORE BUSINESS ENTITY TABLES
-- =============================================
CREATE TABLE categories (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    parent_id BIGINT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Category indexes
CREATE UNIQUE INDEX idx_categories_name ON categories (name);

CREATE INDEX idx_categories_parent ON categories (parent_id);

CREATE INDEX idx_categories_active ON categories (is_active)
WHERE
    is_active;

CREATE TABLE suppliers (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    contact_person_name VARCHAR(255),
    contact_email VARCHAR(255) NOT NULL UNIQUE,
    contact_phone VARCHAR(50),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Supplier indexes
CREATE INDEX idx_suppliers_name ON suppliers (name);

CREATE INDEX idx_suppliers_email ON suppliers (contact_email);

CREATE INDEX idx_suppliers_phone ON suppliers (contact_phone);

CREATE INDEX idx_suppliers_country ON suppliers (country);

CREATE INDEX idx_suppliers_state_city ON suppliers (state, city);

CREATE INDEX idx_suppliers_city ON suppliers (city);

CREATE INDEX idx_suppliers_postal ON suppliers (postal_code);

CREATE INDEX idx_suppliers_active ON suppliers (is_active)
WHERE
    is_active;

CREATE INDEX idx_suppliers_active_region ON suppliers (is_active, country, state);

CREATE INDEX idx_suppliers_created ON suppliers (created_at);

CREATE INDEX idx_suppliers_updated ON suppliers (updated_at);

CREATE TABLE products (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    cost_price DECIMAL(10, 2),
    low_stock_threshold INTEGER DEFAULT 1,
    reorder_point INTEGER DEFAULT 0,
    reorder_quantity INTEGER DEFAULT 10,
    expiry_date DATE,
    barcode_data VARCHAR(255),
    qr_code_data TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product indexes
CREATE UNIQUE INDEX idx_products_sku ON products (sku);

CREATE INDEX idx_products_name ON products (name);

CREATE INDEX idx_products_category ON products (category_id);

CREATE INDEX idx_products_supplier ON products (supplier_id);

CREATE INDEX idx_products_active ON products (is_active)
WHERE
    is_active;

CREATE INDEX idx_products_low_stock ON products (low_stock_threshold);

CREATE INDEX idx_products_reorder ON products (reorder_point);

CREATE INDEX idx_products_price ON products (price);

CREATE INDEX idx_products_cost ON products (cost_price);

CREATE INDEX idx_products_expiry ON products (expiry_date);

CREATE INDEX idx_products_barcode ON products (barcode_data);

CREATE INDEX idx_products_active_category ON products (is_active, category_id);

CREATE INDEX idx_products_active_supplier ON products (is_active, supplier_id);

CREATE INDEX idx_products_category_price ON products (category_id, price);

CREATE INDEX idx_products_active_low_stock ON products (
    is_active,
    low_stock_threshold
);

CREATE INDEX idx_products_created ON products (created_at);

CREATE INDEX idx_products_updated ON products (updated_at);

-- =============================================
-- INVENTORY TRACKING TABLES
-- =============================================
CREATE TABLE product_inventory (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL UNIQUE,
    quantity_on_hand INTEGER NOT NULL DEFAULT 0,
    --Counted in warehouse
    quantity_committed INTEGER DEFAULT 0,
    --Reserved for pending orders
    quantity_available INTEGER NOT NULL DEFAULT 0,
    -- Ready to be selled  = On hand - Committed
    last_restocked_at TIMESTAMP,
    --  Date of last incoming stock
    last_counted_at TIMESTAMP,
    -- Date of last physical count/audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product inventory indexes
CREATE UNIQUE INDEX idx_product_inventory_product ON product_inventory (product_id);

CREATE INDEX idx_available_quantity ON product_inventory (quantity_available);

CREATE INDEX idx_on_hand_quantity ON product_inventory (quantity_on_hand);

CREATE INDEX idx_restock_date ON product_inventory (last_restocked_at);

CREATE INDEX idx_count_date ON product_inventory (last_counted_at);

CREATE INDEX idx_available_restocked ON product_inventory (
    quantity_available,
    last_restocked_at
);

CREATE INDEX idx_on_hand_counted ON product_inventory (
    quantity_on_hand,
    last_counted_at
);

CREATE INDEX idx_low_stock_check ON product_inventory (
    quantity_available,
    product_id
);

CREATE INDEX idx_inventory_aging ON product_inventory (
    last_restocked_at,
    quantity_on_hand
);

CREATE TABLE purchase_orders (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    po_number VARCHAR(100) NOT NULL UNIQUE,
    supplier_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (
        status IN (
            'draft',
            'ordered',
            'received',
            'cancelled'
        )
    ) DEFAULT 'draft',
    total_amount DECIMAL(10, 2),
    ordered_date TIMESTAMP,
    expected_delivery_date TIMESTAMP,
    received_date TIMESTAMP,
    created_by BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Purchase order indexes
CREATE UNIQUE INDEX idx_po_number ON purchase_orders (po_number);

CREATE INDEX idx_supplier_id ON purchase_orders (supplier_id);

CREATE INDEX idx_created_by ON purchase_orders (created_by);

CREATE INDEX idx_po_status ON purchase_orders (status);

CREATE INDEX idx_ordered_date ON purchase_orders (ordered_date);

CREATE INDEX idx_expected_delivery ON purchase_orders (expected_delivery_date);

CREATE INDEX idx_received_date ON purchase_orders (received_date);

CREATE INDEX idx_po_created_at ON purchase_orders (created_at);

CREATE INDEX idx_status_delivery ON purchase_orders (
    status,
    expected_delivery_date
);

CREATE INDEX idx_supplier_status ON purchase_orders (supplier_id, status);

CREATE INDEX idx_status_ordered_date ON purchase_orders (status, ordered_date);

CREATE INDEX idx_total_amount ON purchase_orders (total_amount);

CREATE INDEX idx_status_amount ON purchase_orders (status, total_amount);

CREATE INDEX idx_pending_deliveries ON purchase_orders (
    expected_delivery_date,
    status
);

CREATE INDEX idx_date_amount_analysis ON purchase_orders (ordered_date, total_amount);

CREATE TABLE purchase_order_items (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    purchase_order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity_ordered INTEGER NOT NULL,
    quantity_received INTEGER DEFAULT 0,
    unit_cost DECIMAL(10, 2) NOT NULL,
    line_total DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (purchase_order_id, product_id)
);

-- Purchase order item indexes
CREATE INDEX idx_po_id ON purchase_order_items (purchase_order_id);

CREATE INDEX idx_product_id ON purchase_order_items (product_id);

CREATE UNIQUE INDEX idx_po_product ON purchase_order_items (purchase_order_id, product_id);

CREATE INDEX idx_quantity_ordered ON purchase_order_items (quantity_ordered);

CREATE INDEX idx_quantity_received ON purchase_order_items (quantity_received);

CREATE INDEX idx_unit_cost ON purchase_order_items (unit_cost);

CREATE INDEX idx_line_total ON purchase_order_items (line_total);

CREATE INDEX idx_po_receipt_status ON purchase_order_items (
    purchase_order_id,
    quantity_received
);

CREATE INDEX idx_product_pricing ON purchase_order_items (product_id, unit_cost);

CREATE INDEX idx_po_line_totals ON purchase_order_items (purchase_order_id, line_total);

CREATE INDEX idx_receipt_comparison ON purchase_order_items (
    quantity_ordered,
    quantity_received
);

CREATE INDEX idx_product_purchase_history ON purchase_order_items (product_id, created_at);

CREATE INDEX idx_product_spend ON purchase_order_items (product_id, line_total);

CREATE INDEX idx_po_product_qty ON purchase_order_items (
    purchase_order_id,
    product_id,
    quantity_ordered
);

CREATE INDEX idx_partial_receipts ON purchase_order_items (
    purchase_order_id,
    quantity_ordered,
    quantity_received
);

-- =============================================
-- STOCK MOVEMENT AND TRANSACTION TABLES
-- =============================================
CREATE TABLE stock_movements (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL,
    movement_type VARCHAR(20) NOT NULL CHECK (
        movement_type IN ('in', 'out', 'adjustment')
    ),
    quantity_change INTEGER NOT NULL,
    -- How much moved?
    quantity_before INTEGER NOT NULL,
    -- Inventory level BEFORE the movement(product_inventory.quantity_available)
    quantity_after INTEGER NOT NULL,
    -- Inventory level AFTER the movement
    reference_type VARCHAR(20) NOT NULL CHECK (
        reference_type IN (
            'purchase_order',
            'sale',
            'adjustment',
            'transfer'
        )
    ),
    reference_id BIGINT,
    -- reference to specific item with in reference_type
    movement_date TIMESTAMP NOT NULL,
    created_by BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stock movement indexes
CREATE INDEX idx_stock_product_id ON stock_movements (product_id);

CREATE INDEX idx_stock_created_by ON stock_movements (created_by);

CREATE INDEX idx_product_movement_history ON stock_movements (product_id, movement_date);

CREATE INDEX idx_product_movement_type_history ON stock_movements (
    product_id,
    movement_type,
    movement_date
);

CREATE INDEX idx_movement_type ON stock_movements (movement_type);

CREATE INDEX idx_movement_date ON stock_movements (movement_date);

CREATE INDEX idx_movement_created_at ON stock_movements (created_at);

CREATE INDEX idx_reference_lookup ON stock_movements (reference_type, reference_id);

CREATE INDEX idx_reference_product ON stock_movements (reference_type, product_id);

CREATE INDEX idx_quantity_after ON stock_movements (quantity_after);

CREATE INDEX idx_quantity_before ON stock_movements (quantity_before);

CREATE INDEX idx_product_movement_impact ON stock_movements (
    product_id,
    movement_type,
    quantity_change
);

CREATE INDEX idx_daily_movement_summary ON stock_movements (movement_date, movement_type);

CREATE INDEX idx_quantity_change ON stock_movements (quantity_change);

CREATE INDEX idx_user_activity ON stock_movements (created_by, movement_date);

CREATE INDEX idx_product_stock_timeline ON stock_movements (
    product_id,
    movement_date,
    quantity_after
);

CREATE TABLE stock_adjustments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id INTEGER NOT NULL,
    adjustment_type VARCHAR(20) NOT NULL CHECK (
        adjustment_type IN (
            'damaged',
            'expired',
            'returned',
            'found',
            'theft',
            'internal_use'
        )
    ),
    quantity_adjusted INTEGER NOT NULL,
    reason TEXT,
    adjustment_date TIMESTAMP NOT NULL,
    created_by BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stock adjustment indexes
CREATE INDEX idx_adjustment_product_id ON stock_adjustments (product_id);

CREATE INDEX idx_adjustment_created_by ON stock_adjustments (created_by);

CREATE INDEX idx_adjustment_type ON stock_adjustments (adjustment_type);

CREATE INDEX idx_adjustment_date ON stock_adjustments (adjustment_date);

CREATE INDEX idx_created_at_adj ON stock_adjustments (created_at);

CREATE INDEX idx_quantity_adjusted ON stock_adjustments (quantity_adjusted);

CREATE INDEX idx_product_adjustment_history ON stock_adjustments (product_id, adjustment_date);

CREATE INDEX idx_type_adjustment_trends ON stock_adjustments (
    adjustment_type,
    adjustment_date
);

CREATE INDEX idx_product_adjustment_patterns ON stock_adjustments (product_id, adjustment_type);

CREATE INDEX idx_large_adjustments ON stock_adjustments (
    quantity_adjusted,
    adjustment_date
);

CREATE INDEX idx_loss_analysis ON stock_adjustments (
    adjustment_type,
    quantity_adjusted
);

CREATE INDEX idx_user_adjustments ON stock_adjustments (created_by, adjustment_date);

CREATE INDEX idx_monthly_adjustment_report ON stock_adjustments (
    adjustment_date,
    adjustment_type,
    quantity_adjusted
);

CREATE INDEX idx_product_adjustment_analysis ON stock_adjustments (
    product_id,
    adjustment_type,
    adjustment_date
);

-- =============================================
-- FOREIGN KEY CONSTRAINTS
-- =============================================
-- Product Catalog Relationships
ALTER TABLE products
ADD CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE RESTRICT;

ALTER TABLE products
ADD CONSTRAINT fk_products_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers (id) ON DELETE RESTRICT;

-- Hierarchical Categories Relationship
ALTER TABLE categories
ADD CONSTRAINT fk_categories_parent FOREIGN KEY (parent_id) REFERENCES categories (id) ON DELETE RESTRICT;

-- Inventory Management Relationships
ALTER TABLE product_inventory
ADD CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT;

ALTER TABLE purchase_orders
ADD CONSTRAINT fk_po_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers (id) ON DELETE RESTRICT;

ALTER TABLE purchase_orders
ADD CONSTRAINT fk_po_created_by FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE RESTRICT;

ALTER TABLE purchase_order_items
ADD CONSTRAINT fk_po_items_po FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders (id) ON DELETE RESTRICT;

ALTER TABLE purchase_order_items
ADD CONSTRAINT fk_po_items_product FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT;

-- Stock Movement Relationships
ALTER TABLE stock_movements
ADD CONSTRAINT fk_movements_product FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT;

ALTER TABLE stock_movements
ADD CONSTRAINT fk_movements_created_by FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE RESTRICT;

ALTER TABLE stock_adjustments
ADD CONSTRAINT fk_adjustments_product FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT;

ALTER TABLE stock_adjustments
ADD CONSTRAINT fk_adjustments_created_by FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE RESTRICT;

-- =============================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    -- Skip if only updated_at changed
    IF ROW(NEW.*) IS NOT DISTINCT FROM ROW(OLD.*) THEN
        RETURN NEW;
    END IF;

    -- Force updated_at to current timestamp
    NEW.updated_at := CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE
UPDATE
    ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_categories_updated_at BEFORE
UPDATE
    ON categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_suppliers_updated_at BEFORE
UPDATE
    ON suppliers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE
UPDATE
    ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_inventory_updated_at BEFORE
UPDATE
    ON product_inventory FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_purchase_orders_updated_at BEFORE
UPDATE
    ON purchase_orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_purchase_order_items_updated_at BEFORE
UPDATE
    ON purchase_order_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stock_movements_updated_at BEFORE
UPDATE
    ON stock_movements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stock_adjustments_updated_at BEFORE
UPDATE
    ON stock_adjustments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- =============================================
-- PURCHASE ORDER WORKFLOW TRIGGERS
-- =============================================
-- Auto-generate po_number in sequential format (PO-YYYY-XXXXX)
CREATE TABLE po_number_counters (
    year INT PRIMARY KEY,
    last_number BIGINT NOT NULL
);

CREATE OR REPLACE FUNCTION generate_po_number()
RETURNS TRIGGER AS $$
DECLARE
    current_year INT;
    next_number BIGINT;
BEGIN
    IF NEW.po_number IS NOT NULL THEN
        RETURN NEW;
    END IF;

    current_year := EXTRACT(YEAR FROM CURRENT_DATE)::INT;

    LOOP
        -- Try update first (fast path)
        UPDATE po_number_counters
        SET last_number = last_number + 1
        WHERE year = current_year
        RETURNING last_number INTO next_number;

        EXIT WHEN FOUND;

        -- If no row exists, try to insert
        BEGIN
            INSERT INTO po_number_counters (year, last_number)
            VALUES (current_year, 1)
            RETURNING last_number INTO next_number;

            EXIT;
        EXCEPTION
            WHEN unique_violation THEN
                -- Another transaction inserted first, retry
        END;
    END LOOP;

    NEW.po_number :=
        'PO-' || current_year || '-' || LPAD(next_number::TEXT, 5, '0');

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_generate_po_number
BEFORE INSERT ON purchase_orders
FOR EACH ROW
EXECUTE FUNCTION generate_po_number();

-- =============================================
-- PRODUCT CATALOG TRIGGERS
-- =============================================
-- 7. Auto-generate SKU in sequential format (SKU-YYYY-XXXXX)
CREATE TABLE product_sku_counters (
    year INT PRIMARY KEY,
    last_number BIGINT NOT NULL
);

CREATE OR REPLACE FUNCTION generate_product_sku()
RETURNS TRIGGER AS $$
DECLARE
    current_year INT;
    next_number BIGINT;
BEGIN
    -- Respect manual SKU
    IF NEW.sku IS NOT NULL AND NEW.sku <> '' THEN
        RETURN NEW;
    END IF;

    current_year := EXTRACT(YEAR FROM CURRENT_DATE)::INT;

    LOOP
        -- Fast path
        UPDATE product_sku_counters
        SET last_number = last_number + 1
        WHERE year = current_year
        RETURNING last_number INTO next_number;

        EXIT WHEN FOUND;

        -- First SKU of the year
        BEGIN
            INSERT INTO product_sku_counters (year, last_number)
            VALUES (current_year, 1)
            RETURNING last_number INTO next_number;
            EXIT;
        EXCEPTION
            WHEN unique_violation THEN
                -- Retry if concurrent insert happened
        END;
    END LOOP;

    NEW.sku :=
        'SKU-' || current_year || '-' || LPAD(next_number::TEXT, 5, '0');

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_generate_product_sku
BEFORE INSERT ON products
FOR EACH ROW
EXECUTE FUNCTION generate_product_sku();

-- =============================================
-- Logical Constraints
-- =============================================
-- 1. PRODUCTS TABLE - Business Rule Constraints
ALTER TABLE products -- Ensure positive pricing
ADD CONSTRAINT chk_price_positive CHECK (price > 0),
-- Ensure valid cost price (can be NULL for unknown)
ADD CONSTRAINT chk_cost_price_valid CHECK (
    cost_price IS NULL
    OR cost_price >= 0
),
-- Ensure valid stock thresholds
ADD CONSTRAINT chk_stock_thresholds CHECK (
    low_stock_threshold >= 0
    AND reorder_point >= 0
    AND reorder_quantity > 0
);

-- 2. PURCHASE ORDERS TABLE - Workflow Constraints
ALTER TABLE purchase_orders -- Ensure positive amounts or NULL
ADD CONSTRAINT chk_total_amount_positive CHECK (
    total_amount IS NULL
    OR total_amount >= 0
),
-- Ensure logical date progression
ADD CONSTRAINT chk_po_dates_logical CHECK (
    (
        ordered_date IS NULL
        OR expected_delivery_date IS NULL
    )
    OR expected_delivery_date >= ordered_date
),
ADD CONSTRAINT chk_received_date_valid CHECK (
    (
        received_date IS NULL
        AND status != 'received'
    )
    OR (
        received_date IS NOT NULL
        AND status = 'received'
        AND received_date >= ordered_date
    )
),
-- Ensure draft orders have no ordered date
ADD CONSTRAINT chk_draft_state CHECK (
    (
        status = 'draft'
        AND ordered_date IS NULL
    )
    OR (status != 'draft')
),
-- Ensure ordered orders have an ordered date
ADD CONSTRAINT chk_ordered_state CHECK (
    (
        status = 'ordered'
        AND ordered_date IS NOT NULL
    )
    OR (status != 'ordered')
);

-- 3. PRODUCT INVENTORY TABLE - Quantity Constraints
ALTER TABLE product_inventory -- Ensure non-negative quantities
ADD CONSTRAINT chk_quantity_non_negative CHECK (
    quantity_on_hand >= 0
    AND (
        quantity_committed IS NULL
        OR quantity_committed >= 0
    )
    AND quantity_available >= 0
),
-- Ensure counting dates are logical
ADD CONSTRAINT chk_count_dates CHECK (
    last_counted_at IS NULL
    OR last_restocked_at IS NULL
    OR last_counted_at >= last_restocked_at
);

-- 4. STOCK MOVEMENTS TABLE - Movement Logic Constraints
ALTER TABLE stock_movements -- Ensure quantity change matches movement type
ADD CONSTRAINT chk_movement_quantity_sign CHECK (
    (
        movement_type = 'in'
        AND quantity_change > 0
    )
    OR (
        movement_type = 'out'
        AND quantity_change < 0
    )
    OR (movement_type = 'adjustment') -- Can be positive or negative
),
-- Ensure mathematical consistency
ADD CONSTRAINT chk_movement_math CHECK (
    quantity_after = quantity_before + quantity_change
),
-- Ensure before/after quantities are non-negative
ADD CONSTRAINT chk_movement_quantities_non_negative CHECK (
    quantity_before >= 0
    AND quantity_after >= 0
);

-- 5. PURCHASE ORDER ITEMS TABLE - Item-level Constraints
ALTER TABLE purchase_order_items
ADD CONSTRAINT chk_quantities_positive CHECK (
    quantity_ordered > 0
    AND quantity_received >= 0
    AND unit_cost >= 0
    AND line_total >= 0
),
ADD CONSTRAINT chk_received_vs_ordered CHECK (
    quantity_received <= quantity_ordered
),
ADD CONSTRAINT chk_line_total_calculation CHECK (
    line_total = quantity_ordered * unit_cost
);

-- 6. CATEGORIES TABLE - Hierarchical Constraints
CREATE OR REPLACE FUNCTION enforce_category_hierarchy()
RETURNS TRIGGER AS $$
DECLARE
    parent_active BOOLEAN;
    cycle_found   BOOLEAN;
BEGIN
    -- ==============================
    -- 1. Prevent self-parenting
    -- ==============================
    IF NEW.parent_id IS NOT NULL AND NEW.parent_id = NEW.id THEN
        RAISE EXCEPTION
            'Category % cannot be its own parent',
            NEW.id;
    END IF;

    -- ==============================
    -- 2. Prevent recursive cycles
    -- ==============================
    IF NEW.parent_id IS NOT NULL AND TG_OP = 'UPDATE' THEN
        WITH RECURSIVE ancestors AS (
            SELECT id, parent_id
            FROM categories
            WHERE id = NEW.parent_id

            UNION ALL

            SELECT c.id, c.parent_id
            FROM categories c
            JOIN ancestors a ON c.id = a.parent_id
        )
        SELECT TRUE INTO cycle_found
        FROM ancestors
        WHERE id = NEW.id
        LIMIT 1;

        IF cycle_found THEN
            RAISE EXCEPTION
                'Hierarchy cycle detected: category % cannot be parented under its descendant %',
                NEW.id, NEW.parent_id;
        END IF;
    END IF;

    -- ==============================
    -- 3. Active child requires active parent
    -- ==============================
    IF NEW.is_active = TRUE AND NEW.parent_id IS NOT NULL THEN
        SELECT is_active
        INTO parent_active
        FROM categories
        WHERE id = NEW.parent_id
        FOR SHARE;

        IF parent_active = FALSE THEN
            RAISE EXCEPTION
                'Active category % cannot have inactive parent %',
                NEW.id, NEW.parent_id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_enforce_category_hierarchy
BEFORE INSERT OR UPDATE OF parent_id, is_active
ON categories
FOR EACH ROW
EXECUTE FUNCTION enforce_category_hierarchy();

-- 7. USERS TABLE - time Constraints
ALTER TABLE users
ADD CONSTRAINT chk_user_timeline CHECK (
    created_at <= updated_at
    AND -- Ensure updated_at is after creation
    (
        last_login_at IS NULL
        OR last_login_at >= created_at
    ) -- Ensure last_login_at is after creation
);

-- 8. STOCK ADJUSTMENTS - Adjustment-specific Rules
ALTER TABLE stock_adjustments
ADD CONSTRAINT chk_adjustment_quantities CHECK (
    (
        adjustment_type IN (
            'damaged',
            'expired',
            'theft',
            'internal_use'
        )
        AND quantity_adjusted < 0
    )
    OR (
        adjustment_type IN ('found', 'returned')
        AND quantity_adjusted > 0
    )
),
ADD CONSTRAINT chk_adjustment_reason_required CHECK (
    adjustment_type NOT IN('damaged', 'theft')
    OR (
        reason IS NOT NULL
        AND LENGTH(TRIM(reason)) > 10
    )
);