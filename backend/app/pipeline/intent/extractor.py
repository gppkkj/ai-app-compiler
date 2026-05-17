from typing import Dict, Any, List


def _contains_any(text: str, keywords: List[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def extract_intent(user_prompt: str) -> Dict[str, Any]:
    text = user_prompt.lower()

    app_name = "Generated Application"
    app_type = "Generic App"

    features: List[str] = []
    roles: List[str] = []
    entities: List[str] = []

    # -------------------------
    # App type detection
    # More specific domains should come before broad domains.
    # -------------------------

    if _contains_any(text, ["ice cream", "food", "restaurant", "menu", "delivery", "ordering"]):
        app_name = "Food Ordering Platform"
        app_type = "Food Ordering"
        features += ["menu", "cart", "orders"]
        entities += ["users", "menu_items", "orders", "cart_items"]

    elif _contains_any(text, ["inventory", "stock", "warehouse", "supplier", "suppliers"]):
        app_name = "Inventory Management System"
        app_type = "Inventory"
        features += ["inventory tracking", "stock alerts", "supplier management"]
        entities += ["users", "products", "inventory_items", "suppliers"]

    elif _contains_any(text, ["crm", "customer", "contacts", "sales lead", "leads"]):
        app_name = "CRM Platform"
        app_type = "CRM"
        features += ["contacts", "customer management"]
        entities += ["users", "contacts", "customers"]

    elif _contains_any(text, ["lms", "learning", "course", "quiz", "student", "instructor", "school", "schools", "teacher", "teachers", "classes", "exams"]):
        app_name = "Learning Management System"
        app_type = "LMS"
        features += ["courses", "quizzes", "student progress"]
        entities += ["users", "courses", "quizzes", "enrollments"]

    elif _contains_any(text, ["booking", "appointment", "calendar", "slot", "reservation", "event", "events", "tickets"]):
        app_name = "Booking Platform"
        app_type = "Booking"
        features += ["appointments", "calendar", "availability"]
        entities += ["users", "appointments", "time_slots"]

        if _contains_any(text, ["event", "events"]):
            entities += ["events"]

        if _contains_any(text, ["ticket", "tickets"]):
            entities += ["tickets"]

    elif _contains_any(text, ["helpdesk", "ticketing", "support", "issue", "agent", "agents"]):
        app_name = "Helpdesk System"
        app_type = "Helpdesk"
        features += ["ticket management", "support workflow"]
        entities += ["users", "tickets", "comments"]

    elif _contains_any(text, ["hr", "employee", "payroll", "attendance"]):
        app_name = "HR Management System"
        app_type = "HR"
        features += ["employee management", "attendance tracking"]
        entities += ["users", "employees", "attendance_records"]

    elif _contains_any(text, ["project management", "tasks", "kanban", "sprint", "projects"]):
        app_name = "Project Management Tool"
        app_type = "Project Management"
        features += ["task management", "project tracking"]
        entities += ["users", "projects", "tasks"]

    elif _contains_any(text, ["team", "teams", "collaboration"]):
        app_name = "Team Collaboration Platform"
        app_type = "Team Collaboration"
        features += ["team workspace", "shared dashboard"]
        entities += ["users", "teams", "projects"]

    elif _contains_any(text, ["ecommerce", "e-commerce", "shop", "store", "cart", "checkout", "order", "orders", "product", "products"]):
        app_name = "Ecommerce Platform"
        app_type = "Ecommerce"
        features += ["product catalog", "cart", "orders"]
        entities += ["users", "products", "orders", "cart_items"]

    elif _contains_any(text, ["saas", "subscription saas", "billing", "usage analytics", "plans"]):
        app_name = "Subscription SaaS Platform"
        app_type = "SaaS"
        features += ["dashboard", "usage analytics", "billing"]
        entities += ["users", "plans", "subscriptions", "payments"]

    else:
        app_name = "Generic Business Application"
        app_type = "Generic App"
        features += ["dashboard", "resource management"]
        entities += ["users", "resources"]

    # -------------------------
    # Feature detection
    # -------------------------

    if _contains_any(text, ["login", "auth", "authentication", "sign in", "signup", "role", "role-based"]):
        features.append("authentication")

    if _contains_any(text, ["dashboard", "analytics", "report", "reports", "chart", "admin analytics", "usage analytics"]):
        features.append("analytics dashboard")

    if _contains_any(text, ["premium", "subscription", "subscriptions", "plan", "plans", "billing"]):
        features.append("premium subscriptions")
        entities.append("subscriptions")

    if _contains_any(text, ["payment", "payments", "stripe", "checkout"]):
        features.append("payments")
        entities.append("payments")

    if _contains_any(text, ["notification", "email", "sms"]):
        features.append("notifications")

    if _contains_any(text, ["search", "filter"]):
        features.append("search and filtering")

    if _contains_any(text, ["cart"]):
        features.append("cart")

        if "cart_items" not in entities:
            entities.append("cart_items")

    if _contains_any(text, ["order", "orders"]):
        features.append("orders")

        if app_type == "Food Ordering" and "orders" not in entities:
            entities.append("orders")

        if app_type == "Ecommerce" and "orders" not in entities:
            entities.append("orders")

    # -------------------------
    # Role detection
    # -------------------------

    if _contains_any(text, ["admin", "administrator", "admins"]):
        roles.append("admin")

    if _contains_any(text, ["user", "users", "customer", "client"]):
        roles.append("user")

    if _contains_any(text, ["student", "students"]):
        roles.append("student")

    if _contains_any(text, ["instructor", "teacher", "teachers"]):
        roles.append("instructor")

    if _contains_any(text, ["seller", "vendor"]):
        roles.append("seller")

    if _contains_any(text, ["support agent", "agent", "agents"]):
        roles.append("agent")

    if _contains_any(text, ["manager"]):
        roles.append("manager")

    if _contains_any(text, ["organizer"]):
        roles.append("organizer")

    if _contains_any(text, ["parent"]):
        roles.append("parent")

    # Defaults
    if not roles:
        roles = ["admin", "user"]

    if "authentication" not in features and any(
        role in roles
        for role in ["admin", "manager", "seller", "agent", "instructor", "organizer", "parent"]
    ):
        features.append("authentication")

    # Ensure users table exists when auth or roles exist
    if "users" not in entities:
        entities.insert(0, "users")

    # Deduplicate while preserving order
    features = list(dict.fromkeys(features))
    roles = list(dict.fromkeys(roles))
    entities = list(dict.fromkeys(entities))

    return {
        "app_name": app_name,
        "app_type": app_type,
        "features": features,
        "roles": roles,
        "entities": entities
    }