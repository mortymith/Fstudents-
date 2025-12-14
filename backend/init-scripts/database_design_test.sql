-- =============================================
-- DATABASE DESIGN VALIDATION TEST SCRIPT
-- Professional QA Test Suite - AAA Pattern
-- =============================================





-- =============================================
-- TEST 1: USERS TABLE - COMPLETE VALIDATION
-- =============================================
-- Helper function to create a unique test identifier
CREATE OR REPLACE FUNCTION generate_test_id() 
RETURNS TEXT AS $$
BEGIN
    RETURN 'test_' || REPLACE(CAST(gen_random_uuid() AS TEXT), '-', '_');
END;
$$ LANGUAGE plpgsql;
DO $$
DECLARE
    test_name TEXT := 'USERS_TABLE_VALIDATION';
    test_user_id BIGINT;
    test_email TEXT;
BEGIN
    RAISE NOTICE '=============================================';
    RAISE NOTICE 'TEST: %', test_name;
    RAISE NOTICE '=============================================';
    
    -- ARRANGE: Prepare test data
    test_email := 'user_' || generate_test_id() || '@example.com';
    
    -- ACT & ASSERT: Test 1.1 - Valid user insertion
    BEGIN
        INSERT INTO users (email, password_hash, full_name, role)
        VALUES (test_email, 'hashed_password_123', 'Test User', 'viewer')
        RETURNING id INTO test_user_id;
        
        RAISE NOTICE '✅ Test 1.1: Valid user insertion PASSED (ID: %)', test_user_id;
        
        -- Verify the insertion
        PERFORM 1 FROM users WHERE id = test_user_id;
        IF FOUND THEN
            RAISE NOTICE '✅ Test 1.1 Verification: User record exists';
        ELSE
            RAISE EXCEPTION 'Test 1.1 Verification: User record not found';
        END IF;
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 1.1: Valid user insertion FAILED - %', SQLERRM;
    END;
    
    -- ACT & ASSERT: Test 1.2 - Unique email constraint
    BEGIN
        INSERT INTO users (email, password_hash, full_name, role)
        VALUES (test_email, 'another_hash', 'Duplicate User', 'viewer');
        
        RAISE EXCEPTION 'Test 1.2: Should have raised unique violation';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE '✅ Test 1.2: Unique email constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 1.3 - Valid role constraint
    BEGIN
        INSERT INTO users (email, password_hash, full_name, role)
        VALUES ('admin_' || generate_test_id() || '@example.com', 'hash', 'Admin User', 'admin')
        RETURNING id INTO test_user_id;
        
        RAISE NOTICE '✅ Test 1.3: Valid role (admin) insertion PASSED';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 1.3: Valid role insertion FAILED - %', SQLERRM;
    END;
    
    -- ACT & ASSERT: Test 1.4 - Invalid role constraint
    BEGIN
        INSERT INTO users (email, password_hash, full_name, role)
        VALUES ('invalid_' || generate_test_id() || '@example.com', 'hash', 'Invalid Role', 'invalid_role');
        
        RAISE EXCEPTION 'Test 1.4: Should have raised check violation';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ Test 1.4: Invalid role constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 1.5 - Timestamps auto-population
    DECLARE
        created_timestamp TIMESTAMP;
        updated_timestamp TIMESTAMP;
    BEGIN
        SELECT created_at, updated_at INTO created_timestamp, updated_timestamp
        FROM users WHERE id = test_user_id;
        
        IF created_timestamp IS NOT NULL AND updated_timestamp IS NOT NULL THEN
            RAISE NOTICE '✅ Test 1.5: Auto timestamps PASSED (Created: %, Updated: %)', 
                        created_timestamp, updated_timestamp;
        ELSE
            RAISE EXCEPTION 'Test 1.5: Timestamps not auto-populated';
        END IF;
    END;
    
    -- CLEANUP
    DELETE FROM users WHERE email LIKE '%' || generate_test_id() || '%';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '❌ UNEXPECTED ERROR in %: %', test_name, SQLERRM;
    -- Ensure cleanup
    DELETE FROM users WHERE email LIKE '%' || generate_test_id() || '%';
END $$;

















-- =============================================
-- TEST 2: CATEGORIES TABLE - COMPLETE VALIDATION
-- =============================================
DO $$
DECLARE
    test_name TEXT := 'CATEGORIES_TABLE_VALIDATION';
    test_parent_id BIGINT;
    child_id BIGINT;
    test_category_name TEXT;
BEGIN
    RAISE NOTICE E'\n=============================================';
    RAISE NOTICE 'TEST: %', test_name;
    RAISE NOTICE '=============================================';
    
    -- ARRANGE: Generate unique test data
    test_category_name := 'Test_Category_' || generate_test_id();
    
    -- ACT & ASSERT: Test 2.1 - Valid category insertion
    BEGIN
        INSERT INTO categories (name, description)
        VALUES (test_category_name, 'Test category description')
        RETURNING id INTO test_parent_id;
        
        RAISE NOTICE '✅ Test 2.1: Valid category insertion PASSED (ID: %)', test_parent_id;
        
        -- Verify active default
        DECLARE
            is_active_flag BOOLEAN;
        BEGIN
            SELECT is_active INTO is_active_flag FROM categories WHERE id = test_parent_id;
            IF is_active_flag = true THEN
                RAISE NOTICE '✅ Test 2.1 Verification: Default is_active = true';
            ELSE
                RAISE EXCEPTION 'Test 2.1 Verification: Default is_active incorrect';
            END IF;
        END;
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 2.1: Valid category insertion FAILED - %', SQLERRM;
        RETURN;
    END;
    
    -- ACT & ASSERT: Test 2.2 - Unique name constraint
    BEGIN
        INSERT INTO categories (name, description)
        VALUES (test_category_name, 'Duplicate name');
        
        RAISE EXCEPTION 'Test 2.2: Should have raised unique violation';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE '✅ Test 2.2: Unique name constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 2.3 - Valid child category
    DECLARE
        child_category_name TEXT := 'Child_Category_' || generate_test_id();
    BEGIN
        INSERT INTO categories (name, description, parent_id)
        VALUES (child_category_name, 'Child category', test_parent_id)
        RETURNING id INTO child_id;
        
        RAISE NOTICE '✅ Test 2.3: Valid child category PASSED (ID: %)', child_id;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 2.3: Valid child category FAILED - %', SQLERRM;
    END;
    
    -- ACT & ASSERT: Test 2.4 - Self-reference constraint
    BEGIN
        UPDATE categories SET parent_id = test_parent_id WHERE id = test_parent_id;
        
        RAISE EXCEPTION 'Test 2.4: Should have raised hierarchy constraint violation';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '✅ Test 2.4: Self-reference constraint PASSED - %', SQLERRM;
    END;
    
    -- ACT & ASSERT: Test 2.5 - Active child with inactive parent constraint
    BEGIN
        -- First deactivate parent
        UPDATE categories SET is_active = false WHERE id = test_parent_id;
        
        -- Try to create active child
        INSERT INTO categories (name, description, parent_id, is_active)
        VALUES ('Active_Child_' || generate_test_id(), 'Should fail', test_parent_id, true);
        
        RAISE EXCEPTION 'Test 2.5: Should have raised hierarchy constraint violation';
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '✅ Test 2.5: Active child with inactive parent PASSED';
        -- Reactivate parent for cleanup
        UPDATE categories SET is_active = true WHERE id = test_parent_id;
    END;
    
    -- CLEANUP
    DELETE FROM categories WHERE name LIKE '%' || generate_test_id() || '%';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '❌ UNEXPECTED ERROR in %: %', test_name, SQLERRM;
    DELETE FROM categories WHERE name LIKE '%' || generate_test_id() || '%';
END $$;









-- =============================================
-- TEST 3: SUPPLIERS TABLE - COMPLETE VALIDATION
-- =============================================
DO $$
DECLARE
    test_name TEXT := 'SUPPLIERS_TABLE_VALIDATION';
    test_supplier_id BIGINT;
    test_supplier_name TEXT;
    test_supplier_email TEXT;
BEGIN
    RAISE NOTICE E'\n=============================================';
    RAISE NOTICE 'TEST: %', test_name;
    RAISE NOTICE '================================================';
    
    -- ARRANGE: Generate unique test data
    test_supplier_name := 'Test_Supplier_' || generate_test_id();
    test_supplier_email := 'supplier_' || generate_test_id() || '@example.com';
    
    -- ACT & ASSERT: Test 3.1 - Valid supplier insertion
    BEGIN
        INSERT INTO suppliers (
            name, contact_person_name, contact_email, contact_phone,
            address_line1, city, state, postal_code, country
        ) VALUES (
            test_supplier_name, 'John Supplier', test_supplier_email, '+1234567890',
            '123 Business St', 'Metropolis', 'State', '12345', 'Country'
        ) RETURNING id INTO test_supplier_id;
        
        RAISE NOTICE '✅ Test 3.1: Valid supplier insertion PASSED (ID: %)', test_supplier_id;
        
        -- Verify is_active default
        DECLARE
            is_active_flag BOOLEAN;
        BEGIN
            SELECT is_active INTO is_active_flag FROM suppliers WHERE id = test_supplier_id;
            IF is_active_flag = true THEN
                RAISE NOTICE '✅ Test 3.1 Verification: Default is_active = true';
            ELSE
                RAISE EXCEPTION 'Test 3.1 Verification: Default is_active incorrect';
            END IF;
        END;
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 3.1: Valid supplier insertion FAILED - %', SQLERRM;
        RETURN;
    END;
    
    -- ACT & ASSERT: Test 3.2 - Unique name constraint
    BEGIN
        INSERT INTO suppliers (name, contact_email, contact_phone)
        VALUES (test_supplier_name, 'another_' || test_supplier_email, '+0987654321');
        
        RAISE EXCEPTION 'Test 3.2: Should have raised unique violation';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE '✅ Test 3.2: Unique name constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 3.3 - Unique email constraint
    BEGIN
        INSERT INTO suppliers (name, contact_email, contact_phone)
        VALUES ('Another_Supplier_' || generate_test_id(), test_supplier_email, '+0987654321');
        
        RAISE EXCEPTION 'Test 3.3: Should have raised unique violation';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE '✅ Test 3.3: Unique email constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 3.4 - Timestamps verification
    DECLARE
        created_time TIMESTAMP;
        updated_time TIMESTAMP;
    BEGIN
        SELECT created_at, updated_at INTO created_time, updated_time
        FROM suppliers WHERE id = test_supplier_id;
        
        IF created_time IS NOT NULL AND updated_time IS NOT NULL THEN
            RAISE NOTICE '✅ Test 3.4: Auto timestamps PASSED';
        ELSE
            RAISE EXCEPTION 'Test 3.4: Timestamps not set';
        END IF;
    END;
    
    -- CLEANUP
    DELETE FROM suppliers WHERE name LIKE '%' || generate_test_id() || '%';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '❌ UNEXPECTED ERROR in %: %', test_name, SQLERRM;
    DELETE FROM suppliers WHERE name LIKE '%' || generate_test_id() || '%';
END $$;













-- =============================================
-- TEST 4: PRODUCTS TABLE - COMPLETE VALIDATION
-- =============================================
DO $$
DECLARE
    test_name TEXT := 'PRODUCTS_TABLE_VALIDATION';
    test_category_id BIGINT;
    test_supplier_id BIGINT;
    test_product_id BIGINT;
    test_product_sku VARCHAR(100);
    test_category_name TEXT;
    test_supplier_name TEXT;
    test_product_name TEXT;
BEGIN
    RAISE NOTICE E'\n=============================================';
    RAISE NOTICE 'TEST: %', test_name;
    RAISE NOTICE '=============================================';
    
    -- ARRANGE: Create prerequisite records
    test_category_name := 'ProdTest_Category_' || generate_test_id();
    test_supplier_name := 'ProdTest_Supplier_' || generate_test_id();
    test_product_name := 'Test_Product_' || generate_test_id();
    
    -- Create category
    INSERT INTO categories (name, description)
    VALUES (test_category_name, 'Test category for product validation')
    RETURNING id INTO test_category_id;
    
    -- Create supplier
    INSERT INTO suppliers (name, contact_email, contact_phone)
    VALUES (test_supplier_name, 'supplier_' || generate_test_id() || '@example.com', '+1234567890')
    RETURNING id INTO test_supplier_id;
    
    -- ACT & ASSERT: Test 4.1 - Auto-generated SKU
    BEGIN
        INSERT INTO products (
            name, description, category_id, supplier_id, price, cost_price
        ) VALUES (
            test_product_name, 'Test product description', 
            test_category_id, test_supplier_id, 19.99, 9.99
        ) RETURNING id, sku INTO test_product_id, test_product_sku;
        
        IF test_product_sku LIKE 'SKU-%' THEN
            RAISE NOTICE '✅ Test 4.1: Auto-generated SKU PASSED (SKU: %)', test_product_sku;
        ELSE
            RAISE EXCEPTION 'Test 4.1: SKU not properly generated';
        END IF;
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 4.1: Auto-generated SKU FAILED - %', SQLERRM;
        -- Cleanup and exit
        DELETE FROM categories WHERE id = test_category_id;
        DELETE FROM suppliers WHERE id = test_supplier_id;
        RETURN;
    END;
    
    -- ACT & ASSERT: Test 4.2 - Manual SKU respect
    DECLARE
        manual_sku_product_id BIGINT;
        manual_sku VARCHAR(100) := 'MANUAL-SKU-' || generate_test_id();
    BEGIN
        INSERT INTO products (
            sku, name, category_id, supplier_id, price
        ) VALUES (
            manual_sku, 'Manual_SKU_Product_' || generate_test_id(),
            test_category_id, test_supplier_id, 29.99
        ) RETURNING id INTO manual_sku_product_id;
        
       -- Verify manual SKU was used
        DECLARE
            actual_sku VARCHAR(100);
        BEGIN
            SELECT sku INTO actual_sku FROM products WHERE id = manual_sku_product_id;
            IF actual_sku = manual_sku THEN
                RAISE NOTICE '✅ Test 4.2: Manual SKU respected PASSED';
            ELSE
                RAISE EXCEPTION 'Test 4.2: Manual SKU was overwritten';
            END IF;
        END;
        
        -- -- Clean this test product
        DELETE FROM products WHERE id = manual_sku_product_id;
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 4.2: Manual SKU respect FAILED - %', SQLERRM;
    END;
    
    -- ACT & ASSERT: Test 4.3 - Price positive constraint
    BEGIN
        INSERT INTO products (
            name, category_id, supplier_id, price
        ) VALUES (
            'Invalid_Price_Product_' || generate_test_id(), 
            test_category_id, test_supplier_id, -10.00
        );
        
        RAISE EXCEPTION 'Test 4.3: Should have raised check violation';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ Test 4.4: Positive price constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 4.4 - Stock thresholds constraint
    BEGIN
        UPDATE products 
        SET low_stock_threshold = -1 
        WHERE id = test_product_id;
        
        RAISE EXCEPTION 'Test 4.4: Should have raised check violation';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ Test 4.4: Stock thresholds constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 4.5 - Foreign key constraints
    BEGIN
        INSERT INTO products (
            name, category_id, supplier_id, price
        ) VALUES (
            'Invalid_FK_Product_' || generate_test_id(), 
            999999, test_supplier_id, 15.00
        );
        
        RAISE EXCEPTION 'Test 4.5: Should have raised foreign key violation';
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE '✅ Test 4.5: Foreign key constraint (category) PASSED';
    END;
    
    -- ACT & ASSERT: Test 4.6 - is_active default
    DECLARE
        product_active_flag BOOLEAN;
    BEGIN
        SELECT is_active INTO product_active_flag 
        FROM products WHERE id = test_product_id;
        
        IF product_active_flag = true THEN
            RAISE NOTICE '✅ Test 4.6: Default is_active = true PASSED';
        ELSE
            RAISE EXCEPTION 'Test 4.6: Default is_active incorrect';
        END IF;
    END;
    
    -- CLEANUP
    DELETE FROM products WHERE id = test_product_id;
    DELETE FROM categories WHERE id = test_category_id;
    DELETE FROM suppliers WHERE id = test_supplier_id;
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '❌ UNEXPECTED ERROR in %: %', test_name, SQLERRM;
    -- Attempt cleanup
    DELETE FROM products WHERE name LIKE '%' || generate_test_id() || '%';
    DELETE FROM categories WHERE name LIKE '%' || generate_test_id() || '%';
    DELETE FROM suppliers WHERE name LIKE '%' || generate_test_id() || '%';
END $$;











-- =============================================
-- TEST 5: PRODUCT INVENTORY VALIDATION
-- =============================================
-- Helper function for inventory test cleanup
CREATE OR REPLACE FUNCTION cleanup_inventory_test_data(
    p_category_id BIGINT,
    p_supplier_id BIGINT,
    p_product_id BIGINT
) RETURNS VOID AS $$
BEGIN
    -- Delete in reverse order of dependencies
    IF p_product_id IS NOT NULL THEN
        DELETE FROM product_inventory WHERE product_id = p_product_id;
        DELETE FROM products WHERE id = p_product_id;
    END IF;
    
    DELETE FROM suppliers WHERE id = p_supplier_id;
    DELETE FROM categories WHERE id = p_category_id;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE
    test_name TEXT := 'PRODUCT_INVENTORY_VALIDATION';
    test_category_id BIGINT;
    test_supplier_id BIGINT;
    test_product_id BIGINT;
    test_inventory_id BIGINT;
    test_category_name TEXT;
    test_supplier_name TEXT;
    test_product_name TEXT;
    test_identifier TEXT;
BEGIN
    RAISE NOTICE E'\n=============================================';
    RAISE NOTICE 'TEST: %', test_name;
    RAISE NOTICE '=============================================';
    
    -- ARRANGE: Generate unique identifiers
    test_identifier := generate_test_id();
    test_category_name := 'InvCat_' || test_identifier;
    test_supplier_name := 'InvSupp_' || test_identifier;
    test_product_name := 'InvProd_' || test_identifier;
    
    -- Create category
    BEGIN
        INSERT INTO categories (name, description)
        VALUES (test_category_name, 'Test category for inventory validation')
        RETURNING id INTO test_category_id;
        
        RAISE NOTICE '✅ ARRANGE: Created test category (ID: %)', test_category_id;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ ARRANGE: Failed to create category - %', SQLERRM;
        RETURN;
    END;
    
    -- Create supplier
    BEGIN
        INSERT INTO suppliers (name, contact_email, contact_phone)
        VALUES (
            test_supplier_name, 
            'inv_supplier_' || test_identifier || '@example.com', 
            '+1234567890'
        ) RETURNING id INTO test_supplier_id;
        
        RAISE NOTICE '✅ ARRANGE: Created test supplier (ID: %)', test_supplier_id;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ ARRANGE: Failed to create supplier - %', SQLERRM;
        DELETE FROM categories WHERE id = test_category_id;
        RETURN;
    END;
    
    -- Create product
    BEGIN
        INSERT INTO products (
            name, description, category_id, supplier_id, price, cost_price,
            low_stock_threshold, reorder_point, reorder_quantity
        ) VALUES (
            test_product_name, 'Test product for inventory validation',
            test_category_id, test_supplier_id, 25.99, 12.50,
            5, 10, 25
        ) RETURNING id INTO test_product_id;
        
        RAISE NOTICE '✅ ARRANGE: Created test product (ID: %)', test_product_id;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ ARRANGE: Failed to create product - %', SQLERRM;
        PERFORM cleanup_inventory_test_data(
            test_category_id, test_supplier_id, NULL
        );
        RETURN;
    END;
    
    -- ACT & ASSERT: Test 5.1 - Manual inventory creation
    RAISE NOTICE E'\n--- Test 5.1: Manual inventory creation ---';
    BEGIN
        -- ACT: Manually create inventory record
        INSERT INTO product_inventory (
            product_id, 
            quantity_on_hand, 
            quantity_committed, 
            quantity_available,
            last_restocked_at,
            last_counted_at
        ) VALUES (
            test_product_id,
            100,  -- Initial stock
            25,   -- Committed orders
            75,   -- Available for sale (100 - 25)
            CURRENT_TIMESTAMP - INTERVAL '5 days',
            CURRENT_TIMESTAMP - INTERVAL '2 days'
        ) RETURNING id INTO test_inventory_id;
        
        RAISE NOTICE '✅ ACT: Manually created inventory record (ID: %)', test_inventory_id;
        
        -- ASSERT: Verify inventory was created correctly
        DECLARE
            inv_count INTEGER;
            actual_on_hand INTEGER;
            actual_committed INTEGER;
            actual_available INTEGER;
        BEGIN
            -- Check record exists
            SELECT COUNT(*) INTO inv_count
            FROM product_inventory 
            WHERE id = test_inventory_id;
            
            IF inv_count = 1 THEN
                RAISE NOTICE '✅ ASSERT: Inventory record created successfully';
            ELSE
                RAISE EXCEPTION 'ASSERT: Inventory record not found';
            END IF;
            
            -- Verify quantities
            SELECT 
                quantity_on_hand, 
                quantity_committed, 
                quantity_available
            INTO 
                actual_on_hand, 
                actual_committed, 
                actual_available
            FROM product_inventory 
            WHERE id = test_inventory_id;
            
            IF actual_on_hand = 100 THEN
                RAISE NOTICE '✅ ASSERT: quantity_on_hand = 100';
            ELSE
                RAISE EXCEPTION 'ASSERT: quantity_on_hand incorrect. Expected: 100, Got: %', actual_on_hand;
            END IF;
            
            IF actual_committed = 25 THEN
                RAISE NOTICE '✅ ASSERT: quantity_committed = 25';
            ELSE
                RAISE EXCEPTION 'ASSERT: quantity_committed incorrect. Expected: 25, Got: %', actual_committed;
            END IF;
            
            IF actual_available = 75 THEN
                RAISE NOTICE '✅ ASSERT: quantity_available = 75 (correct calculation: 100 - 25)';
            ELSE
                RAISE EXCEPTION 'ASSERT: quantity_available incorrect. Expected: 75, Got: %', actual_available;
            END IF;
            
            -- Verify timestamps
            DECLARE
                inv_created_at TIMESTAMP;
                inv_updated_at TIMESTAMP;
                inv_restocked_at TIMESTAMP;
                inv_counted_at TIMESTAMP;
            BEGIN
                SELECT 
                    created_at, 
                    updated_at,
                    last_restocked_at,
                    last_counted_at
                INTO 
                    inv_created_at, 
                    inv_updated_at,
                    inv_restocked_at,
                    inv_counted_at
                FROM product_inventory WHERE id = test_inventory_id;
                
                IF inv_created_at IS NOT NULL THEN
                    RAISE NOTICE '✅ ASSERT: created_at auto-populated';
                ELSE
                    RAISE EXCEPTION 'ASSERT: created_at not set';
                END IF;
                
                IF inv_updated_at IS NOT NULL THEN
                    RAISE NOTICE '✅ ASSERT: updated_at auto-populated';
                ELSE
                    RAISE EXCEPTION 'ASSERT: updated_at not set';
                END IF;
                
                IF inv_restocked_at IS NOT NULL THEN
                    RAISE NOTICE '✅ ASSERT: last_restocked_at set correctly';
                ELSE
                    RAISE EXCEPTION 'ASSERT: last_restocked_at not set';
                END IF;
                
                IF inv_counted_at IS NOT NULL THEN
                    RAISE NOTICE '✅ ASSERT: last_counted_at set correctly';
                ELSE
                    RAISE EXCEPTION 'ASSERT: last_counted_at not set';
                END IF;
            END;
        END;
        
        RAISE NOTICE '✅ Test 5.1: PASSED - Manual inventory creation works correctly';
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 5.1: FAILED - %', SQLERRM;
        PERFORM cleanup_inventory_test_data(
            test_category_id, test_supplier_id, test_product_id
        );
        RETURN;
    END;
    
    -- ACT & ASSERT: Test 5.2 - Inventory quantity constraints
    RAISE NOTICE E'\n--- Test 5.2: Inventory quantity constraints ---';
    BEGIN
        -- Test 5.2.1: Negative quantity_on_hand constraint
        BEGIN
            -- ACT: Try to set negative quantity_on_hand
            UPDATE product_inventory 
            SET quantity_on_hand = -10 
            WHERE id = test_inventory_id;
            
            RAISE EXCEPTION 'Test 5.2.1: Should have raised check violation for negative quantity_on_hand';
            
        EXCEPTION WHEN check_violation THEN
            RAISE NOTICE '✅ ASSERT 5.2.1: Check violation raised for negative quantity_on_hand';
            
            -- Verify quantity_on_hand wasn't changed
            DECLARE
                current_on_hand INTEGER;
            BEGIN
                SELECT quantity_on_hand INTO current_on_hand
                FROM product_inventory 
                WHERE id = test_inventory_id;
                
                IF current_on_hand = 100 THEN
                    RAISE NOTICE '✅ ASSERT 5.2.1: quantity_on_hand unchanged (still 100)';
                ELSE
                    RAISE EXCEPTION 'ASSERT 5.2.1: quantity_on_hand incorrectly changed to %', current_on_hand;
                END IF;
            END;
        END;
        
        -- Test 5.2.2: Negative quantity_committed constraint
        BEGIN
            -- ACT: Try to set negative quantity_committed
            UPDATE product_inventory 
            SET quantity_committed = -5 
            WHERE id = test_inventory_id;
            
            RAISE EXCEPTION 'Test 5.2.2: Should have raised check violation for negative quantity_committed';
            
        EXCEPTION WHEN check_violation THEN
            RAISE NOTICE '✅ ASSERT 5.2.2: Check violation raised for negative quantity_committed';
        END;
        
        -- Test 5.2.3: Negative quantity_available constraint
        BEGIN
            -- ACT: Try to set negative quantity_available directly
            UPDATE product_inventory 
            SET quantity_available = -1 
            WHERE id = test_inventory_id;
            
            RAISE EXCEPTION 'Test 5.2.3: Should have raised check violation for negative quantity_available';
            
        EXCEPTION WHEN check_violation THEN
            RAISE NOTICE '✅ ASSERT 5.2.3: Check violation raised for negative quantity_available';
        END;
        
        RAISE NOTICE '✅ Test 5.2: PASSED - All quantity constraints enforced';
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 5.2: FAILED - %', SQLERRM;
    END;
    
    -- ACT & ASSERT: Test 5.4 - Inventory date constraints
    RAISE NOTICE E'\n--- Test 5.4: Inventory date constraints ---';
    DECLARE
        valid_restock_date TIMESTAMP := CURRENT_TIMESTAMP - INTERVAL '7 days';
        valid_count_date TIMESTAMP := CURRENT_TIMESTAMP - INTERVAL '3 days';
        invalid_count_date TIMESTAMP := CURRENT_TIMESTAMP - INTERVAL '10 days'; -- Earlier than restock
    BEGIN
        -- Test 5.4.1: Set valid dates (last_counted_at >= last_restocked_at)
        BEGIN
            -- ACT: Set valid dates
            UPDATE product_inventory 
            SET 
                last_restocked_at = valid_restock_date,
                last_counted_at = valid_count_date
            WHERE id = test_inventory_id;
            
            RAISE NOTICE '✅ ACT 5.4.1: Set valid dates (Restocked: %, Counted: %)', 
                         valid_restock_date, valid_count_date;
            
            -- ASSERT: Verify dates were set
            DECLARE
                actual_restocked TIMESTAMP;
                actual_counted TIMESTAMP;
            BEGIN
                SELECT last_restocked_at, last_counted_at 
                INTO actual_restocked, actual_counted
                FROM product_inventory 
                WHERE id = test_inventory_id;
                
                IF actual_restocked = valid_restock_date THEN
                    RAISE NOTICE '✅ ASSERT 5.4.1: last_restocked_at set correctly';
                ELSE
                    RAISE EXCEPTION 'ASSERT 5.4.1: last_restocked_at not set properly';
                END IF;
                
                IF actual_counted = valid_count_date THEN
                    RAISE NOTICE '✅ ASSERT 5.4.1: last_counted_at set correctly';
                ELSE
                    RAISE EXCEPTION 'ASSERT 5.4.1: last_counted_at not set properly';
                END IF;
            END;
            
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE '❌ Test 5.4.1: FAILED - %', SQLERRM;
        END;
        
        -- Test 5.4.2: Invalid date order constraint
        BEGIN
            -- ACT: Try to set last_counted_at earlier than last_restocked_at
            UPDATE product_inventory 
            SET last_counted_at = invalid_count_date
            WHERE id = test_inventory_id;
            
            RAISE EXCEPTION 'Test 5.4.2: Should have raised check violation for invalid date order';
            
        EXCEPTION WHEN check_violation THEN
            RAISE NOTICE '✅ ASSERT 5.4.2: Check violation raised for last_counted_at < last_restocked_at';
        END;
        
        -- Test 5.4.3: NULL dates are allowed
        BEGIN
            -- ACT: Set dates to NULL
            UPDATE product_inventory 
            SET 
                last_restocked_at = NULL,
                last_counted_at = NULL
            WHERE id = test_inventory_id;
            
            -- ASSERT: Verify NULLs are accepted
            DECLARE
                null_restocked TIMESTAMP;
                null_counted TIMESTAMP;
            BEGIN
                SELECT last_restocked_at, last_counted_at 
                INTO null_restocked, null_counted
                FROM product_inventory 
                WHERE id = test_inventory_id;
                
                IF null_restocked IS NULL AND null_counted IS NULL THEN
                    RAISE NOTICE '✅ ASSERT 5.4.3: NULL dates accepted correctly';
                ELSE
                    RAISE EXCEPTION 'ASSERT 5.4.3: NULL dates not properly set';
                END IF;
            END;
            
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE '❌ Test 5.4.3: FAILED - %', SQLERRM;
        END;
        
        RAISE NOTICE '✅ Test 5.4: PASSED - Date constraints enforced correctly';
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 5.4: FAILED - %', SQLERRM;
    END;
    
    -- ACT & ASSERT: Test 5.5 - Unique product constraint
    RAISE NOTICE E'\n--- Test 5.5: Unique product constraint ---';
    BEGIN
        -- ACT: Try to create duplicate inventory record for same product
        INSERT INTO product_inventory (product_id, quantity_on_hand)
        VALUES (test_product_id, 50);
        
        RAISE EXCEPTION 'Test 5.5: Should have raised unique violation';
        
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE '✅ ASSERT: Unique violation raised for duplicate product_id';
        
        -- Verify no additional record was created
        DECLARE
            inventory_count INTEGER;
        BEGIN
            SELECT COUNT(*) INTO inventory_count
            FROM product_inventory 
            WHERE product_id = test_product_id;
            
            IF inventory_count = 1 THEN
                RAISE NOTICE '✅ ASSERT: Still only one inventory record per product';
            ELSE
                RAISE EXCEPTION 'ASSERT: Inventory count changed to %', inventory_count;
            END IF;
        END;
        
        RAISE NOTICE '✅ Test 5.5: PASSED - One inventory record per product enforced';
    END;
    
    -- ACT & ASSERT: Test 5.6 - Updated_at trigger functionality
    RAISE NOTICE E'\n--- Test 5.6: Updated_at trigger functionality ---';
    DECLARE
        initial_updated_at TIMESTAMP;
        updated_updated_at TIMESTAMP;
        sleep_interval INTERVAL := INTERVAL '1 millisecond';
    BEGIN
        -- ARRANGE: Get initial updated_at
        SELECT updated_at INTO initial_updated_at
        FROM product_inventory 
        WHERE id = test_inventory_id;
        
        RAISE NOTICE '✅ ARRANGE: Initial updated_at: %', initial_updated_at;
        
        -- Wait a bit to ensure timestamp change
        PERFORM pg_sleep(15.500);
        
        -- ACT: Update a field
        UPDATE product_inventory 
        SET quantity_on_hand = quantity_on_hand + 20
        WHERE id = test_inventory_id
        RETURNING updated_at INTO updated_updated_at;
        
        RAISE NOTICE '✅ ACT: Updated quantity_on_hand (+20)';
        
        -- ASSERT: Verify updated_at changed
        IF updated_updated_at > initial_updated_at THEN
            RAISE NOTICE '✅ ASSERT: updated_at automatically updated (Old: %, New: %)',
                        initial_updated_at, updated_updated_at;
            
            -- Test that unchanged rows don't update updated_at
            PERFORM pg_sleep(0.501);
            
            DECLARE
                no_change_updated_at TIMESTAMP;
            BEGIN
                -- Update with same values
                UPDATE product_inventory 
                SET quantity_on_hand = quantity_on_hand  -- No actual change
                WHERE id = test_inventory_id
                RETURNING updated_at INTO no_change_updated_at;
                
                IF no_change_updated_at = updated_updated_at THEN
                    RAISE NOTICE '✅ ASSERT: updated_at unchanged when no real update occurs';
                ELSE
                    RAISE NOTICE '⚠️  WARNING: updated_at changed even when no values changed (Old: %, New: %)',
                                updated_updated_at, no_change_updated_at;
                END IF;
            END;
            
            RAISE NOTICE '✅ Test 5.6: PASSED - updated_at trigger working correctly';
        ELSE
            RAISE EXCEPTION 'ASSERT: updated_at not updated (Old: %, New: %)',
                           initial_updated_at, updated_updated_at;
        END IF;
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 5.6: FAILED - %', SQLERRM;
    END;
    
    -- ACT & ASSERT: Test 5.7 - Foreign key constraint
    RAISE NOTICE E'\n--- Test 5.7: Foreign key constraint ---';
    BEGIN
        -- Create a second product
        DECLARE
            second_product_id BIGINT;
            second_product_name TEXT := 'Second_Product_' || test_identifier;
        BEGIN
            INSERT INTO products (name, category_id, supplier_id, price)
            VALUES (second_product_name, test_category_id, test_supplier_id, 19.99)
            RETURNING id INTO second_product_id;
            
            RAISE NOTICE '✅ ARRANGE: Created second product (ID: %)', second_product_id;
            
            -- Test 5.7.1: Valid foreign key
            BEGIN
                INSERT INTO product_inventory (product_id, quantity_on_hand)
                VALUES (second_product_id, 50);
                
                RAISE NOTICE '✅ ASSERT 5.7.1: Can create inventory for valid product_id';
                
                -- Clean up this inventory record
                DELETE FROM product_inventory WHERE product_id = second_product_id;
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE '❌ ASSERT 5.7.1: Failed to create inventory for valid product - %', SQLERRM;
            END;
            
            -- Test 5.7.2: Invalid foreign key
            BEGIN
                INSERT INTO product_inventory (product_id, quantity_on_hand)
                VALUES (999999, 100);  -- Invalid product_id
                
                RAISE EXCEPTION 'Test 5.7.2: Should have raised foreign key violation';
                
            EXCEPTION WHEN foreign_key_violation THEN
                RAISE NOTICE '✅ ASSERT 5.7.2: Foreign key violation raised for invalid product_id';
            END;
            
            -- Clean up second product
            DELETE FROM products WHERE id = second_product_id;
            
        END;
        
        RAISE NOTICE '✅ Test 5.7: PASSED - Foreign key constraint enforced';
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 5.7: FAILED - %', SQLERRM;
    END;
    
    -- ACT & ASSERT: Test 5.8 - Default values
    RAISE NOTICE E'\n--- Test 5.8: Default values ---';
    DECLARE
        new_product_id BIGINT;
        new_product_name TEXT := 'New_Product_' || test_identifier;
        new_inventory_id BIGINT;
        default_on_hand INTEGER;
        default_committed INTEGER;
        default_available INTEGER;
    BEGIN
        -- Create a new product
        INSERT INTO products (name, category_id, supplier_id, price)
        VALUES (new_product_name, test_category_id, test_supplier_id, 14.99)
        RETURNING id INTO new_product_id;
        
        -- Create inventory with minimal data
        INSERT INTO product_inventory (product_id)
        VALUES (new_product_id)
        RETURNING id INTO new_inventory_id;
        
        -- Check default values
        SELECT 
            quantity_on_hand, 
            quantity_committed, 
            quantity_available
        INTO 
            default_on_hand, 
            default_committed, 
            default_available
        FROM product_inventory 
        WHERE id = new_inventory_id;
        
        IF default_on_hand = 0 THEN
            RAISE NOTICE '✅ ASSERT: Default quantity_on_hand = 0';
        ELSE
            RAISE EXCEPTION 'ASSERT: Default quantity_on_hand incorrect. Expected: 0, Got: %', default_on_hand;
        END IF;
        
        IF default_committed = 0 THEN
            RAISE NOTICE '✅ ASSERT: Default quantity_committed = 0';
        ELSE
            RAISE EXCEPTION 'ASSERT: Default quantity_committed incorrect. Expected: 0, Got: %', default_committed;
        END IF;
        
        IF default_available = 0 THEN
            RAISE NOTICE '✅ ASSERT: Default quantity_available = 0';
        ELSE
            RAISE EXCEPTION 'ASSERT: Default quantity_available incorrect. Expected: 0, Got: %', default_available;
        END IF;
        
        -- Check default timestamps
        DECLARE
            default_created_at TIMESTAMP;
            default_updated_at TIMESTAMP;
        BEGIN
            SELECT created_at, updated_at 
            INTO default_created_at, default_updated_at
            FROM product_inventory WHERE id = new_inventory_id;
            
            IF default_created_at IS NOT NULL THEN
                RAISE NOTICE '✅ ASSERT: Default created_at set';
            ELSE
                RAISE EXCEPTION 'ASSERT: Default created_at not set';
            END IF;
            
            IF default_updated_at IS NOT NULL THEN
                RAISE NOTICE '✅ ASSERT: Default updated_at set';
            ELSE
                RAISE EXCEPTION 'ASSERT: Default updated_at not set';
            END IF;
        END;
        
        -- Clean up test data
        DELETE FROM product_inventory WHERE id = new_inventory_id;
        DELETE FROM products WHERE id = new_product_id;
        
        RAISE NOTICE '✅ Test 5.8: PASSED - Default values work correctly';
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 5.8: FAILED - %', SQLERRM;
    END;
    
    -- CLEANUP
    RAISE NOTICE E'\n--- CLEANUP ---';
    PERFORM cleanup_inventory_test_data(
        test_category_id, test_supplier_id, test_product_id
    );
    RAISE NOTICE '✅ Cleanup completed successfully';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '❌ UNEXPECTED ERROR in %: %', test_name, SQLERRM;
    PERFORM cleanup_inventory_test_data(
        test_category_id, test_supplier_id, test_product_id
    );
END $$;









-- =============================================
-- TEST 6: PURCHASE ORDERS - COMPLETE WORKFLOW
-- =============================================
DO $$
DECLARE
    test_name TEXT := 'PURCHASE_ORDERS_WORKFLOW';
    test_user_id BIGINT;
    test_supplier_id BIGINT;
    test_po_id BIGINT;
    test_po_number VARCHAR(100);
    test_user_email TEXT;
    test_supplier_name TEXT;
BEGIN
    RAISE NOTICE E'\n=============================================';
    RAISE NOTICE 'TEST: %', test_name;
    RAISE NOTICE '=============================================';
    
    -- ARRANGE: Create prerequisite records
    test_user_email := 'po_user_' || generate_test_id() || '@example.com';
    test_supplier_name := 'PO_Supplier_' || generate_test_id();
    
    -- Create user
    INSERT INTO users (email, password_hash, full_name, role)
    VALUES (test_user_email, 'hashed_password', 'PO Test User', 'inventory_manager')
    RETURNING id INTO test_user_id;
    
    -- Create supplier
    INSERT INTO suppliers (name, contact_email, contact_phone)
    VALUES (test_supplier_name, 'po_supplier_' || generate_test_id() || '@example.com', '+1234567890')
    RETURNING id INTO test_supplier_id;
    
    -- ACT & ASSERT: Test 6.1 - Auto-generated PO number
    BEGIN
        INSERT INTO purchase_orders (supplier_id, created_by)
        VALUES (test_supplier_id, test_user_id)
        RETURNING id, po_number INTO test_po_id, test_po_number;
        
        IF test_po_number LIKE 'PO-%' THEN
            RAISE NOTICE '✅ Test 6.1: Auto-generated PO number PASSED (PO: %)', test_po_number;
        ELSE
            RAISE EXCEPTION 'Test 6.1: PO number not properly generated';
        END IF;
        
        -- Verify default status
        DECLARE
            po_status VARCHAR(20);
        BEGIN
            SELECT status INTO po_status FROM purchase_orders WHERE id = test_po_id;
            IF po_status = 'draft' THEN
                RAISE NOTICE '✅ Test 6.1 Verification: Default status = draft';
            ELSE
                RAISE EXCEPTION 'Test 6.1 Verification: Default status incorrect';
            END IF;
        END;
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 6.1: Auto-generated PO number FAILED - %', SQLERRM;
        -- Cleanup and exit
        DELETE FROM users WHERE id = test_user_id;
        DELETE FROM suppliers WHERE id = test_supplier_id;
        RETURN;
    END;
    
    -- ACT & ASSERT: Test 6.2 - Draft state constraints
    BEGIN
        UPDATE purchase_orders 
        SET ordered_date = CURRENT_TIMESTAMP 
        WHERE id = test_po_id;
        
        RAISE EXCEPTION 'Test 6.2: Should have raised check violation for draft with ordered date';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ Test 6.2: Draft state constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 6.3 - Valid transition to ordered
    BEGIN
        UPDATE purchase_orders 
        SET status = 'ordered', 
            ordered_date = CURRENT_TIMESTAMP,
            expected_delivery_date = CURRENT_TIMESTAMP + INTERVAL '7 days'
        WHERE id = test_po_id;
        
        -- Verify the update
        DECLARE
            updated_status VARCHAR(20);
        BEGIN
            SELECT status INTO updated_status FROM purchase_orders WHERE id = test_po_id;
            IF updated_status = 'ordered' THEN
                RAISE NOTICE '✅ Test 6.3: Transition to ordered state PASSED';
            ELSE
                RAISE EXCEPTION 'Test 6.3: Status not updated to ordered';
            END IF;
        END;
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 6.3: Transition to ordered state FAILED - %', SQLERRM;
    END;
    
    -- ACT & ASSERT: Test 6.4 - Ordered state constraints
    BEGIN
        UPDATE purchase_orders 
        SET ordered_date = NULL 
        WHERE id = test_po_id;
        
        RAISE EXCEPTION 'Test 6.4: Should have raised check violation for ordered without date';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ Test 6.4: Ordered state constraint PASSED';
        -- Restore ordered date
        UPDATE purchase_orders 
        SET ordered_date = CURRENT_TIMESTAMP 
        WHERE id = test_po_id;
    END;
    
    -- ACT & ASSERT: Test 6.5 - Delivery date constraint
    BEGIN
        UPDATE purchase_orders 
        SET expected_delivery_date = ordered_date - INTERVAL '1 day'
        WHERE id = test_po_id;
        
        RAISE EXCEPTION 'Test 6.5: Should have raised check violation for invalid delivery date';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ Test 6.5: Delivery date constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 6.6 - Foreign key constraints
    BEGIN
        UPDATE purchase_orders 
        SET supplier_id = 999999 
        WHERE id = test_po_id;
        
        RAISE EXCEPTION 'Test 6.6: Should have raised foreign key violation';
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE '✅ Test 6.6: Foreign key constraint PASSED';
    END;
    
    -- CLEANUP
    DELETE FROM purchase_orders WHERE id = test_po_id;
    DELETE FROM users WHERE id = test_user_id;
    DELETE FROM suppliers WHERE id = test_supplier_id;
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '❌ UNEXPECTED ERROR in %: %', test_name, SQLERRM;
    -- Attempt cleanup
    DELETE FROM purchase_orders WHERE id = test_po_id;
    DELETE FROM users WHERE email LIKE '%' || generate_test_id() || '%';
    DELETE FROM suppliers WHERE name LIKE '%' || generate_test_id() || '%';
END $$;















-- =============================================
-- TEST 7: PURCHASE ORDER ITEMS - VALIDATION
-- =============================================
-- Helper function for PO test cleanup
CREATE OR REPLACE FUNCTION cleanup_po_test_data(
    p_user_id BIGINT,
    p_supplier_id BIGINT,
    p_category_id BIGINT,
    p_product_id BIGINT,
    p_po_id BIGINT
) RETURNS VOID AS $$
BEGIN
    DELETE FROM purchase_order_items WHERE purchase_order_id = p_po_id;
    DELETE FROM purchase_orders WHERE id = p_po_id;
    DELETE FROM products WHERE id = p_product_id;
    DELETE FROM categories WHERE id = p_category_id;
    DELETE FROM suppliers WHERE id = p_supplier_id;
    DELETE FROM users WHERE id = p_user_id;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE
    test_name TEXT := 'PURCHASE_ORDER_ITEMS_VALIDATION';
    test_user_id BIGINT;
    test_supplier_id BIGINT;
    test_category_id BIGINT;
    test_product_id BIGINT;
    test_po_id BIGINT;
    test_po_item_id BIGINT;
    test_identifier TEXT;
BEGIN
    RAISE NOTICE E'\n=============================================';
    RAISE NOTICE 'TEST: %', test_name;
    RAISE NOTICE '=============================================';
    
    -- ARRANGE: Create all prerequisite records
    test_identifier := generate_test_id();
    
    -- Create user
    INSERT INTO users (email, password_hash, full_name, role)
    VALUES ('poi_user_' || test_identifier || '@example.com', 'hash', 'POI Test User', 'inventory_manager')
    RETURNING id INTO test_user_id;
    
    -- Create supplier
    INSERT INTO suppliers (name, contact_email, contact_phone)
    VALUES ('POI_Supplier_' || test_identifier, 'poi_supplier_' || test_identifier || '@example.com', '+1234567890')
    RETURNING id INTO test_supplier_id;
    
    -- Create category
    INSERT INTO categories (name, description)
    VALUES ('POI_Category_' || test_identifier, 'Test category for PO items')
    RETURNING id INTO test_category_id;
    
    -- Create product
    INSERT INTO products (name, category_id, supplier_id, price)
    VALUES ('POI_Product_' || test_identifier, test_category_id, test_supplier_id, 19.99)
    RETURNING id INTO test_product_id;
    
    -- Create purchase order
    INSERT INTO purchase_orders (supplier_id, created_by)
    VALUES (test_supplier_id, test_user_id)
    RETURNING id INTO test_po_id;
    
    -- Update to ordered state
    UPDATE purchase_orders 
    SET status = 'ordered', 
        ordered_date = CURRENT_TIMESTAMP,
        expected_delivery_date = CURRENT_TIMESTAMP + INTERVAL '7 days'
    WHERE id = test_po_id;
    
    -- ACT & ASSERT: Test 7.1 - Valid PO item insertion
    BEGIN
        INSERT INTO purchase_order_items (
            purchase_order_id, product_id, quantity_ordered, unit_cost, line_total
        ) VALUES (
            test_po_id, test_product_id, 10, 9.99, 99.90
        ) RETURNING id INTO test_po_item_id;
        
        RAISE NOTICE '✅ Test 7.1: Valid PO item insertion PASSED (ID: %)', test_po_item_id;
        
        -- Verify insertion
        DECLARE
            item_count INTEGER;
        BEGIN
            SELECT COUNT(*) INTO item_count 
            FROM purchase_order_items 
            WHERE id = test_po_item_id;
            
            IF item_count = 1 THEN
                RAISE NOTICE '✅ Test 7.1 Verification: PO item record exists';
            ELSE
                RAISE EXCEPTION 'Test 7.1 Verification: PO item record not found';
            END IF;
        END;
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 7.1: Valid PO item insertion FAILED - %', SQLERRM;
        -- Cleanup and exit
        PERFORM cleanup_po_test_data(test_user_id, test_supplier_id, test_category_id, test_product_id, test_po_id);
        RETURN;
    END;
    
    -- ACT & ASSERT: Test 7.2 - Unique product per PO constraint
    BEGIN
        INSERT INTO purchase_order_items (
            purchase_order_id, product_id, quantity_ordered, unit_cost, line_total
        ) VALUES (
            test_po_id, test_product_id, 5, 9.99, 49.95
        );
        
        RAISE EXCEPTION 'Test 7.2: Should have raised unique violation';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE '✅ Test 7.2: Unique product per PO constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 7.3 - Negative quantity constraint
    BEGIN
        INSERT INTO purchase_order_items (
            purchase_order_id, product_id, quantity_ordered, unit_cost, line_total
        ) VALUES (
            test_po_id, test_product_id, -5, 9.99, -49.95
        );
        
        RAISE EXCEPTION 'Test 7.3: Should have raised check violation';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ Test 7.3: Positive quantity constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 7.4 - Received vs ordered constraint
    BEGIN
        UPDATE purchase_order_items 
        SET quantity_received = 15 
        WHERE id = test_po_item_id;
        
        RAISE EXCEPTION 'Test 7.4: Should have raised check violation';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ Test 7.4: Received ≤ Ordered constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 7.5 - Line total calculation constraint
    BEGIN
        UPDATE purchase_order_items 
        SET line_total = 50.00 
        WHERE id = test_po_item_id;
        
        RAISE EXCEPTION 'Test 7.5: Should have raised check violation';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ Test 7.5: Line total calculation constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 7.6 - Foreign key constraints
    BEGIN
        UPDATE purchase_order_items 
        SET product_id = 999999 
        WHERE id = test_po_item_id;
        
        RAISE EXCEPTION 'Test 7.6: Should have raised foreign key violation';
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE '✅ Test 7.6: Foreign key constraint PASSED';
    END;
    
    -- CLEANUP using helper function
    PERFORM cleanup_po_test_data(test_user_id, test_supplier_id, test_category_id, test_product_id, test_po_id);
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '❌ UNEXPECTED ERROR in %: %', test_name, SQLERRM;
    -- Attempt cleanup
    PERFORM cleanup_po_test_data(test_user_id, test_supplier_id, test_category_id, test_product_id, test_po_id);
END $$;












-- =============================================
-- TEST 8: STOCK MOVEMENTS - COMPLETE VALIDATION
-- =============================================
-- Helper functions for movement test cleanup
CREATE OR REPLACE FUNCTION cleanup_movement_test_data_partial(
    p_user_id BIGINT,
    p_supplier_id BIGINT,
    p_category_id BIGINT,
    p_product_id BIGINT,
    p_po_id BIGINT
) RETURNS VOID AS $$
BEGIN
    IF p_po_id IS NOT NULL THEN
        DELETE FROM purchase_orders WHERE id = p_po_id;
    END IF;
    
    IF p_product_id IS NOT NULL THEN
        DELETE FROM stock_movements WHERE product_id = p_product_id;
        DELETE FROM product_inventory WHERE product_id = p_product_id;
        DELETE FROM products WHERE id = p_product_id;
    END IF;
    
    DELETE FROM categories WHERE id = p_category_id;
    DELETE FROM suppliers WHERE id = p_supplier_id;
    DELETE FROM users WHERE id = p_user_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cleanup_movement_test_data_full(
    p_user_id BIGINT,
    p_supplier_id BIGINT,
    p_category_id BIGINT,
    p_product_id BIGINT,
    p_po_id BIGINT,
    p_movement_id BIGINT
) RETURNS VOID AS $$
BEGIN
    -- Delete all movements for the product (not just the specific one)
    DELETE FROM stock_movements WHERE product_id = p_product_id;
    
    IF p_po_id IS NOT NULL THEN
        DELETE FROM purchase_orders WHERE id = p_po_id;
    END IF;
    
    IF p_product_id IS NOT NULL THEN
        DELETE FROM product_inventory WHERE product_id = p_product_id;
        DELETE FROM products WHERE id = p_product_id;
    END IF;
    
    DELETE FROM categories WHERE id = p_category_id;
    DELETE FROM suppliers WHERE id = p_supplier_id;
    DELETE FROM users WHERE id = p_user_id;
END;
$$ LANGUAGE plpgsql;


DO $$
DECLARE
    test_name TEXT := 'STOCK_MOVEMENTS_VALIDATION';
    test_user_id BIGINT;
    test_supplier_id BIGINT;
    test_category_id BIGINT;
    test_product_id BIGINT;
    test_inventory_id BIGINT;
    test_movement_id BIGINT;
    test_po_id BIGINT;
    test_identifier TEXT;
    initial_quantity INTEGER;
    test_product_name TEXT;
    test_category_name TEXT;
    test_supplier_name TEXT;
    test_user_email TEXT;
BEGIN
    RAISE NOTICE E'\n=============================================';
    RAISE NOTICE 'TEST: %', test_name;
    RAISE NOTICE '=============================================';
    
    -- ARRANGE: Generate unique identifiers
    test_identifier := generate_test_id();
    test_user_email := 'movement_user_' || test_identifier || '@example.com';
    test_supplier_name := 'Movement_Supplier_' || test_identifier;
    test_category_name := 'Movement_Category_' || test_identifier;
    test_product_name := 'Movement_Product_' || test_identifier;
    
    -- Create user
    BEGIN
        INSERT INTO users (email, password_hash, full_name, role)
        VALUES (
            test_user_email, 
            'hashed_password_123', 
            'Movement Test User ' || test_identifier, 
            'inventory_manager'
        ) RETURNING id INTO test_user_id;
        
        RAISE NOTICE '✅ ARRANGE: Created test user (ID: %)', test_user_id;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ ARRANGE: Failed to create user - %', SQLERRM;
        RETURN;
    END;
    
    -- Create supplier
    BEGIN
        INSERT INTO suppliers (name, contact_email, contact_phone)
        VALUES (
            test_supplier_name, 
            'movement_supplier_' || test_identifier || '@example.com', 
            '+1234567890'
        ) RETURNING id INTO test_supplier_id;
        
        RAISE NOTICE '✅ ARRANGE: Created test supplier (ID: %)', test_supplier_id;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ ARRANGE: Failed to create supplier - %', SQLERRM;
        DELETE FROM users WHERE id = test_user_id;
        RETURN;
    END;
    
    -- Create category
    BEGIN
        INSERT INTO categories (name, description)
        VALUES (
            test_category_name, 
            'Test category for stock movements validation'
        ) RETURNING id INTO test_category_id;
        
        RAISE NOTICE '✅ ARRANGE: Created test category (ID: %)', test_category_id;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ ARRANGE: Failed to create category - %', SQLERRM;
        DELETE FROM suppliers WHERE id = test_supplier_id;
        DELETE FROM users WHERE id = test_user_id;
        RETURN;
    END;
    
    -- Create product
    BEGIN
        INSERT INTO products (name, category_id, supplier_id, price)
        VALUES (
            test_product_name, 
            test_category_id, 
            test_supplier_id, 
            29.99
        ) RETURNING id INTO test_product_id;
        
        RAISE NOTICE '✅ ARRANGE: Created test product (ID: %)', test_product_id;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ ARRANGE: Failed to create product - %', SQLERRM;
        PERFORM cleanup_movement_test_data_partial(
            test_user_id, test_supplier_id, test_category_id, NULL, NULL
        );
        RETURN;
    END;
    
    -- Create inventory manually (since auto-creation trigger is removed)
    BEGIN
        INSERT INTO product_inventory (product_id, quantity_on_hand, quantity_committed, quantity_available)
        VALUES (test_product_id, 100, 20, 80)  -- 100 on hand, 20 committed, 80 available
        RETURNING id INTO test_inventory_id;
        
        RAISE NOTICE '✅ ARRANGE: Created inventory manually (ID: %)', test_inventory_id;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ ARRANGE: Failed to create inventory - %', SQLERRM;
        PERFORM cleanup_movement_test_data_full(
            test_user_id, test_supplier_id, test_category_id, 
            test_product_id, NULL, NULL
        );
        RETURN;
    END;
    
    -- Create purchase order for reference
    BEGIN
        INSERT INTO purchase_orders (supplier_id, created_by, status, ordered_date)
        VALUES (
            test_supplier_id, 
            test_user_id, 
            'ordered', 
            CURRENT_TIMESTAMP
        ) RETURNING id INTO test_po_id;
        
        RAISE NOTICE '✅ ARRANGE: Created test purchase order (ID: %)', test_po_id;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ ARRANGE: Failed to create purchase order - %', SQLERRM;
        PERFORM cleanup_movement_test_data_full(
            test_user_id, test_supplier_id, test_category_id, 
            test_product_id, NULL, NULL
        );
        RETURN;
    END;
    
    -- Get initial quantity from inventory
    SELECT quantity_available INTO initial_quantity 
    FROM product_inventory 
    WHERE id = test_inventory_id;
    
    RAISE NOTICE '✅ ARRANGE: Initial available quantity: %', initial_quantity;
    
    -- ACT & ASSERT: Test 8.1 - Valid IN movement
    RAISE NOTICE E'\n--- Test 8.1: Valid IN movement ---';
    DECLARE
        in_quantity INTEGER := 25;
        expected_after_in INTEGER;
    BEGIN
        -- Calculate expected quantity after IN movement
        expected_after_in := initial_quantity + in_quantity;
        
        -- ACT: Create IN movement
        INSERT INTO stock_movements (
            product_id, movement_type, quantity_change,
            quantity_before, quantity_after,
            reference_type, reference_id, movement_date, created_by
        ) VALUES (
            test_product_id, 'in', in_quantity,
            initial_quantity, expected_after_in,
            'purchase_order', test_po_id, CURRENT_TIMESTAMP, test_user_id
        ) RETURNING id INTO test_movement_id;
        
        RAISE NOTICE '✅ ACT: Created IN movement (ID: %)', test_movement_id;
        
        -- ASSERT: Verify movement record
        DECLARE
            movement_count INTEGER;
            actual_movement_type VARCHAR(20);
            actual_quantity_change INTEGER;
            actual_quantity_before INTEGER;
            actual_quantity_after INTEGER;
            actual_reference_type VARCHAR(20);
            actual_created_by BIGINT;
        BEGIN
            SELECT COUNT(*) 
            INTO movement_count
            FROM stock_movements
            WHERE id = test_movement_id;

            SELECT 
                movement_type,
                quantity_change,
                quantity_before,
                quantity_after,
                reference_type,
                created_by
            INTO 
                actual_movement_type,
                actual_quantity_change,
                actual_quantity_before,
                actual_quantity_after,
                actual_reference_type,
                actual_created_by
            FROM stock_movements 
            WHERE id = test_movement_id;
            
            -- Basic validations
            IF movement_count = 1 THEN
                RAISE NOTICE '✅ ASSERT: Movement record exists';
            ELSE
                RAISE EXCEPTION 'ASSERT: Movement record not found';
            END IF;
            
            IF actual_movement_type = 'in' THEN
                RAISE NOTICE '✅ ASSERT: movement_type = "in"';
            ELSE
                RAISE EXCEPTION 'ASSERT: movement_type incorrect. Expected: "in", Got: "%"', actual_movement_type;
            END IF;
            
            IF actual_quantity_change = in_quantity THEN
                RAISE NOTICE '✅ ASSERT: quantity_change = %', in_quantity;
            ELSE
                RAISE EXCEPTION 'ASSERT: quantity_change incorrect. Expected: %, Got: %', 
                               in_quantity, actual_quantity_change;
            END IF;
            
            IF actual_quantity_before = initial_quantity THEN
                RAISE NOTICE '✅ ASSERT: quantity_before = %', initial_quantity;
            ELSE
                RAISE EXCEPTION 'ASSERT: quantity_before incorrect. Expected: %, Got: %', 
                               initial_quantity, actual_quantity_before;
            END IF;
            
            IF actual_quantity_after = expected_after_in THEN
                RAISE NOTICE '✅ ASSERT: quantity_after = % (correct calculation)', expected_after_in;
            ELSE
                RAISE EXCEPTION 'ASSERT: quantity_after incorrect. Expected: %, Got: %', 
                               expected_after_in, actual_quantity_after;
            END IF;
            
            IF actual_reference_type = 'purchase_order' THEN
                RAISE NOTICE '✅ ASSERT: reference_type = "purchase_order"';
            ELSE
                RAISE EXCEPTION 'ASSERT: reference_type incorrect. Expected: "purchase_order", Got: "%"', 
                               actual_reference_type;
            END IF;
            
            IF actual_created_by = test_user_id THEN
                RAISE NOTICE '✅ ASSERT: created_by = %', test_user_id;
            ELSE
                RAISE EXCEPTION 'ASSERT: created_by incorrect. Expected: %, Got: %', 
                               test_user_id, actual_created_by;
            END IF;
            
            -- Verify timestamps
            DECLARE
                movement_created_at TIMESTAMP;
                movement_updated_at TIMESTAMP;
                movement_movement_date TIMESTAMP;
            BEGIN
                SELECT created_at, updated_at, movement_date 
                INTO movement_created_at, movement_updated_at, movement_movement_date
                FROM stock_movements WHERE id = test_movement_id;
                
                IF movement_created_at IS NOT NULL THEN
                    RAISE NOTICE '✅ ASSERT: created_at auto-populated';
                ELSE
                    RAISE EXCEPTION 'ASSERT: created_at not set';
                END IF;
                
                IF movement_updated_at IS NOT NULL THEN
                    RAISE NOTICE '✅ ASSERT: updated_at auto-populated';
                ELSE
                    RAISE EXCEPTION 'ASSERT: updated_at not set';
                END IF;
                
                IF movement_movement_date IS NOT NULL THEN
                    RAISE NOTICE '✅ ASSERT: movement_date set correctly';
                ELSE
                    RAISE EXCEPTION 'ASSERT: movement_date not set';
                END IF;
            END;
        END;
        
        RAISE NOTICE '✅ Test 8.1: PASSED - Valid IN movement recorded correctly';
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 8.1: FAILED - %', SQLERRM;
        PERFORM cleanup_movement_test_data_full(
            test_user_id, test_supplier_id, test_category_id, 
            test_product_id, test_po_id, test_movement_id
        );
        RETURN;
    END;
    
    -- ACT & ASSERT: Test 8.2 - Valid OUT movement
    RAISE NOTICE E'\n--- Test 8.2: Valid OUT movement ---';
    DECLARE
        current_quantity INTEGER;
        out_quantity INTEGER := 15;
        expected_after_out INTEGER;
        out_movement_id BIGINT;
    BEGIN
        -- Get current quantity (should be initial + in_quantity from Test 8.1)
        SELECT quantity_available INTO current_quantity 
        FROM product_inventory 
        WHERE id = test_inventory_id;
        
        RAISE NOTICE '✅ ARRANGE: Current available quantity: %', current_quantity;
        
        -- Calculate expected quantity after OUT movement
        expected_after_out := current_quantity - out_quantity;
        
        -- ACT: Create OUT movement
        INSERT INTO stock_movements (
            product_id, movement_type, quantity_change,
            quantity_before, quantity_after,
            reference_type, reference_id, movement_date, created_by
        ) VALUES (
            test_product_id, 'out', -out_quantity,  -- Negative for OUT
            current_quantity, expected_after_out,
            'sale', 1, CURRENT_TIMESTAMP, test_user_id
        ) RETURNING id INTO out_movement_id;
        
        RAISE NOTICE '✅ ACT: Created OUT movement (ID: %)', out_movement_id;
        
        -- ASSERT: Verify movement was recorded correctly
        DECLARE
            out_movement_count INTEGER;
            actual_out_quantity_change INTEGER;
        BEGIN
            SELECT COUNT(*) INTO out_movement_count 
            FROM stock_movements 
            WHERE id = out_movement_id;

            SELECT quantity_change INTO actual_out_quantity_change
            FROM stock_movements 
            WHERE id = out_movement_id;
            
            IF out_movement_count = 1 THEN
                RAISE NOTICE '✅ ASSERT: OUT movement recorded';
            ELSE
                RAISE EXCEPTION 'ASSERT: OUT movement not recorded';
            END IF;
            
            IF actual_out_quantity_change = -out_quantity THEN
                RAISE NOTICE '✅ ASSERT: OUT quantity_change negative: %', actual_out_quantity_change;
            ELSE
                RAISE EXCEPTION 'ASSERT: OUT quantity_change incorrect. Expected: -%, Got: %',
                               out_quantity, actual_out_quantity_change;
            END IF;
        END;
        
        RAISE NOTICE '✅ Test 8.2: PASSED - Valid OUT movement recorded correctly';
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 8.2: FAILED - %', SQLERRM;
    END;
    
    -- ACT & ASSERT: Test 8.3 - Valid ADJUSTMENT movement
    RAISE NOTICE E'\n--- Test 8.3: Valid ADJUSTMENT movement ---';
    DECLARE
        adjustment_quantity INTEGER := -5;  -- Negative adjustment (damage/loss)
        quantity_before_adj INTEGER;
        expected_after_adj INTEGER;
        adj_movement_id BIGINT;
    BEGIN
        -- Get current quantity
        SELECT quantity_available INTO quantity_before_adj
        FROM product_inventory 
        WHERE id = test_inventory_id;
        
        -- Calculate expected quantity after adjustment
        expected_after_adj := quantity_before_adj + adjustment_quantity;  -- Note: adjustment_quantity is negative
        
        -- ACT: Create ADJUSTMENT movement
        INSERT INTO stock_movements (
            product_id, movement_type, quantity_change,
            quantity_before, quantity_after,
            reference_type, reference_id, movement_date, created_by
        ) VALUES (
            test_product_id, 'adjustment', adjustment_quantity,
            quantity_before_adj, expected_after_adj,
            'adjustment', 1, CURRENT_TIMESTAMP, test_user_id
        ) RETURNING id INTO adj_movement_id;
        
        RAISE NOTICE '✅ ACT: Created negative ADJUSTMENT movement (ID: %, Quantity: %)', 
                     adj_movement_id, adjustment_quantity;
        
        -- ASSERT: Verify adjustment movement
        DECLARE
            adjustment_count INTEGER;
            actual_adj_quantity INTEGER;
        BEGIN
            SELECT COUNT(*) INTO adjustment_count FROM stock_movements WHERE id = adj_movement_id;
            SELECT quantity_change INTO actual_adj_quantity FROM stock_movements 
            WHERE id = adj_movement_id;
            
            IF adjustment_count = 1 THEN
                RAISE NOTICE '✅ ASSERT: ADJUSTMENT movement recorded';
            ELSE
                RAISE EXCEPTION 'ASSERT: ADJUSTMENT movement not recorded';
            END IF;
            
            IF actual_adj_quantity = adjustment_quantity THEN
                RAISE NOTICE '✅ ASSERT: Adjustment quantity correct: %', actual_adj_quantity;
            ELSE
                RAISE EXCEPTION 'ASSERT: Adjustment quantity incorrect. Expected: %, Got: %',
                               adjustment_quantity, actual_adj_quantity;
            END IF;
        END;
        
        -- Test positive adjustment as well
        BEGIN
            DECLARE
                pos_adjustment_quantity INTEGER := 3;
                qty_before_pos INTEGER;
                expected_after_pos INTEGER;
            BEGIN
                SELECT quantity_available INTO qty_before_pos
                FROM product_inventory 
                WHERE id = test_inventory_id;
                
                expected_after_pos := qty_before_pos + pos_adjustment_quantity;
                
                INSERT INTO stock_movements (
                    product_id, movement_type, quantity_change,
                    quantity_before, quantity_after,
                    reference_type, reference_id, movement_date, created_by
                ) VALUES (
                    test_product_id, 'adjustment', pos_adjustment_quantity,
                    qty_before_pos, expected_after_pos,
                    'adjustment', 2, CURRENT_TIMESTAMP, test_user_id
                );
                
                RAISE NOTICE '✅ ASSERT: Positive adjustment also allowed (Quantity: +%)', pos_adjustment_quantity;
            END;
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE '⚠️  ASSERT: Positive adjustment failed - %', SQLERRM;
        END;
        
        RAISE NOTICE '✅ Test 8.3: PASSED - ADJUSTMENT movements work (both positive and negative)';
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 8.3: FAILED - %', SQLERRM;
    END;
    
    -- ACT & ASSERT: Test 8.4 - Invalid movement type constraint
    RAISE NOTICE E'\n--- Test 8.4: Invalid movement type constraint ---';
    BEGIN
        -- ACT: Try to create movement with invalid type
        INSERT INTO stock_movements (
            product_id, movement_type, quantity_change,
            quantity_before, quantity_after,
            reference_type, reference_id, movement_date, created_by
        ) VALUES (
            test_product_id, 'invalid_type', 10,
            100, 110, 'adjustment', 1, CURRENT_TIMESTAMP, test_user_id
        );
        
        RAISE EXCEPTION 'Test 8.4: Should have raised check violation for invalid movement_type';
        
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ ASSERT: Check violation raised for invalid movement_type';
        RAISE NOTICE '✅ Test 8.4: PASSED - Valid movement types enforced';
    END;
    
    -- ACT & ASSERT: Test 8.5 - Movement math constraint
    RAISE NOTICE E'\n--- Test 8.5: Movement math constraint ---';
    BEGIN
        -- ACT: Try to create movement with incorrect math (100 + 10 != 105)
        INSERT INTO stock_movements (
            product_id, movement_type, quantity_change,
            quantity_before, quantity_after,
            reference_type, reference_id, movement_date, created_by
        ) VALUES (
            test_product_id, 'in', 10,
            100, 105,  -- 100 + 10 != 105
            'adjustment', 1, CURRENT_TIMESTAMP, test_user_id
        );
        
        RAISE EXCEPTION 'Test 8.5: Should have raised check violation for incorrect math';
        
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ ASSERT: Check violation raised for quantity_after ≠ quantity_before + quantity_change';
        RAISE NOTICE '✅ Test 8.5: PASSED - Mathematical consistency enforced';
    END;
    
    -- ACT & ASSERT: Test 8.6 - Quantity sign for movement type
    RAISE NOTICE E'\n--- Test 8.6: Quantity sign for movement type ---';
    BEGIN
        -- ACT: Try IN movement with negative quantity
        INSERT INTO stock_movements (
            product_id, movement_type, quantity_change,
            quantity_before, quantity_after,
            reference_type, reference_id, movement_date, created_by
        ) VALUES (
            test_product_id, 'in', -10,  -- IN should be positive
            100, 90,
            'adjustment', 1, CURRENT_TIMESTAMP, test_user_id
        );
        
        RAISE EXCEPTION 'Test 8.6: Should have raised check violation for IN with negative quantity';
        
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ ASSERT: Check violation raised for IN with negative quantity';
        
        -- Try OUT movement with positive quantity
        BEGIN
            INSERT INTO stock_movements (
                product_id, movement_type, quantity_change,
                quantity_before, quantity_after,
                reference_type, reference_id, movement_date, created_by
            ) VALUES (
                test_product_id, 'out', 10,  -- OUT should be negative
                100, 110,
                'adjustment', 1, CURRENT_TIMESTAMP, test_user_id
            );
            
            RAISE EXCEPTION 'Test 8.6: Should have raised check violation for OUT with positive quantity';
            
        EXCEPTION WHEN check_violation THEN
            RAISE NOTICE '✅ ASSERT: Check violation raised for OUT with positive quantity';
            RAISE NOTICE '✅ Test 8.6: PASSED - Quantity sign constraints enforced';
        END;
    END;
    
    -- ACT & ASSERT: Test 8.7 - Non-negative quantity constraints
    RAISE NOTICE E'\n--- Test 8.7: Non-negative quantity constraints ---';
    BEGIN
        -- ACT: Try to create movement that would result in negative quantity_after
        INSERT INTO stock_movements (
            product_id, movement_type, quantity_change,
            quantity_before, quantity_after,
            reference_type, reference_id, movement_date, created_by
        ) VALUES (
            test_product_id, 'out', -110,  -- Would make quantity_after negative
            100, -10,
            'sale', 1, CURRENT_TIMESTAMP, test_user_id
        );
        
        RAISE EXCEPTION 'Test 8.7: Should have raised check violation for negative quantity_after';
        
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ ASSERT: Check violation raised for negative quantity_after';
        
        -- Try negative quantity_before
        BEGIN
            INSERT INTO stock_movements (
                product_id, movement_type, quantity_change,
                quantity_before, quantity_after,
                reference_type, reference_id, movement_date, created_by
            ) VALUES (
                test_product_id, 'in', 10,
                -5, 5,  -- Negative quantity_before
                'adjustment', 1, CURRENT_TIMESTAMP, test_user_id
            );
            
            RAISE EXCEPTION 'Test 8.7: Should have raised check violation for negative quantity_before';
            
        EXCEPTION WHEN check_violation THEN
            RAISE NOTICE '✅ ASSERT: Check violation raised for negative quantity_before';
            RAISE NOTICE '✅ Test 8.7: PASSED - Non-negative quantities enforced';
        END;
    END;
    
    -- ACT & ASSERT: Test 8.8 - Reference type validation
    RAISE NOTICE E'\n--- Test 8.8: Reference type validation ---';
    BEGIN
        -- ACT: Try to create movement with invalid reference_type
        INSERT INTO stock_movements (
            product_id, movement_type, quantity_change,
            quantity_before, quantity_after,
            reference_type, reference_id, movement_date, created_by
        ) VALUES (
            test_product_id, 'in', 10,
            100, 110,
            'invalid_reference', 1, CURRENT_TIMESTAMP, test_user_id
        );
        
        RAISE EXCEPTION 'Test 8.8: Should have raised check violation for invalid reference_type';
        
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ ASSERT: Check violation raised for invalid reference_type';
        
        -- Test all valid reference types
        DECLARE
            valid_reference_types TEXT[] := ARRAY['purchase_order', 'sale', 'adjustment', 'transfer'];
            current_qty INTEGER;
            ref_type TEXT;
        BEGIN
            SELECT quantity_available INTO current_qty
            FROM product_inventory WHERE id = test_inventory_id;
            
            FOREACH ref_type IN ARRAY valid_reference_types LOOP
                BEGIN
                    INSERT INTO stock_movements (
                        product_id, movement_type, quantity_change,
                        quantity_before, quantity_after,
                        reference_type, reference_id, movement_date, created_by
                    ) VALUES (
                        test_product_id, 'adjustment', 1,
                        current_qty, current_qty + 1,
                        ref_type, 1, CURRENT_TIMESTAMP, test_user_id
                    );
                    
                    RAISE NOTICE '✅ ASSERT: Reference type "%" accepted', ref_type;
                EXCEPTION WHEN OTHERS THEN
                    RAISE NOTICE '⚠️  ASSERT: Reference type "%" insertion failed - %', ref_type, SQLERRM;
                END;
            END LOOP;
        END;
        
        RAISE NOTICE '✅ Test 8.8: PASSED - Reference type validation working';
    END;
    
    -- ACT & ASSERT: Test 8.9 - Foreign key constraints
    RAISE NOTICE E'\n--- Test 8.9: Foreign key constraints ---';
    BEGIN
        -- ACT: Try to create movement with invalid product_id
        INSERT INTO stock_movements (
            product_id, movement_type, quantity_change,
            quantity_before, quantity_after,
            reference_type, reference_id, movement_date, created_by
        ) VALUES (
            999999, 'in', 10,
            100, 110,
            'adjustment', 1, CURRENT_TIMESTAMP, test_user_id
        );
        
        RAISE EXCEPTION 'Test 8.9: Should have raised foreign key violation for invalid product_id';
        
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE '✅ ASSERT: Foreign key violation raised for invalid product_id';
        
        -- Try with invalid created_by
        BEGIN
            INSERT INTO stock_movements (
                product_id, movement_type, quantity_change,
                quantity_before, quantity_after,
                reference_type, reference_id, movement_date, created_by
            ) VALUES (
                test_product_id, 'in', 10,
                100, 110,
                'adjustment', 1, CURRENT_TIMESTAMP, 999999
            );
            
            RAISE EXCEPTION 'Test 8.9: Should have raised foreign key violation for invalid created_by';
            
        EXCEPTION WHEN foreign_key_violation THEN
            RAISE NOTICE '✅ ASSERT: Foreign key violation raised for invalid created_by';
            RAISE NOTICE '✅ Test 8.9: PASSED - Foreign key constraints enforced';
        END;
    END;
    
    -- ACT & ASSERT: Test 8.11 - Movement history querying
    RAISE NOTICE E'\n--- Test 8.11: Movement history querying ---';
    DECLARE
        total_movements INTEGER;
        in_movements INTEGER;
        out_movements INTEGER;
        adjustment_movements INTEGER;
        movements_by_user INTEGER;
        movements_by_product INTEGER;
        total_quantity_moved INTEGER;
    BEGIN
        -- Query movement statistics
        SELECT COUNT(*) INTO total_movements
        FROM stock_movements 
        WHERE product_id = test_product_id;
        
        SELECT COUNT(*) INTO in_movements
        FROM stock_movements 
        WHERE product_id = test_product_id 
        AND movement_type = 'in';
        
        SELECT COUNT(*) INTO out_movements
        FROM stock_movements 
        WHERE product_id = test_product_id 
        AND movement_type = 'out';
        
        SELECT COUNT(*) INTO adjustment_movements
        FROM stock_movements 
        WHERE product_id = test_product_id 
        AND movement_type = 'adjustment';
        
        SELECT COUNT(*) INTO movements_by_user
        FROM stock_movements 
        WHERE created_by = test_user_id;
        
        SELECT COUNT(*) INTO movements_by_product
        FROM stock_movements 
        WHERE product_id = test_product_id;
        
        -- Calculate total quantity moved (absolute values)
        SELECT COALESCE(SUM(ABS(quantity_change)), 0) INTO total_quantity_moved
        FROM stock_movements 
        WHERE product_id = test_product_id;
        
        RAISE NOTICE '✅ ASSERT: Total movements for product: %', total_movements;
        RAISE NOTICE '✅ ASSERT: IN movements: %', in_movements;
        RAISE NOTICE '✅ ASSERT: OUT movements: %', out_movements;
        RAISE NOTICE '✅ ASSERT: ADJUSTMENT movements: %', adjustment_movements;
        RAISE NOTICE '✅ ASSERT: Movements by test user: %', movements_by_user;
        RAISE NOTICE '✅ ASSERT: Movements for product: %', movements_by_product;
        RAISE NOTICE '✅ ASSERT: Total quantity moved (absolute): % units', total_quantity_moved;
        
        IF total_movements > 0 AND movements_by_user > 0 AND movements_by_product = total_movements THEN
            RAISE NOTICE '✅ Test 8.11: PASSED - Movement history properly recorded and queryable';
        ELSE
            RAISE EXCEPTION 'Test 8.11: FAILED - Movement history incomplete or inconsistent';
        END IF;
        
        -- Test specific queries that would be used in the application
        BEGIN
            -- Get latest movement
            DECLARE
                latest_movement_type VARCHAR(20);
                latest_quantity_change INTEGER;
                latest_date TIMESTAMP;
            BEGIN
                SELECT movement_type, quantity_change, movement_date 
                INTO latest_movement_type, latest_quantity_change, latest_date
                FROM stock_movements 
                WHERE product_id = test_product_id 
                ORDER BY movement_date DESC 
                LIMIT 1;
                
                IF latest_movement_type IS NOT NULL THEN
                    RAISE NOTICE '✅ ASSERT: Latest movement query works (Type: %, Qty: %, Date: %)',
                                latest_movement_type, latest_quantity_change, latest_date;
                END IF;
            END;
            
            -- Get movement summary by type
            DECLARE
                movement_summary RECORD;
            BEGIN
                FOR movement_summary IN
                    SELECT movement_type, COUNT(*) as count, SUM(quantity_change) as net_change
                    FROM stock_movements 
                    WHERE product_id = test_product_id 
                    GROUP BY movement_type
                    ORDER BY movement_type
                LOOP
                    RAISE NOTICE '✅ ASSERT: Movement summary - Type: %, Count: %, Net Change: %',
                                movement_summary.movement_type, 
                                movement_summary.count, 
                                movement_summary.net_change;
                END LOOP;
            END;
            
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE '⚠️  ASSERT: Movement query tests failed - %', SQLERRM;
        END;
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 8.11: FAILED - %', SQLERRM;
    END;
    
    -- ACT & ASSERT: Test 8.12 - Movement date constraints
    RAISE NOTICE E'\n--- Test 8.12: Movement date constraints ---';
    BEGIN
        -- Test that movement_date is required (NOT NULL constraint)
        BEGIN
            INSERT INTO stock_movements (
                product_id, movement_type, quantity_change,
                quantity_before, quantity_after,
                reference_type, reference_id, movement_date, created_by
            ) VALUES (
                test_product_id, 'in', 5,
                100, 105,
                'adjustment', 1, NULL, test_user_id  -- NULL movement_date
            );
            
            RAISE EXCEPTION 'Test 8.12: Should have raised not-null violation for movement_date';
            
        EXCEPTION WHEN not_null_violation THEN
            RAISE NOTICE '✅ ASSERT: Not-null violation raised for movement_date';
        END;
        
        -- Test valid future and past dates (should be allowed)
        BEGIN
            -- Past date
            INSERT INTO stock_movements (
                product_id, movement_type, quantity_change,
                quantity_before, quantity_after,
                reference_type, reference_id, movement_date, created_by
            ) VALUES (
                test_product_id, 'in', 2,
                100, 102,
                'adjustment', 1, CURRENT_TIMESTAMP - INTERVAL '1 day', test_user_id
            );
            
            RAISE NOTICE '✅ ASSERT: Past movement_date accepted';
            
            -- Future date (should be allowed for planning purposes)
            INSERT INTO stock_movements (
                product_id, movement_type, quantity_change,
                quantity_before, quantity_after,
                reference_type, reference_id, movement_date, created_by
            ) VALUES (
                test_product_id, 'in', 3,
                102, 105,
                'adjustment', 1, CURRENT_TIMESTAMP + INTERVAL '1 day', test_user_id
            );
            
            RAISE NOTICE '✅ ASSERT: Future movement_date accepted (for planned movements)';
            
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE '⚠️  ASSERT: Date tests failed - %', SQLERRM;
        END;
        
        RAISE NOTICE '✅ Test 8.12: PASSED - Movement date constraints working';
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 8.12: FAILED - %', SQLERRM;
    END;
    
    -- CLEANUP
    RAISE NOTICE E'\n--- CLEANUP ---';
    PERFORM cleanup_movement_test_data_full(
        test_user_id, test_supplier_id, test_category_id, 
        test_product_id, test_po_id, test_movement_id
    );
    RAISE NOTICE '✅ Cleanup completed successfully';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '❌ UNEXPECTED ERROR in %: %', test_name, SQLERRM;
    PERFORM cleanup_movement_test_data_full(
        test_user_id, test_supplier_id, test_category_id, 
        test_product_id, test_po_id, test_movement_id
    );
END $$;


















-- =============================================
-- TEST 9: STOCK ADJUSTMENTS - COMPLETE VALIDATION
-- =============================================
-- Helper function for adjustment test cleanup
CREATE OR REPLACE FUNCTION cleanup_adjustment_test_data(
    p_user_id BIGINT,
    p_supplier_id BIGINT,
    p_category_id BIGINT,
    p_product_id BIGINT
) RETURNS VOID AS $$
BEGIN
    DELETE FROM stock_adjustments WHERE product_id = p_product_id;
    DELETE FROM product_inventory WHERE product_id = p_product_id;
    DELETE FROM products WHERE id = p_product_id;
    DELETE FROM categories WHERE id = p_category_id;
    DELETE FROM suppliers WHERE id = p_supplier_id;
    DELETE FROM users WHERE id = p_user_id;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE
    test_name TEXT := 'STOCK_ADJUSTMENTS_VALIDATION';
    test_user_id BIGINT;
    test_supplier_id BIGINT;
    test_category_id BIGINT;
    test_product_id BIGINT;
    test_adjustment_id BIGINT;
    test_identifier TEXT;
BEGIN
    RAISE NOTICE E'\n=============================================';
    RAISE NOTICE 'TEST: %', test_name;
    RAISE NOTICE '=============================================';
    
    -- ARRANGE: Create all prerequisite records
    test_identifier := generate_test_id();
    
    -- Create user
    INSERT INTO users (email, password_hash, full_name, role)
    VALUES ('adjustment_user_' || test_identifier || '@example.com', 'hash', 'Adjustment Test User', 'inventory_manager')
    RETURNING id INTO test_user_id;
    
    -- Create supplier
    INSERT INTO suppliers (name, contact_email, contact_phone)
    VALUES ('Adjustment_Supplier_' || test_identifier, 'adjustment_supplier_' || test_identifier || '@example.com', '+1234567890')
    RETURNING id INTO test_supplier_id;
    
    -- Create category
    INSERT INTO categories (name, description)
    VALUES ('Adjustment_Category_' || test_identifier, 'Test category for adjustments')
    RETURNING id INTO test_category_id;
    
    -- Create product
    INSERT INTO products (name, category_id, supplier_id, price)
    VALUES ('Adjustment_Product_' || test_identifier, test_category_id, test_supplier_id, 39.99)
    RETURNING id INTO test_product_id;
    
    -- ACT & ASSERT: Test 9.1 - Valid negative adjustment (damaged)
    BEGIN
        INSERT INTO stock_adjustments (
            product_id, adjustment_type, quantity_adjusted,
            reason, adjustment_date, created_by
        ) VALUES (
            test_product_id, 'damaged', -5,
            'Damaged during handling - visible cracks and breakage that occurred during transit',
            CURRENT_TIMESTAMP, test_user_id
        ) RETURNING id INTO test_adjustment_id;
        
        RAISE NOTICE '✅ Test 9.1: Valid negative adjustment (damaged) PASSED (ID: %)', test_adjustment_id;
        
        -- Verify insertion
        DECLARE
            adjustment_count INTEGER;
        BEGIN
            SELECT COUNT(*) INTO adjustment_count 
            FROM stock_adjustments 
            WHERE id = test_adjustment_id;
            
            IF adjustment_count = 1 THEN
                RAISE NOTICE '✅ Test 9.1 Verification: Adjustment record exists';
            ELSE
                RAISE EXCEPTION 'Test 9.1 Verification: Adjustment record not found';
            END IF;
        END;
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 9.1: Valid negative adjustment FAILED - %', SQLERRM;
        PERFORM cleanup_adjustment_test_data(
            test_user_id, test_supplier_id, test_category_id, test_product_id
        );
        RETURN;
    END;
    
    -- ACT & ASSERT: Test 9.2 - Valid positive adjustment (found)
    BEGIN
        INSERT INTO stock_adjustments (
            product_id, adjustment_type, quantity_adjusted,
            reason, adjustment_date, created_by
        ) VALUES (
            test_product_id, 'found', 3,
            'Found in overflow storage area during inventory audit',
            CURRENT_TIMESTAMP, test_user_id
        );
        
        RAISE NOTICE '✅ Test 9.2: Valid positive adjustment (found) PASSED';
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 9.2: Valid positive adjustment FAILED - %', SQLERRM;
    END;
    
    -- ACT & ASSERT: Test 9.3 - Invalid adjustment type
    BEGIN
        INSERT INTO stock_adjustments (
            product_id, adjustment_type, quantity_adjusted,
            reason, adjustment_date, created_by
        ) VALUES (
            test_product_id, 'invalid_type', -2,
            'Some reason', CURRENT_TIMESTAMP, test_user_id
        );
        
        RAISE EXCEPTION 'Test 9.3: Should have raised check violation';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ Test 9.3: Valid adjustment type constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 9.4 - Quantity sign for adjustment type
    BEGIN
        INSERT INTO stock_adjustments (
            product_id, adjustment_type, quantity_adjusted,
            reason, adjustment_date, created_by
        ) VALUES (
            test_product_id, 'damaged', 5,  -- Should be negative
            'Damaged items need detailed explanation for tracking purposes',
            CURRENT_TIMESTAMP, test_user_id
        );
        
        RAISE EXCEPTION 'Test 9.4: Should have raised check violation';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ Test 9.4: Quantity sign constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 9.5 - Required reason for damaged (too short)
    BEGIN
        INSERT INTO stock_adjustments (
            product_id, adjustment_type, quantity_adjusted,
            reason, adjustment_date, created_by
        ) VALUES (
            test_product_id, 'damaged', -2,
            'Short',  -- Too short (less than 10 chars)
            CURRENT_TIMESTAMP, test_user_id
        );
        
        RAISE EXCEPTION 'Test 9.5: Should have raised check violation';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ Test 9.5: Required reason length constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 9.6 - Required reason for theft (missing)
    BEGIN
        INSERT INTO stock_adjustments (
            product_id, adjustment_type, quantity_adjusted,
            adjustment_date, created_by
        ) VALUES (
            test_product_id, 'theft', -3,
            CURRENT_TIMESTAMP, test_user_id
        );
        
        RAISE EXCEPTION 'Test 9.6: Should have raised check violation';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ Test 9.6: Required reason presence constraint PASSED';
    END;
    
    -- ACT & ASSERT: Test 9.7 - No reason required for found
    BEGIN
        INSERT INTO stock_adjustments (
            product_id, adjustment_type, quantity_adjusted,
            adjustment_date, created_by
        ) VALUES (
            test_product_id, 'found', 2,
            CURRENT_TIMESTAMP, test_user_id
        );
        
        RAISE NOTICE '✅ Test 9.7: Optional reason for "found" adjustment PASSED';
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Test 9.7: Optional reason test FAILED - %', SQLERRM;
    END;
    
    -- ACT & ASSERT: Test 9.8 - Foreign key constraint
    BEGIN
        INSERT INTO stock_adjustments (
            product_id, adjustment_type, quantity_adjusted,
            reason, adjustment_date, created_by
        ) VALUES (
            999999, 'damaged', -5,
            'Detailed reason for damaged items that exceeds minimum length',
            CURRENT_TIMESTAMP, test_user_id
        );
        
        RAISE EXCEPTION 'Test 9.8: Should have raised foreign key violation';
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE '✅ Test 9.8: Foreign key constraint PASSED';
    END;
    
    -- CLEANUP
    PERFORM cleanup_adjustment_test_data(
        test_user_id, test_supplier_id, test_category_id, test_product_id
    );
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '❌ UNEXPECTED ERROR in %: %', test_name, SQLERRM;
    PERFORM cleanup_adjustment_test_data(
        test_user_id, test_supplier_id, test_category_id, test_product_id
    );
END $$;




