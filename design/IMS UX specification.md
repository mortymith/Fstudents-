This specification translates the detailed functional requirements into a systematic, implementation-ready screen architecture. The design focuses on robust data integrity, clarity for Inventory Managers and Admins, and adherence to defined constraints (e.g., auto-generated IDs, role permissions, adjustment types).

### 🗺️ High-Level Sitemap / Page Hierarchy

|                               |                                 |               |                          |
| ----------------------------- | ------------------------------- | ------------- | ------------------------ |
| **Section**                   | **Screen Name**                 | **Screen ID** | **Required Role(s)**     |
| **1. Authentication & Users** | Login Screen                    | S-1.0         | All                      |
|                               | Forgot Password Screen          | S-1.1         | ALL                      |
|                               | Reset Password Screen           | S-1.2         | ALL                      |
|                               | User Management List            | S-1.3         | Admin                    |
| **2. Dashboard**              | Inventory Dashboard             | S-2.0         | All                      |
| **3. Product Catalog**        | Products List                   | S-3.1         | All                      |
|                               | Product Detail / Inventory View | S-3.2         | All                      |
|                               | Add/Edit Product Form           | S-3.3         | Inventory Manager, Admin |
|                               | Suppliers List                  | S-3.4         | IM, Admin                |
|                               | Add/Edit Supplier Form          | S-3.5         | IM, Admin                |
|                               | Category Management Modal       | S-3.6         | IM, Admin                |
| **4. Inventory Management**   | Low Stock View                  | S-4.1         | All                      |
| **5. Purchase Orders**        | PO Management List              | S-5.1         | IM, Admin                |
|                               | Create New PO Form              | S-5.2         | IM, Admin                |
|                               | PO Detail / Receiving Interface | S-5.3         | IM, Admin                |
| **6. Stock Operations**       | Stock Adjustment Tool           | S-6.1         | IM, Admin                |
|                               | Stock Movement Log              | S-6.2         | All                      |
| **7. Reports & Analytics**    | Reports Hub                     | S-7.0         | All                      |
|                               | Generic Report View (Template)  | S-7.1         | All                      |
| **8. Audit & Activity Logs**  | System Audit Log                | S-8.0         | Admin                    |
| **9. System Configuration**   | System Settings                 | S-9.0         | Admin                    |

### Detailed Screen-by-Screen Breakdown

#### 1. Authentication & Users

##### Screen Name: S-1.0 Login Screen

- **Purpose:** Authenticate the user.
    
- **User Role(s):** All Users
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Login Container (Centered)
     ├─ App Logo
     ├─ Title: "Inventory Management System"
     ├─ Login Form
     │   ├─ Input: Email Address (Placeholder: user@acme.corp)
     │   ├─ Input: Password (masked)
     │   └─ Primary CTA: "Log In"
     └─ Link: "Forgot Password?" (Future feature)
    ```
    
- **Primary Actions:** Log In.
    
- **Data Displayed/Modified:** `users.email`, `users.password_hash`. Updates `users.last_login_at`.
    
- **States:** - **Default:** Empty form, active inputs, enabled "Log In" button.
    
    - **Input Error:** Inline validation text and red input borders (e.g., "Email is invalid").
        
    - **Submitting/Loading:** Inputs disabled, button shows spinner/text "Logging In...".
        
    - **Authentication Failed:** Form re-enabled, red banner/toast: "Invalid email or password."
        
    - **Inactive Account:** Form re-enabled, red banner: "Your account is inactive."
        
    - **Success:** Brief visual confirmation, immediate redirection to S-2.0.
        
- **Navigation:** Success $\rightarrow$ S-2.0 Dashboard.
    

##### Screen Name: S-1.1 Forgot Password Screen

- **Purpose:** Initiate the password reset process by submitting the user's email address.
    
- **User Role(s):** All Users
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Forgot Password Container (Centered)
     ├─ App Logo
     ├─ Title: "Forgot Password"
     ├─ Instruction Text: "Enter your email address to receive a password reset link."
     ├─ Form
     │   ├─ Input: Email Address (Required)
     │   └─ Primary CTA: "Send Reset Link"
     ├─ Link: "Back to Login"
     └─ State Message: (Confirmation message after successful submission)
    ```
    
- **Primary Actions:** Send Reset Link.
    
- **Data Displayed/Modified:** `users.email`. System generates a secure, time-limited reset token (not stored in `users` table, likely in a separate temporary table or JWT payload).
    
- **States:**
    
    - **Default:** Empty email input, enabled "Send Reset Link" button.
        
    - **Input Error:** Inline validation text (e.g., "Email is required").
        
    - **Submitting/Loading:** Input disabled, button shows spinner.
        
    - **Success Confirmation:** Green banner: "If your email is registered, a reset link was sent."
        
    - **System Error:** Red banner: "A system error occurred."
        
- **Navigation:** "Back to Login" $\rightarrow$ S-1.0.
    

##### Screen Name: S-1.2 Reset Password Screen

- **Purpose:** Allow a user to set a new password after arriving via a secure, time-limited link.
    
- **User Role(s):** All Users
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Reset Password Container (Centered)
     ├─ App Logo
     ├─ Title: "Set New Password"
     ├─ Form (Pre-populated with hidden token from URL)
     │   ├─ Input: New Password (masked, validation required: minimum length, complexity)
     │   ├─ Input: Confirm New Password (masked, must match New Password)
     │   └─ Primary CTA: "Reset Password"
     ├─ Link: "Back to Login"
     └─ State Message: (Error if token is invalid or expired)
    ```
    
- **Primary Actions:** Reset Password.
    
- **Data Displayed/Modified:** Updates `users.password_hash` with the new hashed password.
    
- **States:** - **Default:** Empty password inputs, disabled "Reset Password" button.
    
    - **Input Error:** Inline error for complexity, length, or mismatch between new/confirm passwords.
        
    - **Submitting/Loading:** Inputs disabled, button shows spinner.
        
    - **Token Invalid/Expired:** Red banner: "The reset link is invalid or has expired."
        
    - **Success:** Green banner: "Password successfully updated. Proceed to login."
        
- **Navigation:** Successful Reset $\rightarrow$ S-1.0 Login Screen.
    

##### Screen Name: S-1.3 User Management List

- **Purpose:** View and manage user accounts, roles, and status.
    
- **User Role(s):** Admin only
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Header + Sidebar (Standard Layout)
    
    Main Content Area
     ├─ Control Bar
     │   ├─ Search Input (By Name, Email)
     │   ├─ Filter Dropdown: Role (Admin, Inventory Manager, Viewer)
     │   ├─ Filter Dropdown: Status (Active, Deactivated)
     │   └─ Primary CTA: "Add New User"
     ├─ Users Data Table
     │   ├─ Columns: Name, Email, Role, Status, Last Login, Created At
     │   └─ Row Actions: "Edit," "Deactivate / Activate"
     └─ Pagination
    ```
    
- **Primary Actions:** Create User, Edit User, **Activate / Deactivate User**.
    
- **Data Displayed/Modified:** `users` table data.
    
- **States:** - **Loading:** Data table area shows a skeleton loader or spinner.
    
    - **Default/Populated:** Data table visible, filters active, pagination controls visible.
        
    - **Empty:** Data table area shows a central message: "No users found. Start by creating a new administrator."
        
    - **Search/Filter Empty:** Data table area shows: "No results match your search criteria."
        
    - **Action Success:** Toast notification: "User [Name]'s role updated successfully."
        
- **Navigation:** "Add New User" $\rightarrow$ **S-1.3.1**. Row Action "Edit" $\rightarrow$ **S-1.3.1** (pre-filled).
    

###### Screen Name: S-1.3.1 Add/Edit User Form

- **Purpose:** Create a new user or modify details of an existing user account.
    
- **User Role(s):** Admin only
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Modal / Full Page Form
     ├─ Title: "Add New User" / "Edit User: [User Name]"
     ├─ Form Fields
     │   ├─ Input: Full Name (Required, updates `users.name`)
     │   ├─ Input: Email Address (Required, updates `users.email`)
     │   ├─ Dropdown: Role (Required, updates `users.role`: Admin, Inventory Manager, Viewer)
     │   ├─ Dropdown: Status (Required, updates `users.status`: Active, Deactivated)
     │   ├─ **If New User:** Input: Password (Required, initial password or 'Send Activation Link')
     │   └─ **If Existing User:** Button: "Send Password Reset Link"
     └─ Primary CTA: "Save User" / "Create User"
    ```
    
- **Primary Actions:** Save/Create User.
    
- **Data Displayed/Modified:** `users` table data.
    
- **States:** Standard form validation and success/error states.
    

#### 2. Dashboard

##### Screen Name: S-2.0 Inventory Dashboard

- **Purpose:** Provide a real-time summary of core inventory and PO KPIs, and highlight critical alerts.
    
- **User Role(s):** All Users
    
- **Wireframe Layout :**
    
    ```
    Header + Sidebar (Standard Layout)
    
    Main Content Area
     ├─ **KPI Cards (Inventory Summary)**
     │   ├─ Card 1: Total Products (Active)
     │   ├─ Card 2: **Available Stock Value** (Sum of Qty Available * Cost)
     │   ├─ Card 3: Low Stock Alerts (Link to S-4.1)
     │   └─ Card 4: Inventory Turnover Rate (Analytics)
     ├─ **PO Status Overview (Purchase Orders Overview)**
     │   ├─ Card: Draft POs (Link to S-5.1 filtered by Draft)
     │   ├─ Card: Ordered POs (Link to S-5.1 filtered by Ordered)
     │   └─ Card: Overdue Expected Delivery
     ├─ **Recent Activities (Stock Movement Snapshot)**
     │   ├─ Filter Tabs: Stock Movements / Adjustments / PO Updates
     │   └─ Data Table (Last 10 Activities): Date, Type, Reference ID, User
    ```
    
- **Primary Actions:** Quick access to transactional screens (e.g., clicking 'Draft POs' to manage them).
    
- **Data Displayed/Modified:** Aggregated data from `products`, `product_inventory`, `purchase_orders`, `stock_movements`, `stock_adjustments`.
    
- **Status**:
    
    - **Loading:** KIP cards, widgets, and tables show a skeleton loader for aggregated data.
        
    - **Default/Populated:** All KPI cards display current counts/metrics, PO widgets show real-time numbers, and Recent Activities table is populated.
        
    - **Low Stock Alert:** The Low Stock KPI card changes color (e.g., red/orange) and displays the critical count.
        
    - **Empty Data:** The Recent Activities table shows: "No recent stock movements or PO updates recorded."
        

#### 3. Product Catalog

##### Screen Name: S-3.1 Products List

- **Purpose:** View, search, and filter the entire product catalog.
    
- **User Role(s):** All Users (Viewers are read-only)
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Header + Sidebar (Standard Layout)
    
    Main Content Area
     ├─ Control Bar
     │   ├─ Search Input (By Name, SKU)
     │   ├─ Filter Dropdown: Category (Hierarchical selection)
     │   ├─ Filter Dropdown: Supplier
     │   ├─ Filter Dropdown: Stock Status (Available < Reorder Point, In Stock, Out of Stock)
     │   └─ Primary CTA: "Add New Product" (IM/Admin only)
     ├─ Products Data Table
     │   ├─ Columns: **SKU**, Name, Category, Supplier, **Price**, **Qty Available**, **Reorder Point**
     │   └─ Row Actions: "View Details," "Edit" (IM/Admin only), "Deactivate" (IM/Admin only)
     └─ Pagination
    ```
    
- **Primary Actions:** Search, Filter, Create Product.
    
- **Status:**
    
    - **Loading:** Data table area shows a skeleton loader.
        
    - **Default/Populated:** Filtered/sorted product data is displayed in the table.
        
    - **Empty:** Table area shows: "The product catalog is currently empty. Click 'Add New Product' to begin."
        
    - **Search/Filter Empty:** Table area shows: "No products match your current search/filter criteria."
        
    - **Action Success:** Toast notification: "Product [SKU] archived successfully."
        
- **Navigation:** Row click $\rightarrow$ S-3.2. "Add New Product" $\rightarrow$ S-3.3.
    

##### Screen Name: S-3.2 Product Detail / Inventory View

- **Purpose:** Display all product details, inventory breakdown, and action history.
    
- **User Role(s):** admin and IM
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Header + Sidebar (Standard Layout)
    
    Main Content Area
     ├─ **Product Header**
     │   ├─ Product Name and SKU
     │   └─ Action Buttons (IM/Admin only): "Edit Details" (S-3.3), "Adjust Stock" (S-6.1), "Print Barcode"
     ├─ **Details (Left Panel)**
     │   ├─ Field Group: Product Info (Name, Description, Category, Supplier)
     │   ├─ Field Group: Financial (Unit **Price**, Unit **Cost** - IM/Admin only)
     │   ├─ Field Group: Physical (Barcode/QR, **Expiry Date**)
     ├─ **Inventory & Reorder (Right Panel - Data from `product_inventory`)**
     │   ├─ KPI: **Quantity On Hand** (Raw count)
     │   ├─ KPI: **Quantity Committed** (Orders/Sales)
     │   ├─ KPI: **Quantity Available** (QOH - Committed)
     │   ├─ Field Group: Thresholds (**Low Stock Threshold**, **Reorder Point**, **Reorder Quantity**)
     │   ├─ Audit: **Last Counted**, **Last Restocked**
     ├─ **Tabs**
     │   ├─ Tab 1: Stock Movement Log (Filterable table linked to S-6.2)
     │   ├─ Tab 2: PO History (Table of all POs associated with this product, link to S-5.3)
    ```
    
- **Primary Actions:** Edit Product, Perform Adjustment, Print Barcode/QR.
    
- **Data Displayed:** All fields from `products` and `product_inventory`.
    
- **States:**
    
    - **Loading:** All sections (Details, Inventory, Tabs) show skeleton loaders.
        
    - **Default/Populated:** All product fields and inventory metrics (On Hand, Committed, Available) are displayed.
        
    - **Alert State:** A persistent banner appears if **Quantity Available** $\le$ **Reorder Point** (e.g., "Warning: Product is below the reorder point.").
        
    - **Archived State:** A prominent, non-dismissible banner is displayed at the top: "This product is inactive and cannot be transacted."
        
    - **Error State:** An error message is displayed if the product ID is not found (e.g., "Error: Product not found in catalog.").
        

##### Screen Name: S-3.3 Add/Edit Product Form

- **Purpose:** Create a new product entry or modify the details of an existing product in the catalog.
    
- **User Role(s):** Inventory Manager, Admin
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Full Page Form: Add/Edit Product
     ├─ Title: "Add New Product" / "Edit Product: [Product Name]"
     ├─ **Product Information** (From `products` table)
     │   ├─ Input: Name (Required)
     │   ├─ Text Area: Description
     │   ├─ Dropdown: Category (Required, links to S-3.6)
     │   ├─ Dropdown: Primary Supplier (Required)
     │   ├─ Input: Unit Price (Required, `chk_price_positive`)
     │   ├─ Input: Unit Cost (Editable for Admin only)
     │   ├─ Input: Barcode / QR Code (Optional, unique)
     │   └─ Checkbox: Track Expiry Date (If checked, shows Expiry Date input)
     ├─ **Inventory & Thresholds** (From `product_inventory` table)
     │   ├─ Input: Low Stock Threshold (Min Qty for alert on S-4.1)
     │   ├─ Input: Reorder Point (Qty that triggers auto-PO suggestion)
     │   ├─ Input: Reorder Quantity (Default quantity for new POs)
     │   └─ Checkbox: Is Active (Status of the product)
     └─ Primary CTA: "Save Product"
    ```
    
- **Primary Actions:** Save Product, Cancel.
    
- **Data Displayed/Modified:** `products` and `product_inventory` table data.
    
- **States:** Standard form validation, including ensuring `Reorder Point` is less than `Low Stock Threshold` (if applicable).
    

##### Screen Name: S-3.4 Suppliers List

- **Purpose:** View, search, and filter the list of all product suppliers.
    
- **User Role(s):** Inventory Manager, Admin
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Header + Sidebar (Standard Layout)
    
    Main Content Area
     ├─ Control Bar
     │   ├─ Search Input (By Name, Contact)
     │   └─ Primary CTA: "Add New Supplier"
     ├─ Suppliers Data Table
     │   ├─ Columns: Name, Primary Contact, Phone, Email, Created At
     │   └─ Row Actions: "Edit," "View PO History"
     └─ Pagination
    ```
    
- **Primary Actions:** Search, Create Supplier.
    
- **Navigation:** "Add New Supplier" $\rightarrow$ S-3.5. Row Action "Edit" $\rightarrow$ S-3.5 (pre-filled).
    

##### Screen Name: S-3.5 Add/Edit Supplier Form

- **Purpose:** Create a new supplier or modify an existing supplier's details.
    
- **User Role(s):** Inventory Manager, Admin
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Modal / Full Page Form
     ├─ Title: "Add New Supplier" / "Edit Supplier: [Supplier Name]"
     ├─ **Supplier Information** (From `suppliers` table)
     │   ├─ Input: Supplier Name (Required, unique)
     │   ├─ Text Area: Address
     │   ├─ Input: Phone Number
     │   ├─ Input: Email Address (Optional)
     │   ├─ Input: Primary Contact Name
     │   └─ Dropdown: Default Payment Terms (e.g., Net 30, Net 60)
     └─ Primary CTA: "Save Supplier"
    ```
    
- **Primary Actions:** Save Supplier, Cancel.
    
- **Data Displayed/Modified:** `suppliers` table data.
    

##### Screen Name: S-3.6 Category Management Modal

- **Purpose:** Manage the hierarchical list of product categories.
    
- **User Role(s):** Inventory Manager, Admin
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Modal: Category Management
     ├─ Title: "Product Category Management"
     ├─ **Add New Category Form**
     │   ├─ Input: Category Name (Required)
     │   └─ Dropdown: Parent Category (Selectable list of active categories)
     ├─ **Category Tree View**
     │   ├─ List: Category A (Active)
     │   │   └─ List: Sub-Category A.1 (Active)
     │   ├─ List: Category B (Inactive)
     │   └─ Row Actions: "Edit Name," "Change Parent," "Enable / Disable"
     └─ Action Button: "Save and Close"
    ```
    
- **Validation:** Must prevent setting an active category under a disabled parent.
    
- **States:**
    
    - **Loading:** Tree view shows a spinner while hierarchy data is fetched.
        
    - **Default/Populated:** Category tree list is visible, organized by parent/child relationships.
        
    - **Input Error:** Inline validation on category name or parent selection if attempting an illegal assignment (e.g., cyclic dependency).
        
    - **Action Success:** Toast notification: "Category added successfully" or "Category hierarchy updated."
        

#### 4. Inventory Management

##### Screen Name: S-4.1 Low Stock View

- **Purpose:** List all products where Quantity Available is at or below the Reorder Point.
    
- **User Role(s):** All Users
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Header + Sidebar (Standard Layout)
    
    Main Content Area
     ├─ Title: "Low Stock Alerts"
     ├─ Control Bar
     │   ├─ Filter Dropdown: Category
     │   └─ Filter Dropdown: Supplier
     ├─ Low Stock Data Table
     │   ├─ Columns: **SKU**, Name, Qty Available, Reorder Point, Reorder Quantity
     │   └─ Row Actions: "View Product," "Suggest PO" (IM/Admin only)
     └─ Pagination
    ```
    
- **Primary Actions:** View Product Detail, Suggest/Initiate PO.
    
- **Data Displayed/Modified:** Products filtered where `product_inventory.quantity_available` $\le$ `product_inventory.reorder_point`.
    
- **States:** Standard data table states.
    

#### 5. Purchase Orders

##### Screen Name: S-5.1 PO Management List

- **Purpose:** Manage the lifecycle of all Purchase Orders.
    
- **User Role(s):** Inventory Manager, Admin
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Header + Sidebar (Standard Layout)
    
    Main Content Area
     ├─ Control Bar
     │   ├─ Search Input (By **PO Number**, Supplier)
     │   ├─ Filter Dropdown: **Status** (Draft, Ordered, Partially Received, Received, Cancelled)
     │   ├─ Filter: Date Range
     │   └─ Primary CTA: "Create New PO"
     ├─ Purchase Orders Data Table
     │   ├─ Columns: **PO Number**, Supplier, **Status**, Ordered Date, Expected Delivery Date, Created By
     │   └─ Row Actions: "View/Receive," "Edit (If Draft)," "Mark as Ordered (If Draft)," "Cancel"
     └─ Pagination
    ```
    
- **Primary Actions:** Create PO, View PO, Change PO Status (`Mark as Ordered`).
    
- **Data Displayed:** Data from `purchase_orders`.
    
- **States:**
    
    - **Loading:** Data table area shows a skeleton loader.
        
    - **Default/Populated:** Table shows POs with color-coded status tags (Draft, Ordered, Partially Received, Received, Cancelled).
        
    - **Empty:** Table area shows: "No Purchase Orders have been created yet."
        
    - **Action Success:** Toast notification: "PO [Number] status updated to Ordered."
        
- **Navigation:** Row click $\rightarrow$ S-5.3. "Create New PO" $\rightarrow$ S-5.2 (Create PO Form).
    

##### Screen Name: S-5.2 Create New PO Form

- **Purpose:** Initiate a new Purchase Order linked to a specific supplier.
    
- **User Role(s):** Inventory Manager, Admin
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Full Page Form: Create Purchase Order
     ├─ Title: "Create New Purchase Order"
     ├─ **PO Header Details** (From `purchase_orders` table)
     │   ├─ Dropdown: Supplier (Required)
     │   ├─ Input: Expected Delivery Date (Required)
     │   ├─ Input: Reference Number (Optional, Manual Override of auto-generated PO ID)
     │   └─ Text Area: Internal Notes
     ├─ **Purchase Order Items** (From `purchase_order_items` table)
     │   ├─ Table: Items to Order (Dynamic Entry)
     │   │   ├─ Column Input: Product Search/SKU (Required)
     │   │   ├─ Column Input: Quantity Ordered (Required, positive integer)
     │   │   └─ Column Input: Unit Cost (Required, overrides product cost for this PO)
     │   └─ Button: "Add New Line Item"
     ├─ **PO Summary**
     │   ├─ Readout: Total Estimated Cost
     └─ Primary CTA: "Save as Draft" / "Mark as Ordered"
    ```
    
- **Primary Actions:** Save as Draft, Mark as Ordered.
    
- **Data Displayed/Modified:** Creates records in `purchase_orders` and `purchase_order_items`.
    

##### Screen Name: S-5.3 PO Detail / Receiving Interface

- **Purpose:** Review a PO and record the receipt of goods, updating inventory.
    
- **User Role(s):** Inventory Manager, Admin
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Header + Sidebar (Standard Layout)
    
    Main Content Area
     ├─ Title: "Purchase Order: [PO Number]"
     ├─ **PO Status and Audit**
     │   ├─ Status Tag (Large): [Draft / Ordered / Partially Received / Received]
     │   ├─ Audit Fields: Created By, Ordered Date, Received Date
     ├─ **PO Item List / Receiving Interface**
     │   ├─ Table: **Purchase Order Items**
     │   │   ├─ Columns: Product Name/SKU, Unit Cost, **Quantity Ordered**, **Quantity Received** (Read-only if received)
     │   │   └─ Input Column (Editable if Status = Ordered/Partially Received): **Quantity to Receive Now**
     │   ├─ Summary: Total Line Items, Total Cost
     ├─ **Action Buttons (Conditional)**
     │   ├─ If Status = 'Draft': "Mark as Ordered" (Triggers `purchase_order_items` status update)
     │   ├─ If Status = 'Ordered/Partially Received': Primary CTA: "**Record Receipt**" (Logs IN `stock_movements`, updates `product_inventory.quantity_on_hand`, updates PO status)
     │   ├─ If Status = 'Received': Secondary CTA: "Print Receipt"
    ```
    
- **Primary Actions:** **Record Receipt**.
    
- **Key Components:** Input field for `Quantity to Receive Now` (allowing partial receipts).
    
- **States:**
    
    - **Loading:** All PO detail fields and item tables show a skeleton loader.
        
    - **Status: Draft:** The **Record Receipt** button is hidden; the **Mark as Ordered** button is visible. Item list inputs are editable (via S-5.2 only).
        
    - **Status: Ordered/Partially Received (Ready to Receive):** The **Record Receipt** button is primary. **Quantity to Receive Now** inputs are active.
        
    - **Status: Received:** The **Record Receipt** button is hidden/disabled; a **Print Receipt** button is shown. All inputs are read-only.
        
    - **Validation Error (Receiving):** If `Quantity to Receive Now` exceeds remaining quantity, the input field turns red and an inline error appears.
        
    - **Action Success:** Toast notification: "Stock received successfully. Inventory updated and movements logged."
        

#### 6. Stock Operations

##### Screen Name: S-6.1 Stock Adjustment Tool

- **Purpose:** Perform manual, non-transactional changes to inventory levels.
    
- **User Role(s):** Inventory Manager, Admin
    
- **Wireframe Layout:**
    
    ```
    Header + Sidebar (Standard Layout)
    
    Main Content Area
     ├─ Title: "Stock Adjustment"
     ├─ **Product Identification**
     │   ├─ Input: Product Search (by Name/SKU)
     │   ├─ Readout: Selected Product Name, Current Qty Available
     ├─ **Adjustment Form**
     │   ├─ Dropdown: **Adjustment Type** (Constrained list: Damaged, Expired, Theft, Found, Returned, Internal Use)
     │   ├─ Input: **Adjustment Delta (+/- Quantity)** (Must align with `adjustment_type` constraint)
     │   ├─ Text Area: **Reason / Notes** (Required for 'Damaged' and 'Theft')
     │   ├─ Checkbox: Is Cycle Count? (Optional flag)
     └─ Primary CTA: "Submit Adjustment"
    ```
    
- **Primary Actions:** **Create Adjustment**.
    
- **Validation:** UI enforces `chk_adjustment_quantities` (positive delta for 'Found'/'Returned', negative for loss types) and `chk_adjustment_reason_required`.
    
- **Status:**
    
    - **Loading:** Product search and form fields show a spinner while related data is fetched.
        
    - **Input Error:** If `Adjustment Delta` sign conflicts with the `Adjustment Type` (e.g., negative value for 'Found'), the delta input turns red.
        
    - **Reason Required Error:** If 'Damaged' or 'Theft' is selected and the Reason/Notes field is empty, the field turns red.
        
    - **Action Success:** Toast notification: "Stock adjustment successfully submitted."
        
    - **System Error:** Red banner: "Failed to process adjustment due to a system lock."
        

##### Screen Name: S-6.2 Stock Movement Log (Movement Reports)

- **Purpose:** Provide a detailed, immutable history of all inventory changes.
    
- **User Role(s):** All Users
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Header + Sidebar (Standard Layout)
    
    Main Content Area
     ├─ Title: "Stock Movement Log"
     ├─ Control Bar
     │   ├─ Filter: Date Range
     │   ├─ Filter Dropdown: Movement Type (**IN, OUT, Adjustment**)
     │   ├─ Filter Input: Reference ID (PO#, Sale #, Adjustment ID)
     │   └─ Button: "Export"
     ├─ **Stock Movements Data Table**
     │   ├─ Columns: Timestamp, Product Name, **Movement Type**, **Quantity Change**, **User Responsible**, **Reference**
     │   └─ Row Details (Expandable): Before/After Quantities, Adjustment Reason (if applicable)
     └─ Pagination
    ```
    
- **Data Displayed:** Data from `stock_movements`, linking to `products`, `users`, `purchase_orders`, and `stock_adjustments`.
    
- **States:**
    
    - **Loading:** Data table area shows a skeleton loader.
        
    - **Default/Populated:** Filtered historical movement data is displayed.
        
    - **Empty:** Table area shows: "No stock movements have been recorded yet."
        

#### 7. Reports & Analytics

##### Screen Name: S-7.0 Reports Hub

- **Purpose:** Centralized access point for all system reports and analytical dashboards.
    
- **User Role(s):** All Users
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Header + Sidebar (Standard Layout)
    
    Main Content Area
     ├─ Title: "Reports and Analytics"
     ├─ **Report Categories** (Tabs/Tiles)
     │   ├─ Inventory Reports
     │   ├─ Purchase Order Reports
     │   └─ Audit Reports
     ├─ **Inventory Reports List**
     │   ├─ Link: Inventory Valuation Report (S-7.1 Template)
     │   ├─ Link: Stock Out History Report (S-7.1 Template)
     │   ├─ Link: Low Stock Prediction
     ├─ **PO Reports List**
     │   ├─ Link: PO Aging Report (S-7.1 Template)
     │   └─ Link: Supplier Performance Report
    ```
    
- **Primary Actions:** Select a Report, Filter Report List.
    
- **Navigation:** Click Report Link $\rightarrow$ S-7.1.
    

##### Screen Name: S-7.1 Generic Report View (Template)

- **Purpose:** A standardized template for displaying various report outputs (charts, tables, summaries).
    
- **User Role(s):** All Users
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Header + Sidebar (Standard Layout)
    
    Main Content Area
     ├─ Title: "[Report Name]"
     ├─ **Report Filters**
     │   ├─ Input: Date Range Selector (Required)
     │   ├─ Dropdown: Category / Supplier / Product (Contextual)
     │   └─ Button: "Run Report" / "Refresh"
     ├─ **Report Output**
     │   ├─ Chart Area (e.g., Bar Chart, Line Graph)
     │   ├─ Summary KPIs (e.g., Total Value, Average Days)
     │   └─ Data Table (Exportable)
     └─ Button: "Export to CSV"
    ```
    
- **Primary Actions:** Run Report, Export Data.
    

#### 8. Audit & Activity Logs

##### Screen Name: S-8.0 System Audit Log

- **Purpose:** Provide a high-level, system-wide timeline of user actions and key inventory life cycle events.
    
- **User Role(s):** Admin only
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Header + Sidebar (Standard Layout)
    
    Main Content Area
     ├─ Title: "System Audit Log"
     ├─ Control Bar
     │   ├─ Filter: Date Range
     │   ├─ Filter Dropdown: User
     │   ├─ Filter Dropdown: Entity (Product, PO, User, Category)
     ├─ **Audit Log Timeline**
     │   ├─ Item: [Date/Time] - [User Name] **[Action]** on **[Entity Type]** [Entity Name/ID]
     │   └─ Examples:
     │      - 2025-12-15 14:00: Jane Doe **Logged In** (User Activity)
     │      - 2025-12-15 14:05: John Smith **Created** Product "Laptop Charger" (Inventory Changes)
     │      - 2025-12-15 14:15: Jane Doe **Received** PO #PO-1002 (PO Updates)
    ```
    
- **Data Displayed:** Aggregated, time-stamped log of critical system events.
    
- **State:**
    
    - **Loading:** Timeline shows a skeleton loader.
        
    - **Default/Populated:** Time-stamped list of user and system activities is displayed.
        
    - **Empty:** Timeline area shows: "No recent system audit records found."
        

#### 9. System Configuration

##### Screen Name: S-9.0 System Settings

- **Purpose:** Allow administrators to configure global system parameters, defaults, and integrations.
    
- **User Role(s):** Admin only
    
- **Wireframe Layout (Text-Based):**
    
    ```
    Header + Sidebar (Standard Layout)
    
    Main Content Area
     ├─ Title: "System Configuration"
     ├─ **Configuration Tabs**
     │   ├─ Tab 1: General Settings
     │   ├─ Tab 2: Naming & IDs
     │   └─ Tab 3: Notifications
     ├─ **General Settings Tab**
     │   ├─ Dropdown: Default Currency (e.g., USD, EUR)
     │   ├─ Dropdown: Default Weight Unit (e.g., kg, lbs)
     │   └─ Checkbox: Enable Expiry Date Tracking (Global setting)
     ├─ **Naming & IDs Tab**
     │   ├─ Input: PO Number Prefix (e.g., "PO-", updates `purchase_orders.po_number` generation)
     │   ├─ Input: SKU Auto-Generation Pattern (e.g., {Category Code}-{Sequential})
     │   └─ Checkbox: Enable Manual ID Override (Controls visibility of ID override on S-3.3, S-5.2)
     ├─ **Notifications Tab**
     │   ├─ Checkbox: Send Low Stock Email Alerts
     │   └─ Input: Default Recipient Email for Alerts
     └─ Primary CTA (Bottom of Page): "Save Configuration"
    ```
    
- **Primary Actions:** Save Configuration.
    
- **Data Displayed/Modified:** System-wide configuration parameters (stored outside standard transactional tables).
    
- **States:** Standard form validation and success/error states.
    

### Cross-Cutting UX Considerations

#### Role-Based Visibility (`users.role`)

|   |   |   |   |
|---|---|---|---|
|**Element**|**Admin**|**Inventory Manager**|**Viewer**|
|**Sidebar Link: User Management**|Visible|Hidden|Hidden|
|**Sidebar Link: System Settings**|Visible|Hidden|Hidden|
|**Product Financials (Cost Price)**|Visible (Read/Write - via S-3.3)|Visible (Read-Only)|Hidden|
|**Primary Action: Receive PO**|Visible|Visible|Hidden|
|**Primary Action: Add/Edit Product**|Visible|Visible|Hidden|
|**Audit Log (S-8.0)**|Visible|Hidden|Hidden|
|**Reports Hub (S-7.0)**|Full Access|Full Access|Full Access|

#### Reusable Components

1. **Sidebar Navigation:** Standardized, single-source navigation across all screens (except S-1.0 Login). Must respect role visibility.
    
2. **Data Table:** Standard component with integrated features: search, multi-filter, pagination, and sorting. Used for S-1.1, S-3.1, S-3.4, S-5.1, S-6.2, and reports.
    
3. **Status Tag Component:** Standardized, color-coded badges for all lifecycle statuses (PO: Draft/Ordered/Partially Received/Received; Product: Active/Inactive; Stock: Low/In/Out).
    
4. **Quantity Display Component:** A dedicated UI block on S-3.2 Product Detail to clearly show the relationship between **On Hand** $\leftrightarrow$ **Committed** $\leftrightarrow$ **Available**.
    

#### Validation and Feedback Patterns

- **Atomic Transactions:** Successful updates to stock must trigger a **success toast notification** that explicitly confirms: "Inventory Updated. Stock Movement **S-XXXX** Logged."
    
- **Data Consistency:** Forms (S-3.3, S-6.1, S-5.3) must include **real-time field validation** enforcing DB constraints (`chk_price_positive`, `chk_adjustment_quantities`, etc.). E.g., if a user selects 'Theft' in the Adjustment Tool, the delta input field must immediately turn red if the value entered is positive.
    
- **System Constraints:** For auto-generated fields like SKU and PO Number, the UI on S-3.3 and S-5.2 should display a read-only placeholder (e.g., `[Auto-Generated on Save]`) or the generated value, with a clearly labeled 'Override' control for IM/Admin if manual entry is permitted by business rules.