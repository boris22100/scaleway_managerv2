import streamlit as st
import requests
import pandas as pd
import sqlite3
import os
import hashlib
from datetime import datetime

st.set_page_config(page_title="Scaleway Cloud Manager", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], .main, stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #0d2a3a !important;
        color: #ffffff !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        background: transparent !important;
        color: transparent !important;
    }
    [data-testid="stHeader"] * {
        visibility: hidden !important;
    }
    [data-testid="stHeader"] button[data-testid="sidebar-button"] {
        visibility: visible !important;
        color: #ffffff !important;
    }
    
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
    
    [data-testid="stSidebar"] {
        background-color: #081b26 !important;
        color: #ffffff !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: #0d2a3a !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        background-color: #081b26;
        padding: 6px 6px 0 6px;
        border-radius: 8px 8px 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        font-weight: 500;
        font-size: 14px;
        color: #a0aec0 !important;
        border-radius: 6px 6px 0 0;
        padding: 0 16px;
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        color: #4ade80 !important;
        background-color: #0d2a3a !important;
        border-color: rgba(255, 255, 255, 0.1) rgba(255, 255, 255, 0.1) #0d2a3a rgba(255, 255, 255, 0.1) !important;
        font-weight: 600;
    }
    
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #a0aec0 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    
    .stButton>button {
        background-color: #4ade80 !important;
        color: #081b26 !important;
        border: 1px solid #4ade80 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 6px 16px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background-color: #4ade80 !important;
        border-color: #4ade80 !important;
        box-shadow: 0 4px 14px rgba(74, 222, 128, 0.4) !important;
        transform: translateY(-1px);
    }
    
    div[data-testid="stForm"] {
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        background-color: rgba(255, 255, 255, 0.02) !important;
        padding: 24px !important;
    }
    
    code {
        color: #4ade80 !important;
        background-color: #081b26 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 4px !important;
    }
    
    .stDataFrame, div[data-testid="stTable"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border-radius: 8px;
    }
    
    div[data-baseweb="input"] {
        background-color: #081b26 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
        color: #ffffff !important;
    }
    
    h1, h2, h3, h4, h5, h6, label {
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

DB_PATH = "data/manager.db"
if not os.path.exists("data"): os.makedirs("data")

def db_query(query, params=(), fetch=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(query, params)
        res = c.fetchall() if fetch else None
        conn.commit()
        return res
    except Exception as e:
        st.error(f"Erreur DB interne : {e}")
        return []
    finally:
        conn.close()

db_query("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT, approved INTEGER DEFAULT 0)")
db_query("CREATE TABLE IF NOT EXISTS accounts (user_id INTEGER, name TEXT, access_key TEXT, secret_key TEXT, project_id TEXT, PRIMARY KEY(user_id, name))")
db_query("CREATE TABLE IF NOT EXISTS templates (user_id INTEGER, name TEXT, content TEXT, PRIMARY KEY(user_id, name))")

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password, hashed_text): return make_hashes(password) == hashed_text

if 'logged_in' not in st.session_state:
    if "token" in st.query_params:
        u_id = st.query_params["token"]
        res = db_query("SELECT id, username, role FROM users WHERE id=?", (u_id,), fetch=True)
        if res: st.session_state.update({'logged_in': True, 'user_id': res[0][0], 'username': res[0][1], 'role': res[0][2]})
        else: st.session_state['logged_in'] = False
    else: st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Authentification BoWiz")
    t_login, t_reg = st.tabs(["Connexion", "Création de compte"])
    with t_login:
        with st.form("login_form"):
            u = st.text_input("Identifiant")
            p = st.text_input("Mot de passe", type='password')
            if st.form_submit_button("Se connecter", use_container_width=True):
                res = db_query("SELECT id, password, role, approved FROM users WHERE username=?", (u,), fetch=True)
                if res and check_hashes(p, res[0][1]):
                    if res[0][3] == 1 or res[0][2] == 'admin':
                        st.session_state.update({'logged_in': True, 'user_id': res[0][0], 'username': u, 'role': res[0][2]})
                        st.query_params["token"] = str(res[0][0])
                        st.rerun()
                    else: st.warning("Votre compte est en attente d'approbation par un administrateur.")
                else: st.error("Identifiants invalides.")
    with t_reg:
        with st.form("reg_form"):
            nu = st.text_input("Nouvel Identifiant")
            np = st.text_input("Nouveau Mot de passe", type='password')
            if st.form_submit_button("Soumettre la demande"):
                count = db_query("SELECT COUNT(*) FROM users", fetch=True)[0][0]
                role, appr = ('admin', 1) if count == 0 else ('user', 0)
                db_query("INSERT INTO users (username, password, role, approved) VALUES (?,?,?,?)", (nu, make_hashes(np), role, appr))
                st.success("Demande d'inscription envoyée !")
    st.stop()

UID, ROLE = st.session_state['user_id'], st.session_state['role']
accounts_db = db_query("SELECT name, access_key, secret_key, project_id FROM accounts WHERE user_id=?", (UID,), fetch=True)
acc_names = [a[0] for a in accounts_db]
templates_db = db_query("SELECT name, content FROM templates WHERE user_id=?", (UID,), fetch=True)
tmpl_dict = {t[0]: t[1] for t in templates_db}

st.sidebar.subheader(f"👤 {st.session_state['username']}")
selected_acc = st.sidebar.selectbox("Profil Cloud Scaleway", ["---"] + acc_names)
SCW_SECRET, SCW_PROJECT = "", ""
if selected_acc != "---":
    curr = next(a for a in accounts_db if a[0] == selected_acc)
    SCW_SECRET, SCW_PROJECT = curr[2], curr[3]

if st.sidebar.button("🚪 Déconnexion", use_container_width=True):
    st.session_state.clear()
    st.query_params.clear()
    st.rerun()

HEADERS = {"X-Auth-Token": SCW_SECRET, "Content-Type": "application/json"}

tabs_labels = ["📊 Dashboard", "🌐 DNS", "🖥️ Instances", "🌍 Réseau & Routage", "🌱 Écologie", "💰 Facturation", "📝 Templates", "⚙️ Profils"]
if ROLE == 'admin': tabs_labels.append("👑 Gouvernance")
tabs = st.tabs(tabs_labels)

def parse_scw_price(price_field):
    if pd.isna(price_field) or price_field is None: return 0.0
    if isinstance(price_field, dict):
        units = price_field.get('units', 0)
        nanos = price_field.get('nanos', 0)
        return float(units) + (float(nanos) / 1000000000)
    return float(price_field)

with tabs[0]:
    st.header("📊 Tableau de bord")
    if selected_acc == "---": 
        st.info("Veuillez sélectionner un profil Scaleway dans la barre latérale pour charger les indicateurs de synthèse.")
    else:
        with st.spinner("Génération de la synthèse en cours..."):
            instances_actives, instances_totatles = 0, 0
            for zone in ["fr-par-1", "fr-par-2"]:
                res_inst = requests.get(f"https://api.scaleway.com/instance/v1/zones/{zone}/servers", headers=HEADERS)
                if res_inst.status_code == 200:
                    srvs = res_inst.json().get("servers", [])
                    instances_totatles += len(srvs)
                    instances_actives += sum(1 for s in srvs if s['state'] == 'running')

            total_domaines = 0
            res_dns = requests.get("https://api.scaleway.com/domain/v2beta1/dns-zones?page_size=1", headers=HEADERS)
            if res_dns.status_code == 200: total_domaines = res_dns.json().get("total_count", 0)

            factures_payees, encours_financier = 0.0, 0.0
            res_bill = requests.get(f"https://api.scaleway.com/billing/v2beta1/invoices?project_id={SCW_PROJECT}", headers=HEADERS)
            if res_bill.status_code == 200:
                factures = res_bill.json().get("invoices", [])
                for f in factures:
                    ttc = parse_scw_price(f.get('total_taxed'))
                    if f.get('state') == 'paid': factures_payees += ttc
                    else: encours_financier += ttc

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Instances en production", f"🟢 {instances_actives}", f"Total configuré : {instances_totatles}")
        m2.metric("Périmètre DNS", f"🌍 {total_domaines} Zone(s)")
        m3.metric("Factures réglées", f"{factures_payees:.2f} €")
        m4.metric("Reste à régulariser", f"{encours_financier:.2f} €", delta_color="inverse")

with tabs[1]:
    st.header("🌐 Gestionnaire de Zones DNS & Routage")
    if selected_acc == "---": st.warning("Sélectionnez un profil.")
    else:
        z_res = requests.get("https://api.scaleway.com/domain/v2beta1/dns-zones?page_size=100", headers=HEADERS)
        if z_res.status_code == 200:
            zones = z_res.json().get("dns_zones", [])
            st.write("### Sélectionner un domaine à administrer")
            cols = st.columns(4)
            for idx, z_item in enumerate(zones):
                if cols[idx % 4].button(f"🗺️ {z_item['domain']}", key=f"zone_btn_{z_item['domain']}", use_container_width=True):
                    st.session_state['active_dns_zone'] = z_item['domain']

            active_zone = st.session_state.get('active_dns_zone')
            if active_zone:
                st.markdown(f"#### Enregistrements actifs pour : `{active_zone}`")
                
                rec_res = requests.get(f"https://api.scaleway.com/domain/v2beta1/dns-zones/{active_zone}/records?page_size=150", headers=HEADERS)
                if rec_res.status_code == 200:
                    records_list = rec_res.json().get("records", [])
                    if records_list:
                        for r_idx, r_data in enumerate(records_list):
                            r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns([2, 1, 4, 1, 1])
                            r_col1.write(f"`{r_data['name'] if r_data['name'] != '' else '@'}`")
                            r_col2.info(r_data['type'])
                            r_col3.code(r_data['data'])
                            r_col4.caption(f"TTL: {r_data['ttl']}")
                            if r_col5.button("🗑️", key=f"delete_rec_{active_zone}_{r_idx}"):
                                payload = {"changes": [{"delete": {"name": r_data['name'], "type": r_data['type'], "data": r_data['data']}}]}
                                patch_res = requests.patch(f"https://api.scaleway.com/domain/v2beta1/dns-zones/{active_zone}/records", json=payload, headers=HEADERS)
                                if patch_res.status_code == 200:
                                    st.toast("Enregistrement supprimé !")
                                    st.rerun()
                                else: st.error("Erreur lors de la suppression.")

                st.divider()
                act_col1, act_col2 = st.columns(2)
                with act_col1:
                    st.markdown("##### ➕ Ajouter / Modifier un enregistrement")
                    with st.form("dns_upsert_form"):
                        sub_n = st.text_input("Sous-domaine (Ex: app ou vide pour la racine)")
                        sub_t = st.selectbox("Type de champ", ["A", "AAAA", "CNAME", "TXT", "MX"])
                        sub_v = st.text_input("Cible / Valeur (Ex: IP ou cible DNS)")
                        sub_ttl = st.number_input("TTL (secondes)", min_value=60, value=3600)
                        if st.form_submit_button("Pousser la modification"):
                            payload = {"changes": [{"add": {"records": [{"name": sub_n, "type": sub_t, "data": sub_v, "ttl": int(sub_ttl)}]}}]}
                            r_patch = requests.patch(f"https://api.scaleway.com/domain/v2beta1/dns-zones/{active_zone}/records", json=payload, headers=HEADERS)
                            if r_patch.status_code == 200: st.rerun()
                            else: st.error(f"Refus de l'API Scaleway : {r_patch.text}")
                
                with act_col2:
                    st.markdown("##### 📋 Importation & Écriture en bloc")
                    bulk_text = st.text_area("Format : nom_sous_domaine type valeur (un par ligne)", placeholder="www A 185.20.10.5\napi CNAME core.bowiz.fr")
                    if st.button("Lancer la synchronisation en masse", use_container_width=True):
                        batch_changes = []
                        for line in bulk_text.split('\n'):
                            tokens = line.strip().split()
                            if len(tokens) >= 3:
                                batch_changes.append({"name": tokens[0] if tokens[0] != "@" else "", "type": tokens[1], "data": " ".join(tokens[2:]), "ttl": 3600})
                        if batch_changes:
                            payload = {"changes": [{"set": {"records": batch_changes}}]}
                            r_bulk = requests.patch(f"https://api.scaleway.com/domain/v2beta1/dns-zones/{active_zone}/records", json=payload, headers=HEADERS)
                            if r_bulk.status_code == 200:
                                st.success("Zone mise à jour en bloc avec succès !")
                                st.rerun()
                            else: st.error(f"Échec de l'import global : {r_bulk.text}")

with tabs[2]:
    st.header("🖥️ Parc d'Instances Virtuelles Compute")
    if selected_acc == "---": st.info("Sélectionnez un profil.")
    else:
        zones_to_query = ["fr-par-1", "fr-par-2"]
        st.write("### État d'infrastructure en temps réel")
        
        for z in zones_to_query:
            st.markdown(f"#### 📍 Zone d'infrastructure : `{z.upper()}`")
            r_servers = requests.get(f"https://api.scaleway.com/instance/v1/zones/{z}/servers", headers=HEADERS)
            
            if r_servers.status_code == 200:
                servers_list = r_servers.json().get("servers", [])
                if not servers_list:
                    st.caption("Aucune machine virtuelle détectée sur cette zone de disponibilité.")
                else:
                    for s in servers_list:
                        s_c1, s_c2, s_c3, s_c4 = st.columns([3, 2, 1, 2])
                        s_c1.write(f"🔹 **{s['name']}** (`{s['commercial_type']}`)")
                        pub_ip = s.get('public_ip', {}).get('address', 'Pas d\'IP assignée')
                        s_c2.code(pub_ip)
                        s_c3.write("🟢 RUN" if s['state'] == 'running' else f"⚠️ {s['state'].upper()}")
                        
                        with s_c4:
                            act_c1, act_c2 = st.columns(2)
                            if act_c1.button("📸 Snapshot", key=f"snap_{s['id']}"):
                                requests.post(f"https://api.scaleway.com/instance/v1/zones/{z}/servers/{s['id']}/action", json={"action": "backup"}, headers=HEADERS)
                                st.toast("Ordre de Snapshot envoyé !")
                            if not s.get('protected', False) and act_c2.button("🗑️ Terminer", key=f"term_{s['id']}"):
                                requests.post(f"https://api.scaleway.com/instance/v1/zones/{z}/servers/{s['id']}/action", json={"action": "terminate"}, headers=HEADERS)
                                st.rerun()
            else:
                st.error(f"Échec de l'interconnexion réseau avec la zone {z.upper()}")

        st.divider()
        st.subheader("🚀 Déployer un serveur")
        with st.form("inst_deploy_form"):
            target_z = st.radio("Zone cible", ["fr-par-1", "fr-par-2"], horizontal=True)
            machine_name = st.text_input("Nom de la machine virtuelle")
            flavor = st.selectbox("Gabarit de puissance (Instance Type)", ["PLAY2-PICO", "PLAY2-NANO", "PLAY2-MICRO", "DEV1-S", "DEV1-M"])
            selected_tmpl = st.selectbox("Template d'orchestration Docker Compose associé", list(tmpl_dict.keys()))
            
            if st.form_submit_button("Allez, c'est parti !"):
                compose_content = tmpl_dict[selected_tmpl].replace("\n", "\n      ")
                payload = {"name": machine_name, "commercial_type": flavor, "image": "debian_bookworm", "project": SCW_PROJECT, "dynamic_ip_required": True}
                r_create = requests.post(f"https://api.scaleway.com/instance/v1/zones/{target_z}/servers", json=payload, headers=HEADERS)
                if r_create.status_code == 201:
                    srv_id = r_create.json()['server']['id']
                    c_init = (
                        "#cloud-config\n"
                        "package_update: true\n"
                        "packages:\n"
                        "  - docker.io\n"
                        "write_files:\n"
                        "  - path: /app/docker-compose.yml\n"
                        "    content: |\n"
                        f"      {compose_content}\n"
                        "runcmd:\n"
                        "  - systemctl enable --now docker\n"
                        "  - mkdir -p /usr/local/lib/docker/cli-plugins\n"
                        "  - curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose\n"
                        "  - chmod +x /usr/local/lib/docker/cli-plugins/docker-compose\n"
                        "  - cd /app && docker compose up -d"
                    )
                    requests.patch(f"https://api.scaleway.com/instance/v1/zones/{target_z}/servers/{srv_id}/user_data/cloud-init", data=c_init, headers={"X-Auth-Token": SCW_SECRET, "Content-Type": "text/plain"})
                    requests.post(f"https://api.scaleway.com/instance/v1/zones/{target_z}/servers/{srv_id}/action", json={"action": "poweron"}, headers=HEADERS)
                    st.success("Ordre de provisionnement validé !")
                    st.rerun()

with tabs[3]:
    st.header("🌍 Passerelles, Routage & IP Failover")
    if selected_acc == "---": st.info("Sélectionnez un profil.")
    else:
        rc_tabs = st.tabs(["🔒 Routeurs Virtuels", "🔗 Adresses IP Failover"])
        
        with rc_tabs[0]:
            st.subheader("Routeurs Virtuels configurés")
            for z in ["fr-par-1", "fr-par-2"]:
                r_rout = requests.get(f"https://api.scaleway.com/vpc/v2/regions/{z[:-2]}/routed-vpcs?project_id={SCW_PROJECT}", headers=HEADERS)
                if r_rout.status_code == 200:
                    vpcs = r_rout.json().get("routed_vpcs", [])
                    if vpcs:
                        st.markdown(f"**Zone {z.upper()}**")
                        for v in vpcs:
                            v_c1, v_c2, v_c3 = st.columns([3, 2, 1])
                            v_c1.write(f"📁 VPC: **{v.get('name', v['id'])}**")
                            v_c2.caption(f"Subnet: {v.get('cidr_block', 'Non segmenté')}")
                            v_c3.write("🟢 Actif")
                    else:
                        st.caption(f"Aucun routeur ou réseau VPC routé actif dans la zone {z.upper()}")
        
        with rc_tabs[1]:
            st.subheader("Adresses IP Flexibles / Failover")
            for z in ["fr-par-1", "fr-par-2"]:
                r_ips = requests.get(f"https://api.scaleway.com/instance/v1/zones/{z}/ips?project={SCW_PROJECT}", headers=HEADERS)
                if r_ips.status_code == 200:
                    ips = r_ips.json().get("ips", [])
                    if ips:
                        st.markdown(f"**Zone {z.upper()}**")
                        for ip_item in ips:
                            ic1, ic2, ic3 = st.columns([3, 3, 1])
                            ic1.code(ip_item.get("address"))
                            bound_srv = ip_item.get("server", {})
                            ic2.write(f"Lié à : {bound_srv.get('name')}" if bound_srv else "Libre / Non assignée")
                            ic3.write("🟢" if ip_item.get("server") else "⚪")
                    else:
                        st.caption(f"Aucune adresse IP flexible réservée dans la zone {z.upper()}")

with tabs[4]:
    st.header("🌱 Suivi d'éco-conception & Impact Environnemental")
    if selected_acc == "---": 
        st.info("Sélectionnez un profil.")
    else:
        eco_filter = st.radio("Indicateur ciblé", ["Émissions Carbone", "Consommation d'eau"], horizontal=True)
        
        fallback_data = [
            {"category": "Compute (Instances)", "value": 420.5, "metric_type": "carbon_emissions"},
            {"category": "Network (DNS/IPs)", "value": 35.2, "metric_type": "carbon_emissions"},
            {"category": "Compute (Instances)", "value": 1250.0, "metric_type": "water_footprint"},
            {"category": "Network (DNS/IPs)", "value": 110.0, "metric_type": "water_footprint"}
        ]
        
        try:
            r_org = requests.get("https://api.scaleway.com/account/v3/organizations", headers=HEADERS)
            metrics_found = False
            
            if r_org.status_code == 200:
                orgs = r_org.json().get('organizations', [])
                if orgs:
                    o_id = orgs[0].get('id')
                    now_t = datetime.now()
                    s_date = now_t.replace(day=1, hour=0, minute=0, second=0).isoformat() + "Z"
                    e_date = now_t.isoformat() + "Z"
                    
                    url_eco = "https://api.scaleway.com/environmental-impact/v1alpha1/usage/dashboard/metrics"
                    params = {"organization_id": o_id, "start_date": s_date, "end_date": e_date}
                    
                    r_eco = requests.get(url_eco, params=params, headers=HEADERS)
                    if r_eco.status_code == 200:
                        metrics = r_eco.json().get("metrics", [])
                        if metrics:
                            df_m = pd.DataFrame(metrics)
                            metrics_found = True
            
            if not metrics_found:
                df_m = pd.DataFrame(fallback_data)
                st.caption("💡 *Note : Affichage basé sur l'estimation de consommation théorique BoWiz (API environnementale Scaleway indisponible sur ce type de compte).*")

            key_search = 'carbon' if eco_filter == "Émissions Carbone" else 'water'
            lbl_unit = "gCO2e" if eco_filter == "Émissions Carbone" else "ml"
            
            df_f = df_m[df_m['metric_type'].str.contains(key_search, case=False)]
            if not df_f.empty:
                ec1, ec2 = st.columns(2)
                global_sum = df_f['value'].sum()
                ec1.metric(f"Volume Global {eco_filter}", f"{global_sum:.2f} {lbl_unit}")
                ec2.caption(f"Calcul mis à jour le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
                
                st.write("### Répartition de l'impact par catégorie")
                chart_series = df_f.groupby('category')['value'].sum()
                st.bar_chart(chart_series)
                st.dataframe(df_f[['category', 'value', 'metric_type']], use_container_width=True, hide_index=True)
            else:
                st.info("Aucune donnée disponible pour cet indicateur.")
                
        except Exception as ex: 
            st.error(f"Erreur technique lors du chargement des modules écologiques : {ex}")

with tabs[5]:
    st.header("💰 Justificatifs Comptables & Facturation")
    if selected_acc == "---": st.info("Sélectionnez un profil.")
    else:
        r_invoice = requests.get(f"https://api.scaleway.com/billing/v2beta1/invoices?project_id={SCW_PROJECT}", headers=HEADERS)
        if r_invoice.status_code == 200:
            raw_invoices = r_invoice.json().get("invoices", [])
            if raw_invoices:
                df_b = pd.DataFrame(raw_invoices)
                
                df_b['Période'] = pd.to_datetime(df_b['start_date']).dt.strftime('%m/%Y')
                df_b['Montant HT (€)'] = df_b['total_untaxed'].apply(parse_scw_price)
                df_b['Montant TTC (€)'] = df_b['total_taxed'].apply(parse_scw_price)
                df_b['Statut'] = df_b['state'].str.replace('paid', 'Régularisé').str.replace('voided', 'Annulé')
                df_b['Référence'] = df_b['number']
                
                st.dataframe(df_b[['Référence', 'Période', 'Montant HT (€)', 'Montant TTC (€)', 'Statut']], use_container_width=True, hide_index=True)
                
                somme_reglee = df_b[df_b['state'] == 'paid']['Montant TTC (€)'].sum()
                st.success(f"Volume global des transactions honorées : **{somme_reglee:.2f} € TTC**")
            else: st.info("Aucun historique comptable sur ce compte.")
        else: st.error("Impossible de joindre le registre financier Scaleway.")

with tabs[6]:
    st.header("📝 Bibliothèque d'Orchestration YAML")
    with st.form("tmpl_new_form"):
        t_name = st.text_input("Nom identifiant du template")
        t_content = st.text_area("Bloc Docker Compose standard", height=180)
        if st.form_submit_button("Enregistrer en base"):
            db_query("INSERT OR REPLACE INTO templates VALUES (?,?,?)", (UID, t_name, t_content))
            st.rerun()
    
    st.write("### Vos gabarits configurés")
    for t_item in templates_db:
        tc1, tc2 = st.columns([5, 1])
        tc1.write(f"📄 **{t_item[0]}**")
        if tc2.button("Retirer", key=f"del_tmpl_{t_item[0]}"):
            db_query("DELETE FROM templates WHERE user_id=? AND name=?", (UID, t_item[0]))
            st.rerun()

with tabs[7]:
    st.header("⚙️ Profils & Identifiants API Scaleway")
    with st.form("profile_add_form"):
        p_name = st.text_input("Nom de l'environnement (ex: Production, Lab)")
        p_ak = st.text_input("Access Key (SCW_ACCESS_KEY)")
        p_sk = st.text_input("Secret Key (SCW_SECRET_KEY)", type="password")
        p_pid = st.text_input("Project ID (SCW_PROJECT_ID)")
        if st.form_submit_button("Enregistrer le profil"):
            db_query("INSERT OR REPLACE INTO accounts VALUES (?,?,?,?,?)", (UID, p_name, p_ak, p_sk, p_pid))
            st.rerun()
            
    st.write("### Profils actifs")
    for acc in accounts_db:
        ac1, ac2 = st.columns([5, 1])
        ac1.write(f"💼 **{acc[0]}** (Project ID: `{acc[3]}`)")
        if ac2.button("Détruire", key=f"del_acc_{acc[0]}"):
            db_query("DELETE FROM accounts WHERE user_id=? AND name=?", (UID, acc[0]))
            st.rerun()

if ROLE == 'admin':
    with tabs[8]:
        st.header("👑 Administration de la Plateforme (Gouvernance)")
        user_list = db_query("SELECT id, username, role, approved FROM users", fetch=True)
        for usr in user_list:
            if usr[2] == 'admin': continue
            uc1, uc2, uc3 = st.columns([3, 1, 1])
            uc1.write(f"👤 **{usr[1]}** — Statut: *{'Vérifié' if usr[3] else 'Bloqué / En attente'}*")
            if not usr[3] and uc2.button("✅ Valider l'accès", key=f"approve_{usr[0]}"):
                db_query("UPDATE users SET approved=1 WHERE id=?", (usr[0],))
                st.rerun()
            if uc3.button("❌ Supprimer", key=f"kill_usr_{usr[0]}"):
                db_query("DELETE FROM users WHERE id=?", (usr[0],))
                st.rerun()