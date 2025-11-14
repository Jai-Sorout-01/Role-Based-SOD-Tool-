import streamlit as st
import pandas as pd
import io
from datetime import datetime
import base64

# Page config
st.set_page_config(
    page_title="Victora - Role-Based SoD Conflict Analyzer", 
    page_icon="🔐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_logo():
    """Load and encode the company logo"""
    try:
        with open("Victora logo.svg", "r", encoding="utf-8") as f:
            svg_content = f.read()
        b64_svg = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        return f"data:image/svg+xml;base64,{b64_svg}"
    except:
        return None

def get_logo_html(logo_data):
    """Generate HTML for logo display"""
    if logo_data:
        return f'<img src="{logo_data}" style="height: 80px;" alt="Victora Logo"/>'
    return '<div style="height: 80px; width: 200px; background: linear-gradient(45deg, #667eea, #764ba2); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; font-weight: bold;">VICTORA</div>'

# Enhanced Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main { font-family: 'Inter', sans-serif; }
    
    .company-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .company-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .company-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .company-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        position: relative;
        z-index: 1;
    }
    
    .company-branding {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1.5rem;
        position: relative;
        z-index: 1;
    }
    
    .conflict-card {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.8rem 0;
        box-shadow: 0 8px 25px rgba(238, 90, 36, 0.3);
        border: 1px solid rgba(255,255,255,0.2);
        transition: transform 0.3s ease;
    }
    
    .conflict-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(238, 90, 36, 0.4);
    }
    
    .success-card {
        background: linear-gradient(135deg, #00b894, #00cec9);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0, 184, 148, 0.3);
        margin: 1rem 0;
    }
    
    .info-card {
        background: linear-gradient(135deg, #6c5ce7, #a29bfe);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.8rem 0;
        box-shadow: 0 8px 25px rgba(108, 92, 231, 0.3);
    }
    
    .role-card {
        background: linear-gradient(135deg, #fd79a8, #e84393);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.8rem 0;
        box-shadow: 0 8px 25px rgba(253, 121, 168, 0.3);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    }
    
    .metric-card h2 {
        margin: 0 0 0.5rem 0;
        font-size: 2.2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2.5rem;
        border-radius: 50px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .upload-area {
        background: linear-gradient(135deg, #f9fbfd, #ffffff);
        border: 2px dashed #4a90e2;
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        margin: 2rem 0;
    }
    
    .upload-area:hover {
        border-color: #764ba2;
        transform: translateY(-2px);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Helper functions
def normalize_colname(col):
    return str(col).strip().lower().replace(" ", "_").replace("-", "_").replace("#", "")

@st.cache_data
def load_role_tcode_data(roles_file):
    """Load role-tcode data from uploaded file"""
    try:
        if roles_file.name.endswith('.csv'):
            roles_data = pd.read_csv(roles_file)
        else:
            roles_data = pd.read_excel(roles_file)
        
        roles_data.columns = [normalize_colname(c) for c in roles_data.columns]
        
        # Expected columns: role, tcode
        if 'role' not in roles_data.columns or 'tcode' not in roles_data.columns:
            st.error(f"Required columns 'Role' and 'Tcode' not found. Available: {roles_data.columns.tolist()}")
            return None
        
        roles_data = roles_data[['role', 'tcode']].dropna()
        roles_data['role'] = roles_data['role'].astype(str).str.strip().str.upper()
        roles_data['tcode'] = roles_data['tcode'].astype(str).str.strip().str.upper()
        roles_data = roles_data[(roles_data['role'] != 'NAN') & (roles_data['tcode'] != 'NAN')]
        
        return roles_data.drop_duplicates()
    except Exception as e:
        st.error(f"Error loading role-tcode data: {str(e)}")
        return None

@st.cache_data
def load_risk_data(risk_file):
    """Load risk data from SAP GRC file"""
    try:
        # Load Function T-Code Mapping
        function_map = pd.read_excel(risk_file, sheet_name="Function T-Code Mapping")
        function_map.columns = [normalize_colname(c) for c in function_map.columns]
        
        func_id_col = "function_id"
        tcode_col = "action_(tcodes/apps/services)" if "action_(tcodes/apps/services)" in function_map.columns else "action_(t_codes/apps/services)"
        
        if func_id_col not in function_map.columns:
            st.error(f"Function ID column not found. Available: {function_map.columns.tolist()}")
            return None, None
        
        if tcode_col not in function_map.columns:
            tcode_col = next((c for c in function_map.columns if "action" in c and ("tcode" in c or "t_code" in c)), None)
            if not tcode_col:
                st.error(f"Action (T-Codes) column not found. Available: {function_map.columns.tolist()}")
                return None, None
        
        function_map = function_map[[func_id_col, tcode_col]].rename(columns={tcode_col: "tcode"})
        
        # Expand comma-separated tcodes
        expanded_functions = []
        for _, row in function_map.iterrows():
            function_id = str(row['function_id']).strip().upper()
            tcodes = str(row['tcode']).strip()
            if tcodes and tcodes not in ['nan', 'NaN', '']:
                for tcode in tcodes.replace(';', ',').split(','):
                    tcode = tcode.strip().upper()
                    if tcode:
                        expanded_functions.append({"function_id": function_id, "tcode": tcode})
        
        function_map_expanded = pd.DataFrame(expanded_functions).drop_duplicates()
        
        # Load Risk Function Mapping
        risk_pairs = pd.read_excel(risk_file, sheet_name="Risk Function Mapping")
        risk_pairs.columns = [normalize_colname(c) for c in risk_pairs.columns]
        
        conflict_cols = [c for c in risk_pairs.columns if "conflicting_function" in c and any(char.isdigit() for char in c)]
        
        if not conflict_cols:
            st.error(f"Conflicting Function columns not found. Available: {risk_pairs.columns.tolist()}")
            return None, None
        
        risk_function_pairs = []
        for _, row in risk_pairs.iterrows():
            risk_id = str(row.get("access_risk_id", "")).strip().upper()
            risk_type = str(row.get("risk_type", "")).strip()
            business_process = str(row.get("business_process", "")).strip()
            functions = []
            
            for col in conflict_cols:
                val = row[col]
                if pd.notna(val):
                    val = str(val).strip().upper()
                    if " - " in val:
                        val = val.split(" - ")[0].strip()
                    if val and val not in ['NAN', '']:
                        functions.append(val)
            
            functions = sorted(set(functions))
            for i in range(len(functions)):
                for j in range(i + 1, len(functions)):
                    risk_function_pairs.append({
                        "business_process": business_process,
                        "risk_type": risk_type,
                        "risk_id": risk_id,
                        "function_1": functions[i],
                        "function_2": functions[j]
                    })
        
        risk_pairs_df = pd.DataFrame(risk_function_pairs).drop_duplicates()
        
        # Remove invalid entries
        risk_pairs_df = risk_pairs_df[
            (risk_pairs_df["risk_id"] != "") & 
            (risk_pairs_df["risk_id"] != "NAN") &
            (risk_pairs_df["function_1"] != "") &
            (risk_pairs_df["function_2"] != "") &
            (risk_pairs_df["function_1"] != "NAN") &
            (risk_pairs_df["function_2"] != "NAN")
        ]
        
        # Add tcode info
        func_tcodes = function_map_expanded.groupby("function_id")["tcode"].apply(
            lambda x: ", ".join(sorted(set(x)))
        ).reset_index()
        
        risk_pairs_df = risk_pairs_df.merge(
            func_tcodes, left_on="function_1", right_on="function_id", how="left"
        ).rename(columns={"tcode": "tcode1"}).drop(columns=["function_id"])
        
        risk_pairs_df = risk_pairs_df.merge(
            func_tcodes, left_on="function_2", right_on="function_id", how="left"
        ).rename(columns={"tcode": "tcode2"}).drop(columns=["function_id"])
        
        return function_map_expanded, risk_pairs_df
    except Exception as e:
        st.error(f"Error loading risk data: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None, None

def analyze_role_conflicts(role_name, roles_tcode, function_map, risk_pairs):
    """Analyze conflicts within a single role"""
    role_name = str(role_name).strip().upper()
    role_data = roles_tcode[roles_tcode["role"] == role_name]
    
    if role_data.empty:
        return {
            "role": role_name, "conflicts": [], "functions": [], 
            "tcodes": [], "conflict_count": 0, 
            "error": f"Role {role_name} not found"
        }
    
    role_tcodes_list = list(role_data["tcode"].unique())
    
    if len(role_tcodes_list) == 0:
        return {
            "role": role_name, "conflicts": [], "functions": [], 
            "tcodes": [], "conflict_count": 0, 
            "error": f"No T-codes found for role {role_name}"
        }
    
    # Map role's tcodes to functions
    role_func = role_data.merge(function_map, on="tcode", how="left")
    role_functions = list(role_func["function_id"].dropna().unique())
    
    # Track which functions this role has access to (with tcodes)
    role_function_access = {}
    for _, row in role_func.iterrows():
        if pd.notna(row["function_id"]):
            func_id = row["function_id"]
            tcode = row["tcode"]
            
            if func_id not in role_function_access:
                role_function_access[func_id] = set()
            role_function_access[func_id].add(tcode)
    
    # Check for conflicts WITHIN the role
    conflicts = []
    processed_pairs = set()
    
    for _, risk_pair in risk_pairs.iterrows():
        func1 = str(risk_pair.get("function_1", "")).strip()
        func2 = str(risk_pair.get("function_2", "")).strip()
        risk_id = str(risk_pair.get("risk_id", "")).strip()
        risk_type = str(risk_pair.get("risk_type", "")).strip()
        business_process = str(risk_pair.get("business_process", "")).strip()
        
        if not all([func1, func2, risk_id]) or any(x == 'NAN' for x in [func1, func2, risk_id]):
            continue
        
        # CONFLICT: Role has BOTH conflicting functions
        if func1 in role_function_access and func2 in role_function_access:
            func_pair = tuple(sorted([func1, func2]))
            if func_pair not in processed_pairs:
                processed_pairs.add(func_pair)
                
                func1_tcodes = list(role_function_access[func1])
                func2_tcodes = list(role_function_access[func2])
                
                conflicts.append({
                    "type": f"SoD Violation ({risk_id})",
                    "business_process": business_process if business_process and business_process != 'NAN' else "Not Specified",
                    "risk_type": risk_type if risk_type and risk_type != 'NAN' else "Not Specified",
                    "function_1": func1,
                    "function_2": func2,
                    "description": f"Role has conflicting T-codes from both functions",
                    "risk_id": risk_id,
                    "tcode_1": ", ".join(sorted(func1_tcodes)),
                    "tcode_2": ", ".join(sorted(func2_tcodes)),
                })
    
    return {
        "role": role_name,
        "functions": role_functions,
        "tcodes": role_tcodes_list,
        "conflicts": conflicts,
        "conflict_count": len(conflicts)
    }

def analyze_all_roles(roles_tcode, function_map, risk_pairs):
    """Analyze conflicts for all roles"""
    all_roles = roles_tcode["role"].unique()
    role_summary = []
    all_conflicts = []
    
    for role_name in all_roles:
        result = analyze_role_conflicts(role_name, roles_tcode, function_map, risk_pairs)
        
        role_summary.append({
            "Role": result["role"],
            "Total_Tcodes": len(result["tcodes"]),
            "Total_Functions": len(result["functions"]),
            "Conflicts_Found": result["conflict_count"],
            "Risk_Status": "HIGH RISK" if result["conflict_count"] > 0 else "CLEAN"
        })
        
        for conflict in result["conflicts"]:
            all_conflicts.append({
                "Role": result["role"],
                "Risk_ID": conflict["risk_id"],
                "Business_Process": conflict.get("business_process", "Not Specified"),
                "Risk_Type": conflict.get("risk_type", "Not Specified"),
                "Function_1": conflict["function_1"],
                "Function_2": conflict["function_2"],
                "Tcode_1": conflict["tcode_1"],
                "Tcode_2": conflict["tcode_2"],
                "Description": conflict["description"]
            })
    
    return pd.DataFrame(role_summary), pd.DataFrame(all_conflicts)

def create_excel_report(role_summary, role_conflicts, roles_tcode, function_map, risk_pairs):
    """Create comprehensive Excel report"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        role_summary.to_excel(writer, sheet_name="Role_Summary", index=False)
        role_conflicts.to_excel(writer, sheet_name="Role_Conflicts", index=False)
        roles_tcode.to_excel(writer, sheet_name="Role_Tcode_Mapping", index=False)
        function_map.to_excel(writer, sheet_name="Function_Tcodes", index=False)
        risk_pairs.to_excel(writer, sheet_name="Risk_Pairs", index=False)
    
    output.seek(0)
    return output.read()

# Initialize session state
if "roles_tcode" not in st.session_state:
    st.session_state.roles_tcode = None
if "function_map" not in st.session_state:
    st.session_state.function_map = None
if "risk_pairs" not in st.session_state:
    st.session_state.risk_pairs = None

# Header with branding
logo_data = load_logo()
st.markdown(f"""
<div class="company-header">
    <div class="company-branding">
        {get_logo_html(logo_data)}
    </div>
    <h1>🔐 Role-Based SoD Conflict Analyzer</h1>
    <p>Detect Conflicting T-codes Within SAP Roles</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - File Uploads
with st.sidebar:
    st.markdown("## 📁 Upload Required Files")
    
    # 1. Role-Tcode Data
    st.markdown("### 1️⃣ Role-Tcode Mapping File")
    st.caption("Must contain: Role and Tcode columns")
    roles_file = st.file_uploader(
        "Upload Role-Tcode File",
        type=["xlsx", "xls", "csv"],
        key="roles_upload"
    )
    
    if roles_file:
        if st.session_state.roles_tcode is None:
            with st.spinner("Processing role-tcode data..."):
                st.session_state.roles_tcode = load_role_tcode_data(roles_file)
                if st.session_state.roles_tcode is not None:
                    st.success("✅ Role-Tcode data loaded!")
        else:
            st.success("✅ Role-Tcode data loaded!")
    
    st.markdown("---")
    
    # 2. SAP GRC Risk File
    st.markdown("### 2️⃣ SAP GRC Risk File")
    st.caption("Must contain: Function T-Code Mapping and Risk Function Mapping sheets")
    risk_file = st.file_uploader(
        "Upload SAP GRC File",
        type=["xlsx", "xls"],
        key="risk_upload"
    )
    
    if risk_file:
        if st.session_state.function_map is None:
            with st.spinner("Processing risk data..."):
                func_map, risk_pairs = load_risk_data(risk_file)
                if func_map is not None and risk_pairs is not None:
                    st.session_state.function_map = func_map
                    st.session_state.risk_pairs = risk_pairs
                    st.success("✅ Risk data loaded!")
        else:
            st.success("✅ Risk data loaded!")
    
    # Show stats
    if all([st.session_state.roles_tcode is not None,
            st.session_state.function_map is not None,
            st.session_state.risk_pairs is not None]):
        st.markdown("---")
        st.markdown("### 📊 Data Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🔐 Roles", len(st.session_state.roles_tcode["role"].unique()))
            st.metric("⚙️ Functions", len(st.session_state.function_map["function_id"].unique()))
        with col2:
            st.metric("💻 T-Codes", len(st.session_state.roles_tcode["tcode"].unique()))
            st.metric("🔗 Risk Pairs", len(st.session_state.risk_pairs))

# Main content
if all([st.session_state.roles_tcode is not None,
        st.session_state.function_map is not None,
        st.session_state.risk_pairs is not None]):
    
    tab1, tab2 = st.tabs(["🔍 Single Role Analysis", "📊 Complete Role Report"])
    
    # TAB 1: Single Role Analysis
    with tab1:
        st.markdown("### 🎯 Select Role to Analyze")
        
        available_roles = sorted(st.session_state.roles_tcode["role"].unique())
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            role_input = st.selectbox(
                "Choose Role",
                options=[""] + available_roles,
                key="role_selector"
            )
            
            st.markdown("**OR**")
            
            manual_role = st.text_input(
                "Type Role Name",
                placeholder="Enter role name...",
                key="manual_role"
            )
        
        with col2:
            final_role = manual_role.strip() if manual_role.strip() else role_input
            
            if final_role:
                role_info = st.session_state.roles_tcode[
                    st.session_state.roles_tcode["role"] == final_role.upper()
                ]
                if not role_info.empty:
                    role_tcodes_count = role_info["tcode"].nunique()
                    
                    st.markdown(f"""
                    <div class="role-card">
                        <h4>🔐 Role Information</h4>
                        <p><strong>Role:</strong> {final_role.upper()}</p>
                        <p><strong>T-Codes:</strong> {role_tcodes_count}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        if final_role and final_role != "":
            role_data = analyze_role_conflicts(
                final_role, 
                st.session_state.roles_tcode,
                st.session_state.function_map,
                st.session_state.risk_pairs
            )
            
            st.markdown("---")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h2>{len(role_data['tcodes'])}</h2>
                    <p>T-Codes</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h2>{len(role_data['functions'])}</h2>
                    <p>Functions</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h2 style="color: {'#e74c3c' if role_data['conflict_count'] > 0 else '#27ae60'}">{role_data['conflict_count']}</h2>
                    <p>Conflicts</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                status = "🔴 HIGH RISK" if role_data['conflict_count'] > 0 else "🟢 CLEAN"
                color = "#e74c3c" if role_data['conflict_count'] > 0 else "#27ae60"
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: {color}">{status}</h4>
                    <p>Status</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Details
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ⚙️ Functions Accessed")
                if role_data['functions']:
                    for func in role_data['functions'][:15]:
                        st.markdown(f"• `{func}`")
                    if len(role_data['functions']) > 15:
                        st.info(f"... and {len(role_data['functions']) - 15} more")
                else:
                    st.info("No functions found")
            
            with col2:
                st.markdown("### 💻 T-Codes")
                if role_data['tcodes']:
                    for tcode in role_data['tcodes'][:15]:
                        st.markdown(f"• `{tcode}`")
                    if len(role_data['tcodes']) > 15:
                        st.info(f"... and {len(role_data['tcodes']) - 15} more")
                else:
                    st.info("No T-codes found")
            
            # Conflicts
            if role_data['conflicts']:
                st.markdown("### ⚠️ Detected Conflicts Within Role")
                for conflict in role_data['conflicts']:
                    business_proc = conflict.get('business_process', 'Not Specified')
                    risk_type = conflict.get('risk_type', 'Not Specified')
                    
                    st.markdown(f"""
                    <div class="conflict-card">
                        <h4>{conflict['type']}</h4>
                        <p><strong>Business Process:</strong> {business_proc}</p>
                        <p><strong>Risk Type:</strong> {risk_type}</p>
                        <p><strong>{conflict['function_1']}</strong> ↔️ <strong>{conflict['function_2']}</strong></p>
                        <p>{conflict['description']}</p>
                        <small>Conflicting T-Codes: {conflict['tcode_1']} ↔️ {conflict['tcode_2']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="success-card">
                    <h3>🎉 No Conflicts Found!</h3>
                    <p>This role has proper segregation of duties</p>
                </div>
                """, unsafe_allow_html=True)
    
    # TAB 2: Complete Role Report
    with tab2:
        st.markdown("### 📊 Generate Complete Role Conflict Report")
        
        st.markdown("""
        <div class="info-card">
            <h4>📋 Report Contents</h4>
            <p>This comprehensive report will analyze ALL roles and include:</p>
            <ul>
                <li><strong>Role_Summary:</strong> Overview of all roles with conflict statistics</li>
                <li><strong>Role_Conflicts:</strong> Detailed conflict information for each role</li>
                <li><strong>Role_Tcode_Mapping:</strong> Complete role-tcode mappings</li>
                <li><strong>Function_Tcodes:</strong> Function to T-code relationships</li>
                <li><strong>Risk_Pairs:</strong> All risk pairs from SAP GRC</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 Generate Complete Report", type="primary", use_container_width=True):
                with st.spinner("🔄 Analyzing all roles and generating comprehensive report..."):
                    progress = st.progress(0)
                    
                    # Analyze all roles
                    progress.progress(30)
                    role_summary, role_conflicts = analyze_all_roles(
                        st.session_state.roles_tcode,
                        st.session_state.function_map,
                        st.session_state.risk_pairs
                    )
                    
                    progress.progress(80)
                    progress.progress(100)
                    
                    st.markdown("---")
                    st.success("✅ Analysis Complete!")
                    
                    # Display summary statistics
                    st.markdown("### 📈 Report Summary")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        total_roles = len(role_summary)
                        st.markdown(f"""
                        <div class="metric-card">
                            <h2>{total_roles}</h2>
                            <p>Total Roles</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        roles_with_conflicts = len(role_summary[role_summary["Conflicts_Found"] > 0])
                        st.markdown(f"""
                        <div class="metric-card">
                            <h2 style="color: #e74c3c">{roles_with_conflicts}</h2>
                            <p>Roles with Conflicts</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        total_conflicts = len(role_conflicts)
                        st.markdown(f"""
                        <div class="metric-card">
                            <h2 style="color: #e74c3c">{total_conflicts}</h2>
                            <p>Total Conflicts</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        clean_roles = total_roles - roles_with_conflicts
                        st.markdown(f"""
                        <div class="metric-card">
                            <h2 style="color: #27ae60">{clean_roles}</h2>
                            <p>Clean Roles</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Display preview of results
                    if not role_conflicts.empty:
                        st.markdown("### ⚠️ Roles with Conflicts (Top 10)")
                        top_roles = role_summary.nlargest(10, "Conflicts_Found")
                        st.dataframe(top_roles, use_container_width=True)
                        
                        st.markdown("### 🔍 Conflict Details (Preview - First 20)")
                        st.dataframe(role_conflicts.head(20), use_container_width=True)
                        
                        # Conflict distribution analysis
                        st.markdown("### 📊 Conflict Distribution")
                        conflict_stats = role_summary[role_summary["Conflicts_Found"] > 0]
                        
                        if not conflict_stats.empty:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("""
                                <div class="info-card">
                                    <h4>📈 Conflict Statistics</h4>
                                """, unsafe_allow_html=True)
                                st.write(f"**Average conflicts per role:** {conflict_stats['Conflicts_Found'].mean():.2f}")
                                st.write(f"**Max conflicts (single role):** {conflict_stats['Conflicts_Found'].max()}")
                                st.write(f"**Min conflicts (affected roles):** {conflict_stats['Conflicts_Found'].min()}")
                                st.markdown("</div>", unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown("""
                                <div class="info-card">
                                    <h4>🎯 Risk Overview</h4>
                                """, unsafe_allow_html=True)
                                high_risk = len(conflict_stats[conflict_stats["Conflicts_Found"] >= 5])
                                medium_risk = len(conflict_stats[(conflict_stats["Conflicts_Found"] >= 2) & (conflict_stats["Conflicts_Found"] < 5)])
                                low_risk = len(conflict_stats[conflict_stats["Conflicts_Found"] < 2])
                                st.write(f"**High Risk (≥5 conflicts):** {high_risk} roles")
                                st.write(f"**Medium Risk (2-4 conflicts):** {medium_risk} roles")
                                st.write(f"**Low Risk (1 conflict):** {low_risk} roles")
                                st.markdown("</div>", unsafe_allow_html=True)
                            
                            # Risk type distribution
                            if 'Risk_Type' in role_conflicts.columns:
                                st.markdown("### 📋 Top Risk Types")
                                risk_type_counts = role_conflicts['Risk_Type'].value_counts().head(10)
                                if not risk_type_counts.empty:
                                    st.bar_chart(risk_type_counts)
                    else:
                        st.markdown("""
                        <div class="success-card">
                            <h2>🎉 No Conflicts Found!</h2>
                            <p>All roles have proper segregation of duties</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Generate Excel report
                    st.markdown("### 📥 Download Complete Report")
                    
                    excel_data = create_excel_report(
                        role_summary,
                        role_conflicts,
                        st.session_state.roles_tcode,
                        st.session_state.function_map,
                        st.session_state.risk_pairs
                    )
                    
                    filename = f"Role_SoD_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    
                    st.download_button(
                        label="📥 Download Complete Excel Report (All 5 Sheets)",
                        data=excel_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        type="primary"
                    )
                    
                    st.markdown("""
                    <div class="info-card">
                        <h4>📋 Report Contains:</h4>
                        <ul>
                            <li><strong>Role_Summary:</strong> Overall statistics for each role (Role name, T-code count, Function count, Conflict count, Risk status)</li>
                            <li><strong>Role_Conflicts:</strong> Detailed conflict information (Role, Risk ID, Business Process, Risk Type, Conflicting functions, Conflicting T-codes)</li>
                            <li><strong>Role_Tcode_Mapping:</strong> Complete role-to-tcode mapping for traceability</li>
                            <li><strong>Function_Tcodes:</strong> Function to T-code mapping from SAP GRC</li>
                            <li><strong>Risk_Pairs:</strong> All risk pairs with conflicting functions from SAP GRC</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="upload-area">
        <h3>👈 Please upload both required files from the sidebar:</h3>
        
        <h4>1. Role-Tcode Mapping File</h4>
        <p>This file should contain role and T-code information with exactly these columns:</p>
        <ul>
            <li><code>Role</code> - Role names (e.g., SAP_FI_ACCOUNTANT, SAP_MM_BUYER)</li>
            <li><code>Tcode</code> - Transaction codes assigned to each role (e.g., FB01, ME21N, VA01)</li>
        </ul>
        <p><strong>Format:</strong> Excel (.xlsx, .xls) or CSV (.csv)</p>
        <p><strong>Example:</strong></p>
        <table style="border: 1px solid #ddd; border-collapse: collapse; margin: 10px 0;">
            <tr style="background: #f8f9fa;">
                <th style="border: 1px solid #ddd; padding: 8px;">Role</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Tcode</th>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">SAP_FI_ACCOUNTANT</td>
                <td style="border: 1px solid #ddd; padding: 8px;">FB01</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">SAP_FI_ACCOUNTANT</td>
                <td style="border: 1px solid #ddd; padding: 8px;">FB50</td>
            </tr>
        </table>
        
        <h4>2. SAP GRC Risk File</h4>
        <p>This file must contain the following sheets with exact column names:</p>
        
        <p><strong>Sheet 1: Function T-Code Mapping</strong></p>
        <ul>
            <li><code>Business Process</code> - Business process name</li>
            <li><code>Function ID</code> - Unique function identifier</li>
            <li><code>Function Description</code> - Description of the function</li>
            <li><code>Action (T-Codes/Apps/Services)</code> - T-codes associated with function (comma-separated)</li>
            <li><code>Action Description</code> - Description of actions</li>
            <li><code>Proposal</code> - Optional proposal field</li>
        </ul>
        
        <p><strong>Sheet 2: Risk Function Mapping</strong></p>
        <ul>
            <li><code>Business Process</code> - Business process name</li>
            <li><code>Risk Type</code> - Type of risk</li>
            <li><code>Access Risk ID</code> - Unique risk identifier</li>
            <li><code>Conflicting Function #1</code> - First conflicting function</li>
            <li><code>Conflicting Function #2</code> - Second conflicting function</li>
            <li><code>Conflicting Function #3</code> - Third conflicting function (optional, can have more)</li>
            <li>Other columns: Proposal, Proposed By, Comments, Client Confirmation, Confirmed By</li>
        </ul>
        
        <p><strong>Sheet 3: Function Permission Proposal</strong> (Optional)</p>
        <ul>
            <li><code>Action</code>, <code>Auth Object</code>, <code>Auth Field</code>, <code>Low Value</code>, <code>High Value</code>, <code>Operator</code>, <code>Status</code></li>
        </ul>
        
        <p><strong>Format:</strong> Excel (.xlsx, .xls)</p>
        
        <p style="margin-top: 1.5rem;"><strong>Both files are required to perform role-based conflict analysis.</strong></p>
        
        <h4 style="color: #e74c3c; margin-top: 2rem;">What This Tool Does:</h4>
        <p>This analyzer checks for <strong>SoD conflicts WITHIN each role</strong>. It identifies when a single role contains T-codes that belong to conflicting functions according to SAP GRC risk rules.</p>
        <p><strong>Example:</strong> If Role "SAP_FI_FULL" has both T-codes for "Create Invoice" (Function A) and "Approve Payment" (Function B), and these two functions are marked as conflicting in the GRC risk file, this tool will flag it as a segregation of duties violation.</p>
    </div>
    """, unsafe_allow_html=True)

# Footer with company branding
st.markdown("---")
st.markdown(f"""
<div class="company-footer">
    <div class="company-branding">
        {get_logo_html(logo_data)}
    </div>
    <h4>Victora - Role-Based SoD Conflict Analyzer</h4>
    <p>Detect Conflicting T-codes Within SAP Roles</p>
    <small>Empowering organizations with intelligent conflict detection and risk management</small>
</div>
""", unsafe_allow_html=True)