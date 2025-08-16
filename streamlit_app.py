import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# =============================
# App Config
# =============================
st.set_page_config(page_title="Local Food Wastage Management System", layout="wide")
st.title("Local Food Wastage Management System")

# =============================
# Database Connection
# =============================
DB_PATH = "sqlite:///data/food_waste.db"
engine = create_engine(DB_PATH, echo=False)

# =============================
# Helpers
# =============================
@st.cache_data(ttl=60)
def fetch_df(query: str, params: dict | None = None) -> pd.DataFrame:
    try:
        return pd.read_sql_query(text(query), engine, params=params)
    except Exception as e:
        st.error(f"SQL error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_distinct_values(table: str, column: str) -> list:
    q = f"SELECT DISTINCT {column} AS val FROM {table} WHERE {column} IS NOT NULL ORDER BY 1"
    df = fetch_df(q)
    return [v for v in df["val"].dropna().astype(str).tolist()]

def run_write(query: str, params: dict | None = None):
    try:
        with engine.begin() as conn:
            conn.execute(text(query), params or {})
        st.success("Operation successful.")
        fetch_df.clear()  # invalidate caches
        get_distinct_values.clear()
    except Exception as e:
        st.error(f"Write error: {e}")

# Safely check table exists
@st.cache_data(ttl=60)
def tables_present() -> set:
    df = fetch_df("SELECT name FROM sqlite_master WHERE type='table'")
    return set(df["name"].tolist())

REQUIRED_TABLES = {"providers", "receivers", "food_listings", "claims"}
missing = REQUIRED_TABLES - tables_present()
if missing:
    st.warning("⚠️ Some required tables are missing: " + ", ".join(sorted(missing)))
    st.stop()

# =============================
# Sidebar - Filters & Navigation
# =============================
with st.sidebar:
    st.header("Filters")
    locations = get_distinct_values("food_listings", "location") or []
    providers_list = get_distinct_values("providers", "name") or []
    food_types = get_distinct_values("food_listings", "food_type") or []

    loc_choice = st.selectbox("Location", options=["All"] + locations, index=0)
    prov_choice = st.selectbox("Provider", options=["All"] + providers_list, index=0)
    type_choice = st.selectbox("Food Type", options=["All"] + food_types, index=0)

    st.markdown("---")
    mode = st.radio(
        "Choose section",
        [
            "Browse & Filter",
            "Contact Directory",
            "CRUD Operations",
            "Reports (16 SQL Queries)",
        ],
    )

# =============================
# Browse & Filter Page
# =============================
if mode == "Browse & Filter":
    st.subheader("Browse Food Listings with Filters")
    base_q = """
        SELECT f.food_id, f.food_name, f.food_type, f.quantity, f.expiry_date,
               f.location, p.name AS provider_name, p.contact AS provider_contact
        FROM food_listings f
        LEFT JOIN providers p ON f.provider_id = p.provider_id
        WHERE 1=1
    """
    params = {}
    if loc_choice != "All":
        base_q += " AND LOWER(TRIM(f.location)) = LOWER(TRIM(:loc))"
        params["loc"] = loc_choice
    if prov_choice != "All":
        base_q += " AND LOWER(TRIM(p.name)) = LOWER(TRIM(:pname))"
        params["pname"] = prov_choice
    if type_choice != "All":
        base_q += " AND LOWER(TRIM(f.food_type)) = LOWER(TRIM(:ft))"
        params["ft"] = type_choice

    base_q += " ORDER BY COALESCE(f.expiry_date, '9999-12-31') ASC"

    df = fetch_df(base_q, params)
    st.caption(f"Found {len(df)} listing(s)")
    st.dataframe(df, use_container_width=True)

# =============================
# Contact Directory
# =============================
elif mode == "Contact Directory":
    st.subheader("Contact Providers & Receivers")
    tabs = st.tabs(["Providers", "Receivers"])

    with tabs[0]:
        st.markdown("### Providers")
        city_filter = st.selectbox("Filter by City", options=["All"] + get_distinct_values("providers", "city"))
        q = "SELECT provider_id, name, type, city, contact, address FROM providers WHERE 1=1"
        params = {}
        if city_filter != "All":
            q += " AND LOWER(TRIM(city)) = LOWER(TRIM(:city))"
            params["city"] = city_filter
        pdf = fetch_df(q, params)
        st.dataframe(pdf, use_container_width=True)

    with tabs[1]:
        st.markdown("### Receivers")
        city_filter_r = st.selectbox("Filter by City ", options=["All"] + get_distinct_values("receivers", "city"))
        # q = "SELECT receiver_id, name, category, city, contact, address FROM receivers WHERE 1=1"
        q = "SELECT receiver_id, name, type, city, contact FROM receivers WHERE 1=1"

        # cols = ["receiver_id", "name", "city", "contact", "address"]
        # available = pd.read_sql_query("PRAGMA table_info(receivers);", engine)["name"].tolist()
        # if "category" in available:
        #     cols.insert(2, "category")
        # q = f"SELECT {', '.join(cols)} FROM receivers WHERE 1=1"

        params = {}
        if city_filter_r != "All":
            q += " AND LOWER(TRIM(city)) = LOWER(TRIM(:city))"
            params["city"] = city_filter_r
        rdf = fetch_df(q, params)
        st.dataframe(rdf, use_container_width=True)

# =============================
# CRUD Operations
# =============================
elif mode == "CRUD Operations":
    st.subheader("Create / Read / Update / Delete")
    section = st.selectbox("Choose table", ["providers", "receivers", "food_listings", "claims"])

    st.markdown("#### Preview (Top 25)")
    st.dataframe(fetch_df(f"SELECT * FROM {section} LIMIT 25"), use_container_width=True)

    st.markdown("---")
    colA, colB, colC = st.columns(3)

    # CREATE
    with colA:
        st.markdown("### Add New Record")
        if section == "providers":
            with st.form("add_provider"):
                name = st.text_input("Name")
                type_ = st.text_input("Type")
                address = st.text_input("Address")
                city = st.text_input("City")
                contact = st.text_input("Contact")
                submitted = st.form_submit_button("Add Provider")
                if submitted:
                    run_write("INSERT INTO providers (name, type, address, city, contact) VALUES (:name, :type, :address, :city, :contact)", {"name": name, "type": type_, "address": address, "city": city, "contact": contact})
        elif section == "receivers":
            with st.form("add_receiver"):
                name = st.text_input("Name")
                category = st.text_input("Category")
                address = st.text_input("Address")
                city = st.text_input("City")
                contact = st.text_input("Contact")
                submitted = st.form_submit_button("Add Receiver")
                if submitted:
                    run_write("INSERT INTO receivers (name, category, address, city, contact) VALUES (:name, :category, :address, :city, :contact)", {"name": name, "category": category, "address": address, "city": city, "contact": contact})
        elif section == "food_listings":
            with st.form("add_food"):
                provider_id = st.number_input("Provider ID", step=1, min_value=1)
                food_name = st.text_input("Food Name")
                food_type = st.text_input("Food Type")
                quantity = st.number_input("Quantity", step=1, min_value=0)
                expiry_date = st.date_input("Expiry Date")
                location = st.text_input("Location")
                submitted = st.form_submit_button("Add Listing")
                if submitted:
                    run_write("INSERT INTO food_listings (provider_id, food_name, food_type, quantity, expiry_date, location) VALUES (:pid, :fname, :ftype, :qty, :exp, :loc)", {"pid": int(provider_id), "fname": food_name, "ftype": food_type, "qty": int(quantity), "exp": datetime.combine(expiry_date, datetime.min.time()).isoformat() if expiry_date else None, "loc": location})
        else:  # claims
            with st.form("add_claim"):
                food_id = st.number_input("Food ID", step=1, min_value=1)
                receiver_id = st.number_input("Receiver ID", step=1, min_value=1)
                status = st.selectbox("Status", ["Pending", "Completed", "Cancelled"])
                submitted = st.form_submit_button("Add Claim")
                if submitted:
                    run_write("INSERT INTO claims (food_id, receiver_id, status, timestamp) VALUES (:fid, :rid, :status, :ts)", {"fid": int(food_id), "rid": int(receiver_id), "status": status, "ts": datetime.now().isoformat()})

    # UPDATE
    with colB:
        st.markdown("### Update Record")
        id_col = {"providers": "provider_id", "receivers": "receiver_id", "food_listings": "food_id", "claims": "claim_id"}[section]
        rec_id = st.number_input(f"{id_col}", step=1, min_value=1)
        col_to_update = st.text_input("Column to update (e.g., contact)")
        new_val = st.text_input("New value")
        if st.button("Update"):
            if col_to_update:
                q = f"UPDATE {section} SET {col_to_update} = :val WHERE {id_col} = :id"
                run_write(q, {"val": new_val, "id": int(rec_id)})

    # DELETE
    with colC:
        st.markdown("### Delete Record")
        id_col = {"providers": "provider_id", "receivers": "receiver_id", "food_listings": "food_id", "claims": "claim_id"}[section]
        del_id = st.number_input(f"{id_col} to delete", key=f"del_{section}", step=1, min_value=1)
        if st.button("Delete"):
            run_write(f"DELETE FROM {section} WHERE {id_col} = :id", {"id": int(del_id)})

# =============================
# Reports - 16 SQL Queries
# =============================
elif mode == "Reports (16 SQL Queries)":
    st.subheader("Predefined Reports (16 SQL Queries)")

    QUERIES = {
        "Q1: Providers per city": "SELECT city, COUNT(*) AS num_providers FROM providers GROUP BY city ORDER BY num_providers DESC;",
        "Q2: Receivers per city": "SELECT city, COUNT(*) AS num_receivers FROM receivers GROUP BY city ORDER BY num_receivers DESC;",
        "Q3: Which type of food provider contributes the most food": "SELECT p.type AS provider_type, SUM(f.quantity) AS total_quantity FROM food_listings f JOIN providers p ON f.provider_id = p.provider_id GROUP BY p.type ORDER BY total_quantity DESC;",
        "Q4: Contact info of providers by city": "SELECT name, contact, address FROM providers WHERE LOWER(TRIM(city)) = LOWER(TRIM(:city_name));",
        "Q5: Which receivers have claimed the most food": "SELECT r.receiver_id, r.name, COUNT(c.claim_id) AS claims_count FROM claims c JOIN receivers r ON c.receiver_id = r.receiver_id GROUP BY r.receiver_id, r.name ORDER BY claims_count DESC LIMIT 20;",
        "Q6: Total quantity of food available": "SELECT SUM(quantity) AS total_available_quantity FROM food_listings;",
        "Q7: Which city has highest number of food listings": "SELECT location AS city, COUNT(*) AS listings_count FROM food_listings GROUP BY location ORDER BY listings_count DESC LIMIT 10;",
        "Q8: Most commonly available food types": "SELECT food_type, COUNT(*) AS cnt FROM food_listings GROUP BY food_type ORDER BY cnt DESC LIMIT 10;",
        "Q9: Claims count per food item": "SELECT f.food_id, f.food_name, COUNT(c.claim_id) AS claim_count FROM food_listings f LEFT JOIN claims c ON f.food_id = c.food_id GROUP BY f.food_id, f.food_name ORDER BY claim_count DESC;",
        "Q10: Provider with highest number of completed claims": "SELECT p.provider_id, p.name, COUNT(c.claim_id) AS completed_claims FROM claims c JOIN food_listings f ON c.food_id = f.food_id JOIN providers p ON f.provider_id = p.provider_id WHERE LOWER(c.status) = 'completed' GROUP BY p.provider_id, p.name ORDER BY completed_claims DESC LIMIT 10;",
        "Q11: Claim status distribution": "SELECT status, COUNT(*) AS cnt, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM claims), 2) AS pct FROM claims GROUP BY status;",
        "Q12: Average quantity of food claimed per receiver": "SELECT r.receiver_id, r.name, ROUND(AVG(f.quantity),2) AS avg_quantity_per_claim FROM claims c JOIN food_listings f ON c.food_id = f.food_id JOIN receivers r ON c.receiver_id = r.receiver_id GROUP BY r.receiver_id, r.name ORDER BY avg_quantity_per_claim DESC LIMIT 20;",
        "Q13: Meal type claimed the most": "SELECT f.meal_type, COUNT(c.claim_id) AS times_claimed FROM claims c JOIN food_listings f ON c.food_id = f.food_id GROUP BY f.meal_type ORDER BY times_claimed DESC;",
        "Q14: Total quantity donated by each provider": "SELECT p.provider_id, p.name, SUM(f.quantity) AS total_donated FROM food_listings f JOIN providers p ON f.provider_id = p.provider_id GROUP BY p.provider_id, p.name ORDER BY total_donated DESC LIMIT 20;",
        "Q15: Claims per day": "SELECT DATE(timestamp) AS day, COUNT(*) AS claims_count FROM claims GROUP BY day ORDER BY day;",
        "Q16: Distribution efficiency (% completed listings per provider)": "WITH provider_listings AS (SELECT provider_id, COUNT(*) AS total_listings FROM food_listings GROUP BY provider_id), provider_completed AS (SELECT f.provider_id, COUNT(c.claim_id) AS completed_claims FROM claims c JOIN food_listings f ON c.food_id = f.food_id WHERE LOWER(c.status) = 'completed' GROUP BY f.provider_id) SELECT pr.provider_id, pr.name, COALESCE(pc.completed_claims,0) AS completed_claims, pl.total_listings, ROUND(100.0 * COALESCE(pc.completed_claims,0) / pl.total_listings,2) AS pct_completed FROM provider_listings pl JOIN providers pr ON pl.provider_id = pr.provider_id LEFT JOIN provider_completed pc ON pl.provider_id = pc.provider_id ORDER BY pct_completed DESC LIMIT 20;"
    }

    choice = st.selectbox("Select a query", options=list(QUERIES.keys()))
    params = None
    if "Q4" in choice:
        city_param = st.selectbox("City", options=get_distinct_values("providers", "city"))
        params = {"city_name": city_param}
    df = fetch_df(QUERIES[choice], params)
    st.caption(f"Returned {len(df)} row(s)")
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name=f"{choice.replace(' ', '_')}.csv", mime="text/csv")
