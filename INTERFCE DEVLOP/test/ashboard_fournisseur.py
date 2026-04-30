import customtkinter as ctk
from PIL import Image
import sqlite3
from tkinter import messagebox, filedialog
import os
import sys

# =========================================================
# MEDSAFE — Chemins ressources
# =========================================================
def get_resource_path(filename):
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)

DB_PATH   = get_resource_path('medsafe_cabinet.db')
LOGO_PATH = get_resource_path('mokkt.jpg')

# =========================================================
# THÈME GLOBAL MEDSAFE — même Design System que pharmacien
# =========================================================
COULEURS = {
    "fond_principal": "#F0F4F3",
    "fond_sidebar":   "#0D2B28",
    "fond_carte":     "#FFFFFF",
    "vert_primaire":  "#1A6B55",
    "vert_clair":     "#2C9970",
    "vert_accent":    "#3EBF8A",
    "teal_doux":      "#A8D5C8",
    "texte_principal":"#0D2B28",
    "texte_clair":    "#FFFFFF",
    "texte_gris":     "#6B7F7D",
    "danger":         "#C0392B",
    "warning":        "#E67E22",
    "bordure":        "#D4E8E2",
    "fond_input":     "#EEF5F3",
    "sidebar_active": "#1A6B55",
    "sidebar_hover":  "#1A4A40",
    "fond_entete":    "#0D2B28",
    # Couleur accentuée pour fournisseur
    "bleu_fournisseur": "#1A3A6B",
    "bleu_clair":       "#2C5F9E",
}

FONT_TITRE  = ("Segoe UI", 26, "bold")
FONT_SOUS   = ("Segoe UI", 14, "bold")
FONT_NORMAL = ("Segoe UI", 13)
FONT_PETIT  = ("Segoe UI", 11)
FONT_BTN    = ("Segoe UI", 13, "bold")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# =========================================================
# COMPOSANTS PARTAGÉS
# =========================================================
def creer_carte(parent, **kwargs):
    outer = ctk.CTkFrame(parent, fg_color=COULEURS["bordure"], corner_radius=14)
    inner = ctk.CTkFrame(outer, fg_color=COULEURS["fond_carte"], corner_radius=12, **kwargs)
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    return outer, inner

def creer_badge(parent, texte, couleur_fond, couleur_texte, taille=11):
    return ctk.CTkLabel(parent, text=texte, fg_color=couleur_fond, text_color=couleur_texte,
                        font=("Segoe UI", taille, "bold"), corner_radius=8, padx=10, pady=3)

def creer_separateur(parent, couleur=None):
    c = couleur or COULEURS["bordure"]
    sep = ctk.CTkFrame(parent, height=1, fg_color=c)
    sep.pack(fill="x", padx=20, pady=8)
    return sep

# =========================================================
# BASE DE DONNÉES — Initialisation tables fournisseur
# =========================================================
def init_db_fournisseur():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    # Table fournisseurs
    cur.execute('''CREATE TABLE IF NOT EXISTS fournisseurs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        nom           TEXT NOT NULL,
        entreprise    TEXT,
        email         TEXT UNIQUE NOT NULL,
        telephone     TEXT,
        mot_de_passe  TEXT NOT NULL
    )''')
    # Table catalogue (médicaments proposés par le fournisseur)
    cur.execute('''CREATE TABLE IF NOT EXISTS catalogue_fournisseur (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        fournisseur_id  INTEGER NOT NULL,
        nom_produit     TEXT NOT NULL,
        reference       TEXT,
        prix_unitaire   REAL DEFAULT 0.0,
        stock_dispo     INTEGER DEFAULT 0,
        unite           TEXT DEFAULT "boîte",
        FOREIGN KEY(fournisseur_id) REFERENCES fournisseurs(id)
    )''')
    # Table commandes reçues des pharmacies
    cur.execute('''CREATE TABLE IF NOT EXISTS commandes (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        fournisseur_id  INTEGER NOT NULL,
        pharmacie_nom   TEXT,
        produit         TEXT,
        quantite        INTEGER,
        statut          TEXT DEFAULT "En attente",
        date_commande   TEXT DEFAULT (date('now')),
        FOREIGN KEY(fournisseur_id) REFERENCES fournisseurs(id)
    )''')
    # Table livraisons
    cur.execute('''CREATE TABLE IF NOT EXISTS livraisons (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        commande_id     INTEGER NOT NULL,
        fournisseur_id  INTEGER NOT NULL,
        date_livraison  TEXT,
        transporteur    TEXT,
        statut          TEXT DEFAULT "Préparée",
        FOREIGN KEY(commande_id) REFERENCES commandes(id)
    )''')
    conn.commit()
    conn.close()


# =========================================================
# 1. FENÊTRE DE CONNEXION FOURNISSEUR
# =========================================================
class LoginFournisseur(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MEDSAFE — Espace Fournisseur")
        self.geometry("480x740")
        self.resizable(False, False)
        self.configure(fg_color=COULEURS["fond_principal"])
        self.connexion_reussie = False
        self.fournisseur_data  = None
        init_db_fournisseur()
        self.afficher_login()

    # ── Utilitaires ────────────────────────────────────────
    def nettoyer(self):
        for w in self.winfo_children():
            w.destroy()

    def ajouter_logo(self, taille=(110, 110)):
        try:
            img = ctk.CTkImage(light_image=Image.open(LOGO_PATH),
                               dark_image=Image.open(LOGO_PATH), size=taille)
            ctk.CTkLabel(self, image=img, text="").pack(pady=(38, 6))
        except Exception:
            logo_frame = ctk.CTkFrame(self, fg_color=COULEURS["bleu_fournisseur"],
                                      corner_radius=55, width=taille[0], height=taille[1])
            logo_frame.pack(pady=(38, 6))
            logo_frame.pack_propagate(False)
            ctk.CTkLabel(logo_frame, text="🏭", font=("Segoe UI", 38),
                         text_color="white").place(relx=0.5, rely=0.5, anchor="center")

    # ── Vue connexion ──────────────────────────────────────
    def afficher_login(self):
        self.nettoyer()
        self.ajouter_logo()
        ctk.CTkLabel(self, text="MEDSAFE", font=("Segoe UI", 28, "bold"),
                     text_color=COULEURS["fond_entete"]).pack()
        ctk.CTkLabel(self, text="Portail Fournisseur", font=("Segoe UI", 13),
                     text_color=COULEURS["texte_gris"]).pack(pady=(2, 24))

        outer, card = creer_carte(self)
        outer.pack(padx=40, fill="x")
        ctk.CTkLabel(card, text="Connexion", font=("Segoe UI", 15, "bold"),
                     text_color=COULEURS["texte_principal"]).pack(anchor="w", padx=24, pady=(20, 12))

        self.entry_email = ctk.CTkEntry(
            card, placeholder_text="Email professionnel", height=44, corner_radius=10,
            fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"], border_width=1,
            text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.entry_email.pack(fill="x", padx=24, pady=6)

        self.entry_mdp = ctk.CTkEntry(
            card, placeholder_text="Mot de passe", show="●", height=44, corner_radius=10,
            fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"], border_width=1,
            text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.entry_mdp.pack(fill="x", padx=24, pady=6)

        ctk.CTkButton(
            card, text="Se connecter", height=46,
            fg_color=COULEURS["bleu_fournisseur"], hover_color=COULEURS["bleu_clair"],
            font=FONT_BTN, corner_radius=10, command=self.verifier_login
        ).pack(fill="x", padx=24, pady=(14, 20))

        lien = ctk.CTkFrame(self, fg_color="transparent")
        lien.pack(pady=14)
        ctk.CTkLabel(lien, text="Nouveau fournisseur ?", font=FONT_PETIT,
                     text_color=COULEURS["texte_gris"]).pack(side="left")
        ctk.CTkButton(lien, text=" S'inscrire", fg_color="transparent",
                      text_color=COULEURS["bleu_fournisseur"], hover_color=COULEURS["fond_principal"],
                      font=("Segoe UI", 11, "bold"), command=self.afficher_inscription).pack(side="left")

    # ── Vue inscription ────────────────────────────────────
    def afficher_inscription(self):
        self.nettoyer()
        self.ajouter_logo((90, 90))
        ctk.CTkLabel(self, text="Inscrire un fournisseur", font=("Segoe UI", 18, "bold"),
                     text_color=COULEURS["fond_entete"]).pack(pady=(4, 16))

        outer, card = creer_carte(self)
        outer.pack(padx=40, fill="x")

        champs = [
            ("reg_nom",        "Nom du responsable (ex : M. Karim Benali)", False),
            ("reg_entreprise", "Nom de l'entreprise / laboratoire",          False),
            ("reg_tel",        "Téléphone professionnel",                    False),
            ("reg_email",      "Adresse email",                              False),
            ("reg_mdp",        "Mot de passe",                               True),
        ]
        for attr, ph, is_pass in champs:
            e = ctk.CTkEntry(card, placeholder_text=ph, height=42, corner_radius=10,
                             fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"],
                             border_width=1, text_color=COULEURS["texte_principal"],
                             font=FONT_NORMAL, show="●" if is_pass else "")
            e.pack(fill="x", padx=24, pady=5)
            setattr(self, attr, e)

        ctk.CTkButton(card, text="Créer le compte", height=44,
                      fg_color=COULEURS["bleu_fournisseur"], hover_color=COULEURS["bleu_clair"],
                      font=FONT_BTN, corner_radius=10,
                      command=self.enregistrer_fournisseur).pack(fill="x", padx=24, pady=(12, 20))

        ctk.CTkButton(self, text="← Retour à la connexion", fg_color="transparent",
                      text_color=COULEURS["texte_gris"], hover_color=COULEURS["fond_principal"],
                      font=FONT_PETIT, command=self.afficher_login).pack(pady=8)

    # ── Logique connexion ──────────────────────────────────
    def verifier_login(self):
        email = self.entry_email.get().strip()
        mdp   = self.entry_mdp.get().strip()
        try:
            conn = sqlite3.connect(DB_PATH)
            cur  = conn.cursor()
            cur.execute("SELECT * FROM fournisseurs WHERE email = ? AND mot_de_passe = ?", (email, mdp))
            f = cur.fetchone()
            conn.close()
            if f:
                self.fournisseur_data  = f
                self.connexion_reussie = True
                self.quit()
                self.destroy()
            else:
                messagebox.showerror("Erreur", "Identifiants incorrects.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Problème de connexion : {e}")

    def enregistrer_fournisseur(self):
        nom        = self.reg_nom.get().strip()
        entreprise = self.reg_entreprise.get().strip()
        tel        = self.reg_tel.get().strip()
        email      = self.reg_email.get().strip()
        mdp        = self.reg_mdp.get().strip()
        if not nom or not email or not mdp:
            messagebox.showwarning("Champs manquants", "Remplissez au moins le nom, l'email et le mot de passe.")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cur  = conn.cursor()
            cur.execute(
                "INSERT INTO fournisseurs (nom, entreprise, email, telephone, mot_de_passe) VALUES (?,?,?,?,?)",
                (nom, entreprise, email, tel, mdp)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Inscrit ✓", "Compte fournisseur créé avec succès !")
            self.afficher_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Email existant", "Cet email est déjà utilisé.")
        except Exception as e:
            messagebox.showerror("Erreur BDD", str(e))


# =========================================================
# 2. TABLEAU DE BORD FOURNISSEUR
# =========================================================
class DashboardFournisseur(ctk.CTk):
    def __init__(self, fournisseur_connecte):
        super().__init__()
        self.four_info = fournisseur_connecte   # tuple: (id, nom, entreprise, email, telephone, mdp)
        self.four_id   = fournisseur_connecte[0]
        self.title("MEDSAFE — Espace Fournisseur")
        self.geometry("1280x840")
        self.minsize(1050, 700)
        self.configure(fg_color=COULEURS["fond_principal"])
        self._construire_interface()
        self.afficher_profil()

    # ── Interface principale ───────────────────────────────
    def _construire_interface(self):
        # SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0,
                                    fg_color=COULEURS["fond_sidebar"])
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        try:
            img = ctk.CTkImage(light_image=Image.open(LOGO_PATH),
                               dark_image=Image.open(LOGO_PATH), size=(120, 120))
            ctk.CTkLabel(self.sidebar, image=img, text="").pack(pady=(30, 4))
        except Exception:
            logo_f = ctk.CTkFrame(self.sidebar, fg_color=COULEURS["bleu_fournisseur"],
                                  corner_radius=40, width=80, height=80)
            logo_f.pack(pady=(30, 4))
            logo_f.pack_propagate(False)
            ctk.CTkLabel(logo_f, text="🏭", font=("Segoe UI", 32),
                         text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.sidebar, text="MEDSAFE", font=("Segoe UI", 16, "bold"),
                     text_color=COULEURS["teal_doux"]).pack()
        ctk.CTkLabel(self.sidebar, text="Espace Fournisseur", font=("Segoe UI", 10),
                     text_color="#7AAFA4").pack(pady=(0, 24))
        creer_separateur(self.sidebar, "#1A3D38")

        self.btns_nav = {}
        nav_items = [
            ("👤", "Mon Profil",       self.afficher_profil),
            ("📦", "Mon Catalogue",    self.afficher_catalogue),
            ("🛒", "Commandes",        self.afficher_commandes),
            ("🚚", "Livraisons",       self.afficher_livraisons),
            ("📊", "Statistiques",     self.afficher_statistiques),
        ]
        for icone, label, cmd in nav_items:
            btn = self._creer_btn_nav(icone, label, cmd)
            self.btns_nav[label] = btn

        creer_separateur(self.sidebar, "#1A3D38")
        nom = self.four_info[1] if self.four_info else "Fournisseur"
        ent = self.four_info[2] if self.four_info else ""
        ctk.CTkLabel(self.sidebar, text=nom, font=("Segoe UI", 12, "bold"),
                     text_color=COULEURS["texte_clair"]).pack(pady=(10, 0))
        ctk.CTkLabel(self.sidebar, text=ent, font=("Segoe UI", 10),
                     text_color="#7AAFA4").pack(pady=(0, 8))
        ctk.CTkButton(
            self.sidebar, text="Déconnexion", height=34, fg_color="#1A3D38",
            hover_color=COULEURS["danger"], text_color="#7AAFA4", font=("Segoe UI", 11),
            command=self.destroy, corner_radius=8
        ).pack(padx=20, pady=(0, 20), fill="x")

        # CONTENU
        self.zone_contenu = ctk.CTkScrollableFrame(
            self, fg_color=COULEURS["fond_principal"], corner_radius=0)
        self.zone_contenu.pack(side="right", fill="both", expand=True)

    def _creer_btn_nav(self, icone, label, cmd):
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", corner_radius=10)
        frame.pack(fill="x", padx=12, pady=2)
        btn = ctk.CTkButton(frame, text=f"  {icone}  {label}", anchor="w", height=44,
                            corner_radius=10, fg_color="transparent",
                            hover_color=COULEURS["sidebar_hover"], font=("Segoe UI", 13),
                            text_color=COULEURS["texte_clair"],
                            command=lambda: self._nav(label, cmd))
        btn.pack(fill="x")
        return btn

    def _nav(self, label, cmd):
        for lbl, btn in self.btns_nav.items():
            btn.configure(fg_color=COULEURS["sidebar_active"] if lbl == label else "transparent")
        cmd()

    def nettoyer_contenu(self):
        for w in self.zone_contenu.winfo_children():
            w.destroy()

    def _entete_section(self, titre, sous_titre=""):
        f = ctk.CTkFrame(self.zone_contenu, fg_color="transparent")
        f.pack(fill="x", padx=30, pady=(28, 0))
        ctk.CTkLabel(f, text=titre, font=FONT_TITRE,
                     text_color=COULEURS["texte_principal"]).pack(anchor="w")
        if sous_titre:
            ctk.CTkLabel(f, text=sous_titre, font=FONT_PETIT,
                         text_color=COULEURS["texte_gris"]).pack(anchor="w", pady=(2, 0))

    # =========================================================
    # ─── 0. PROFIL ────────────────────────────────────────────
    # =========================================================
    def afficher_profil(self):
        self._nav("Mon Profil", lambda: None)
        self.nettoyer_contenu()
        self._entete_section("Mon Profil", "Informations du fournisseur")

        outer, card = creer_carte(self.zone_contenu)
        outer.pack(fill="x", padx=30, pady=20)

        header = ctk.CTkFrame(card, fg_color=COULEURS["bleu_fournisseur"], corner_radius=0, height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        nom = self.four_info[1] if self.four_info else "Fournisseur"
        ent = self.four_info[2] if self.four_info else "—"
        eml = self.four_info[3] if self.four_info else "—"
        tel = self.four_info[4] if self.four_info else "—"

        ctk.CTkLabel(header, text=nom, font=("Segoe UI", 20, "bold"),
                     text_color="white").pack(anchor="w", padx=30, pady=(18, 0))
        ctk.CTkLabel(header, text=ent, font=("Segoe UI", 12),
                     text_color=COULEURS["teal_doux"]).pack(anchor="w", padx=30)

        info_f = ctk.CTkFrame(card, fg_color="transparent")
        info_f.pack(fill="x", padx=30, pady=20)

        for lbl, val in [("Entreprise", ent), ("Email", eml),
                         ("Téléphone", tel or "—"), ("Statut", "Actif ✓")]:
            row = ctk.CTkFrame(info_f, fg_color=COULEURS["fond_input"], corner_radius=8)
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=lbl, font=("Segoe UI", 11), text_color=COULEURS["texte_gris"],
                         width=130, anchor="w").pack(side="left", padx=16, pady=12)
            ctk.CTkLabel(row, text=val, font=("Segoe UI", 12, "bold"),
                         text_color=COULEURS["texte_principal"]).pack(side="left", padx=8)

        # Stats rapides
        stats = ctk.CTkFrame(self.zone_contenu, fg_color="transparent")
        stats.pack(fill="x", padx=30)

        def _compter(tbl, condition=""):
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                q = f"SELECT COUNT(*) FROM {tbl} WHERE fournisseur_id=?"
                if condition:
                    q += f" AND {condition}"
                c.execute(q, (self.four_id,))
                v = c.fetchone()[0]
                conn.close()
                return v
            except Exception:
                return "—"

        tuiles = [
            ("Produits au catalogue", _compter("catalogue_fournisseur"), "📦", COULEURS["bleu_fournisseur"]),
            ("Commandes en attente",  _compter("commandes", "statut='En attente'"), "🛒", COULEURS["warning"]),
            ("Livraisons en cours",   _compter("livraisons", "statut='En cours'"), "🚚", COULEURS["vert_accent"]),
        ]
        for label, val, icone, couleur in tuiles:
            outer2, c2 = creer_carte(stats)
            outer2.pack(side="left", expand=True, fill="x", padx=8, pady=8)
            ctk.CTkLabel(c2, text=icone, font=("Segoe UI", 26)).pack(pady=(20, 4))
            ctk.CTkLabel(c2, text=str(val), font=("Segoe UI", 28, "bold"),
                         text_color=couleur).pack()
            ctk.CTkLabel(c2, text=label, font=FONT_PETIT,
                         text_color=COULEURS["texte_gris"]).pack(pady=(2, 18))

    # =========================================================
    # ─── 1. CATALOGUE ─────────────────────────────────────────
    # =========================================================
    def afficher_catalogue(self):
        self._nav("Mon Catalogue", lambda: None)
        self.nettoyer_contenu()
        self._entete_section("Mon Catalogue", "Produits disponibles à la vente")

        # Formulaire ajout
        outer, form = creer_carte(self.zone_contenu)
        outer.pack(fill="x", padx=30, pady=(16, 8))

        ctk.CTkLabel(form, text="Ajouter un produit", font=("Segoe UI", 13, "bold"),
                     text_color=COULEURS["texte_principal"]).pack(anchor="w", padx=24, pady=(16, 8))

        row1 = ctk.CTkFrame(form, fg_color="transparent")
        row1.pack(fill="x", padx=24, pady=(0, 8))

        self.e_cat_nom = ctk.CTkEntry(row1, placeholder_text="Nom du produit", height=40,
                                      corner_radius=10, fg_color=COULEURS["fond_input"],
                                      border_color=COULEURS["bordure"], border_width=1,
                                      text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.e_cat_nom.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.e_cat_ref = ctk.CTkEntry(row1, placeholder_text="Référence", height=40, width=130,
                                      corner_radius=10, fg_color=COULEURS["fond_input"],
                                      border_color=COULEURS["bordure"], border_width=1,
                                      text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.e_cat_ref.pack(side="left", padx=(0, 8))

        row2 = ctk.CTkFrame(form, fg_color="transparent")
        row2.pack(fill="x", padx=24, pady=(0, 16))

        self.e_cat_prix = ctk.CTkEntry(row2, placeholder_text="Prix unitaire (DA)", height=40, width=160,
                                       corner_radius=10, fg_color=COULEURS["fond_input"],
                                       border_color=COULEURS["bordure"], border_width=1,
                                       text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.e_cat_prix.pack(side="left", padx=(0, 8))

        self.e_cat_stock = ctk.CTkEntry(row2, placeholder_text="Qté disponible", height=40, width=140,
                                        corner_radius=10, fg_color=COULEURS["fond_input"],
                                        border_color=COULEURS["bordure"], border_width=1,
                                        text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.e_cat_stock.pack(side="left", padx=(0, 8))

        self.e_cat_unite = ctk.CTkEntry(row2, placeholder_text="Unité (boîte, flacon…)", height=40, width=160,
                                        corner_radius=10, fg_color=COULEURS["fond_input"],
                                        border_color=COULEURS["bordure"], border_width=1,
                                        text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.e_cat_unite.pack(side="left", padx=(0, 8))

        ctk.CTkButton(row2, text="Ajouter", height=40, width=110, corner_radius=10,
                      fg_color=COULEURS["bleu_fournisseur"], hover_color=COULEURS["bleu_clair"],
                      font=FONT_BTN, command=self.ajouter_produit).pack(side="right")

        # Liste catalogue
        self.liste_catalogue = ctk.CTkScrollableFrame(
            self.zone_contenu, fg_color=COULEURS["fond_carte"],
            corner_radius=12, border_color=COULEURS["bordure"], border_width=1)
        self.liste_catalogue.pack(fill="both", expand=True, padx=30, pady=(0, 24))
        self.charger_catalogue()

    def ajouter_produit(self):
        nom   = self.e_cat_nom.get().strip()
        ref   = self.e_cat_ref.get().strip()
        prix  = self.e_cat_prix.get().strip()
        stock = self.e_cat_stock.get().strip()
        unite = self.e_cat_unite.get().strip() or "boîte"

        if not nom or not stock:
            messagebox.showwarning("Incomplet", "Le nom et la quantité sont obligatoires.")
            return
        if not stock.isdigit():
            messagebox.showerror("Erreur", "La quantité doit être un entier.")
            return
        try:
            prix_f = float(prix.replace(",", ".")) if prix else 0.0
        except ValueError:
            messagebox.showerror("Erreur", "Le prix doit être un nombre.")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.cursor().execute(
                "INSERT INTO catalogue_fournisseur (fournisseur_id, nom_produit, reference, prix_unitaire, stock_dispo, unite) VALUES (?,?,?,?,?,?)",
                (self.four_id, nom, ref, prix_f, int(stock), unite)
            )
            conn.commit()
            conn.close()
            for e in (self.e_cat_nom, self.e_cat_ref, self.e_cat_prix, self.e_cat_stock, self.e_cat_unite):
                e.delete(0, "end")
            self.charger_catalogue()
        except Exception as e:
            messagebox.showerror("Erreur BDD", str(e))

    def charger_catalogue(self):
        for w in self.liste_catalogue.winfo_children():
            w.destroy()
        try:
            conn = sqlite3.connect(DB_PATH)
            cur  = conn.cursor()
            cur.execute(
                "SELECT id, nom_produit, reference, prix_unitaire, stock_dispo, unite FROM catalogue_fournisseur WHERE fournisseur_id=? ORDER BY nom_produit ASC",
                (self.four_id,)
            )
            produits = cur.fetchall()
            conn.close()

            if not produits:
                ctk.CTkLabel(self.liste_catalogue, text="Catalogue vide. Ajoutez vos premiers produits.",
                             font=FONT_NORMAL, text_color=COULEURS["texte_gris"]).pack(pady=30)
                return

            # En-tête colonnes
            hdr = ctk.CTkFrame(self.liste_catalogue, fg_color=COULEURS["fond_entete"], corner_radius=8)
            hdr.pack(fill="x", padx=10, pady=(8, 4))
            for col, w in [("Produit", 3), ("Réf.", 1), ("Prix unit.", 1), ("Stock", 1), ("Unité", 1), ("Actions", 1)]:
                ctk.CTkLabel(hdr, text=col, font=("Segoe UI", 11, "bold"),
                             text_color=COULEURS["texte_clair"]).pack(side="left", expand=(w == 3), padx=12, pady=8)

            for prod_id, nom, ref, prix, stock, unite in produits:
                row = ctk.CTkFrame(self.liste_catalogue, fg_color=COULEURS["fond_input"], corner_radius=8)
                row.pack(fill="x", pady=4, padx=10)

                ctk.CTkLabel(row, text=nom, font=("Segoe UI", 12, "bold"),
                             text_color=COULEURS["texte_principal"],
                             anchor="w").pack(side="left", expand=True, padx=12, pady=10)
                ctk.CTkLabel(row, text=ref or "—", font=FONT_PETIT,
                             text_color=COULEURS["texte_gris"], width=90).pack(side="left", padx=8)
                ctk.CTkLabel(row, text=f"{prix:.2f} DA", font=FONT_PETIT,
                             text_color=COULEURS["bleu_fournisseur"], width=90).pack(side="left", padx=8)
                badge_col = "#FFF5F5" if stock < 10 else COULEURS["fond_input"]
                badge_txt_col = COULEURS["danger"] if stock < 10 else COULEURS["texte_principal"]
                ctk.CTkLabel(row, text=str(stock), font=("Segoe UI", 12, "bold"),
                             text_color=badge_txt_col, fg_color=badge_col,
                             corner_radius=6, width=60).pack(side="left", padx=8)
                ctk.CTkLabel(row, text=unite, font=FONT_PETIT,
                             text_color=COULEURS["texte_gris"], width=70).pack(side="left", padx=8)

                btns = ctk.CTkFrame(row, fg_color="transparent")
                btns.pack(side="right", padx=10)
                ctk.CTkButton(btns, text="Modifier", height=30, width=78, corner_radius=6,
                              fg_color=COULEURS["fond_input"], hover_color=COULEURS["bordure"],
                              text_color=COULEURS["bleu_fournisseur"], font=("Segoe UI", 11, "bold"),
                              command=lambda pid=prod_id, pnom=nom: self.modifier_produit(pid, pnom)
                              ).pack(side="left", padx=2)
                ctk.CTkButton(btns, text="Supprimer", height=30, width=88, corner_radius=6,
                              fg_color="#FFECEC", hover_color="#FFCDD2",
                              text_color=COULEURS["danger"], font=("Segoe UI", 11, "bold"),
                              command=lambda pid=prod_id, pnom=nom: self.supprimer_produit(pid, pnom)
                              ).pack(side="left", padx=2)
        except Exception as e:
            print(e)

    def modifier_produit(self, prod_id, nom):
        nv = ctk.CTkInputDialog(text=f"Nouveau stock disponible pour\n« {nom} » :", title="Modifier stock").get_input()
        if nv and nv.strip().isdigit():
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.cursor().execute("UPDATE catalogue_fournisseur SET stock_dispo=? WHERE id=?", (int(nv), prod_id))
                conn.commit()
                conn.close()
                self.charger_catalogue()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
        elif nv:
            messagebox.showerror("Erreur", "Entrez un nombre entier.")

    def supprimer_produit(self, prod_id, nom):
        if messagebox.askyesno("Confirmer", f"Supprimer « {nom} » du catalogue ?"):
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.cursor().execute("DELETE FROM catalogue_fournisseur WHERE id=?", (prod_id,))
                conn.commit()
                conn.close()
                self.charger_catalogue()
            except Exception as e:
                messagebox.showerror("Erreur BDD", str(e))

    # =========================================================
    # ─── 2. COMMANDES ─────────────────────────────────────────
    # =========================================================
    def afficher_commandes(self):
        self._nav("Commandes", lambda: None)
        self.nettoyer_contenu()
        self._entete_section("Commandes reçues", "Suivi des demandes des pharmacies")

        # Formulaire saisie manuelle d'une commande
        outer, form = creer_carte(self.zone_contenu)
        outer.pack(fill="x", padx=30, pady=(16, 8))

        ctk.CTkLabel(form, text="Enregistrer une commande", font=("Segoe UI", 13, "bold"),
                     text_color=COULEURS["texte_principal"]).pack(anchor="w", padx=24, pady=(16, 8))

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(0, 16))

        self.e_cmd_phar = ctk.CTkEntry(row, placeholder_text="Pharmacie (nom)", height=40,
                                       corner_radius=10, fg_color=COULEURS["fond_input"],
                                       border_color=COULEURS["bordure"], border_width=1,
                                       text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.e_cmd_phar.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.e_cmd_prod = ctk.CTkEntry(row, placeholder_text="Produit commandé", height=40,
                                       corner_radius=10, fg_color=COULEURS["fond_input"],
                                       border_color=COULEURS["bordure"], border_width=1,
                                       text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.e_cmd_prod.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.e_cmd_qte = ctk.CTkEntry(row, placeholder_text="Qté", height=40, width=80,
                                      corner_radius=10, fg_color=COULEURS["fond_input"],
                                      border_color=COULEURS["bordure"], border_width=1,
                                      text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.e_cmd_qte.pack(side="left", padx=(0, 8))

        ctk.CTkButton(row, text="Enregistrer", height=40, width=120, corner_radius=10,
                      fg_color=COULEURS["bleu_fournisseur"], hover_color=COULEURS["bleu_clair"],
                      font=FONT_BTN, command=self.ajouter_commande).pack(side="right")

        # Filtre statut
        filtre_f = ctk.CTkFrame(self.zone_contenu, fg_color="transparent")
        filtre_f.pack(fill="x", padx=30, pady=(4, 0))
        ctk.CTkLabel(filtre_f, text="Filtrer :", font=FONT_PETIT,
                     text_color=COULEURS["texte_gris"]).pack(side="left", padx=(0, 8))
        self.filtre_cmd = ctk.StringVar(value="Tous")
        for opt in ["Tous", "En attente", "Confirmée", "Expédiée", "Livrée", "Annulée"]:
            ctk.CTkButton(filtre_f, text=opt, height=32, corner_radius=8,
                          fg_color=COULEURS["fond_input"], hover_color=COULEURS["bordure"],
                          text_color=COULEURS["texte_principal"], font=("Segoe UI", 11),
                          command=lambda o=opt: self._filtrer_commandes(o)).pack(side="left", padx=3)

        # Liste
        self.liste_commandes = ctk.CTkScrollableFrame(
            self.zone_contenu, fg_color=COULEURS["fond_carte"],
            corner_radius=12, border_color=COULEURS["bordure"], border_width=1)
        self.liste_commandes.pack(fill="both", expand=True, padx=30, pady=(8, 24))
        self.charger_commandes()

    def ajouter_commande(self):
        phar = self.e_cmd_phar.get().strip()
        prod = self.e_cmd_prod.get().strip()
        qte  = self.e_cmd_qte.get().strip()
        if not phar or not prod or not qte:
            messagebox.showwarning("Incomplet", "Remplissez tous les champs.")
            return
        if not qte.isdigit():
            messagebox.showerror("Erreur", "La quantité doit être un entier.")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.cursor().execute(
                "INSERT INTO commandes (fournisseur_id, pharmacie_nom, produit, quantite) VALUES (?,?,?,?)",
                (self.four_id, phar, prod, int(qte))
            )
            conn.commit()
            conn.close()
            for e in (self.e_cmd_phar, self.e_cmd_prod, self.e_cmd_qte):
                e.delete(0, "end")
            self.charger_commandes()
        except Exception as e:
            messagebox.showerror("Erreur BDD", str(e))

    def _filtrer_commandes(self, statut):
        self.filtre_cmd.set(statut)
        self.charger_commandes(statut)

    def charger_commandes(self, filtre="Tous"):
        for w in self.liste_commandes.winfo_children():
            w.destroy()
        try:
            conn = sqlite3.connect(DB_PATH)
            cur  = conn.cursor()
            if filtre == "Tous":
                cur.execute(
                    "SELECT id, pharmacie_nom, produit, quantite, statut, date_commande FROM commandes WHERE fournisseur_id=? ORDER BY id DESC",
                    (self.four_id,)
                )
            else:
                cur.execute(
                    "SELECT id, pharmacie_nom, produit, quantite, statut, date_commande FROM commandes WHERE fournisseur_id=? AND statut=? ORDER BY id DESC",
                    (self.four_id, filtre)
                )
            cmds = cur.fetchall()
            conn.close()

            if not cmds:
                ctk.CTkLabel(self.liste_commandes, text="Aucune commande.",
                             font=FONT_NORMAL, text_color=COULEURS["texte_gris"]).pack(pady=30)
                return

            STATUT_COLORS = {
                "En attente": ("#FFF3E0", COULEURS["warning"]),
                "Confirmée":  ("#E8F5E9", COULEURS["vert_accent"]),
                "Expédiée":   ("#E3F2FD", COULEURS["bleu_fournisseur"]),
                "Livrée":     (COULEURS["fond_input"], COULEURS["vert_primaire"]),
                "Annulée":    ("#FFECEC", COULEURS["danger"]),
            }
            STATUTS_SUIVANTS = {
                "En attente": "Confirmée",
                "Confirmée":  "Expédiée",
                "Expédiée":   "Livrée",
            }

            for cmd_id, phar, prod, qte, statut, date in cmds:
                bg, _ = STATUT_COLORS.get(statut, (COULEURS["fond_input"], COULEURS["texte_gris"]))
                row = ctk.CTkFrame(self.liste_commandes, fg_color=bg, corner_radius=10)
                row.pack(fill="x", pady=4, padx=10)

                left = ctk.CTkFrame(row, fg_color="transparent")
                left.pack(side="left", fill="both", expand=True, padx=16, pady=12)
                ctk.CTkLabel(left, text=f"#{cmd_id}  —  {phar}", font=("Segoe UI", 13, "bold"),
                             text_color=COULEURS["texte_principal"]).pack(anchor="w")
                ctk.CTkLabel(left, text=f"{prod}  ×{qte}   📅 {date}",
                             font=FONT_PETIT, text_color=COULEURS["texte_gris"]).pack(anchor="w", pady=(2, 0))

                right = ctk.CTkFrame(row, fg_color="transparent")
                right.pack(side="right", padx=12)

                _, sc = STATUT_COLORS.get(statut, ("#DDD", "#000"))
                creer_badge(right, f"  {statut}  ", bg, sc, taille=11).pack(pady=4)

                if statut in STATUTS_SUIVANTS:
                    suivant = STATUTS_SUIVANTS[statut]
                    ctk.CTkButton(right, text=f"→ {suivant}", height=28, width=110, corner_radius=6,
                                  fg_color=COULEURS["bleu_fournisseur"], hover_color=COULEURS["bleu_clair"],
                                  text_color="white", font=("Segoe UI", 10, "bold"),
                                  command=lambda cid=cmd_id, s=suivant: self.changer_statut_cmd(cid, s)
                                  ).pack(pady=2)
                if statut not in ("Livrée", "Annulée"):
                    ctk.CTkButton(right, text="Annuler", height=26, width=80, corner_radius=6,
                                  fg_color="#FFECEC", hover_color="#FFCDD2",
                                  text_color=COULEURS["danger"], font=("Segoe UI", 10),
                                  command=lambda cid=cmd_id: self.changer_statut_cmd(cid, "Annulée")
                                  ).pack(pady=2)
        except Exception as e:
            print(e)

    def changer_statut_cmd(self, cmd_id, nouveau_statut):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.cursor().execute("UPDATE commandes SET statut=? WHERE id=?", (nouveau_statut, cmd_id))
            conn.commit()
            conn.close()
            self.charger_commandes(self.filtre_cmd.get())
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # =========================================================
    # ─── 3. LIVRAISONS ────────────────────────────────────────
    # =========================================================
    def afficher_livraisons(self):
        self._nav("Livraisons", lambda: None)
        self.nettoyer_contenu()
        self._entete_section("Livraisons", "Suivi des expéditions")

        # Formulaire création livraison
        outer, form = creer_carte(self.zone_contenu)
        outer.pack(fill="x", padx=30, pady=(16, 8))

        ctk.CTkLabel(form, text="Créer une livraison", font=("Segoe UI", 13, "bold"),
                     text_color=COULEURS["texte_principal"]).pack(anchor="w", padx=24, pady=(16, 8))

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(0, 16))

        self.e_liv_cmd = ctk.CTkEntry(row, placeholder_text="ID Commande", height=40, width=140,
                                      corner_radius=10, fg_color=COULEURS["fond_input"],
                                      border_color=COULEURS["bordure"], border_width=1,
                                      text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.e_liv_cmd.pack(side="left", padx=(0, 8))

        self.e_liv_date = ctk.CTkEntry(row, placeholder_text="Date prévue (JJ/MM/AAAA)", height=40, width=200,
                                       corner_radius=10, fg_color=COULEURS["fond_input"],
                                       border_color=COULEURS["bordure"], border_width=1,
                                       text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.e_liv_date.pack(side="left", padx=(0, 8))

        self.e_liv_trans = ctk.CTkEntry(row, placeholder_text="Transporteur", height=40,
                                        corner_radius=10, fg_color=COULEURS["fond_input"],
                                        border_color=COULEURS["bordure"], border_width=1,
                                        text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.e_liv_trans.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(row, text="Créer", height=40, width=100, corner_radius=10,
                      fg_color=COULEURS["vert_primaire"], hover_color=COULEURS["vert_clair"],
                      font=FONT_BTN, command=self.ajouter_livraison).pack(side="right")

        # Liste
        self.liste_livraisons = ctk.CTkScrollableFrame(
            self.zone_contenu, fg_color=COULEURS["fond_carte"],
            corner_radius=12, border_color=COULEURS["bordure"], border_width=1)
        self.liste_livraisons.pack(fill="both", expand=True, padx=30, pady=(0, 24))
        self.charger_livraisons()

    def ajouter_livraison(self):
        cmd_id = self.e_liv_cmd.get().strip()
        date   = self.e_liv_date.get().strip()
        trans  = self.e_liv_trans.get().strip()
        if not cmd_id or not cmd_id.isdigit():
            messagebox.showerror("Erreur", "L'ID commande doit être un nombre.")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.cursor().execute(
                "INSERT INTO livraisons (commande_id, fournisseur_id, date_livraison, transporteur) VALUES (?,?,?,?)",
                (int(cmd_id), self.four_id, date, trans)
            )
            conn.commit()
            conn.close()
            for e in (self.e_liv_cmd, self.e_liv_date, self.e_liv_trans):
                e.delete(0, "end")
            self.charger_livraisons()
        except Exception as e:
            messagebox.showerror("Erreur BDD", str(e))

    def charger_livraisons(self):
        for w in self.liste_livraisons.winfo_children():
            w.destroy()
        try:
            conn = sqlite3.connect(DB_PATH)
            cur  = conn.cursor()
            cur.execute(
                "SELECT id, commande_id, date_livraison, transporteur, statut FROM livraisons WHERE fournisseur_id=? ORDER BY id DESC",
                (self.four_id,)
            )
            livs = cur.fetchall()
            conn.close()

            if not livs:
                ctk.CTkLabel(self.liste_livraisons, text="Aucune livraison enregistrée.",
                             font=FONT_NORMAL, text_color=COULEURS["texte_gris"]).pack(pady=30)
                return

            LIV_COLORS = {
                "Préparée":   (COULEURS["fond_input"], COULEURS["texte_gris"]),
                "En cours":   ("#E3F2FD", COULEURS["bleu_fournisseur"]),
                "Livrée":     ("#E8F5E9", COULEURS["vert_primaire"]),
                "Incident":   ("#FFECEC", COULEURS["danger"]),
            }
            LIV_SUIVANTS = {"Préparée": "En cours", "En cours": "Livrée"}

            for liv_id, cmd_id, date, trans, statut in livs:
                bg, sc = LIV_COLORS.get(statut, (COULEURS["fond_input"], COULEURS["texte_gris"]))
                row = ctk.CTkFrame(self.liste_livraisons, fg_color=bg, corner_radius=10)
                row.pack(fill="x", pady=4, padx=10)

                left = ctk.CTkFrame(row, fg_color="transparent")
                left.pack(side="left", fill="both", expand=True, padx=16, pady=12)
                ctk.CTkLabel(left, text=f"Livraison #{liv_id}  (Commande #{cmd_id})",
                             font=("Segoe UI", 13, "bold"), text_color=COULEURS["texte_principal"]).pack(anchor="w")
                ctk.CTkLabel(left, text=f"📅 {date or '—'}   🚛 {trans or '—'}",
                             font=FONT_PETIT, text_color=COULEURS["texte_gris"]).pack(anchor="w", pady=(2, 0))

                right = ctk.CTkFrame(row, fg_color="transparent")
                right.pack(side="right", padx=12)
                creer_badge(right, f"  {statut}  ", bg, sc, taille=11).pack(pady=4)
                if statut in LIV_SUIVANTS:
                    suivant = LIV_SUIVANTS[statut]
                    ctk.CTkButton(right, text=f"→ {suivant}", height=28, width=110, corner_radius=6,
                                  fg_color=COULEURS["vert_primaire"], hover_color=COULEURS["vert_clair"],
                                  text_color="white", font=("Segoe UI", 10, "bold"),
                                  command=lambda lid=liv_id, s=suivant: self.changer_statut_liv(lid, s)
                                  ).pack(pady=2)
                if statut not in ("Livrée",):
                    ctk.CTkButton(right, text="⚠ Incident", height=26, width=90, corner_radius=6,
                                  fg_color="#FFECEC", hover_color="#FFCDD2",
                                  text_color=COULEURS["danger"], font=("Segoe UI", 10),
                                  command=lambda lid=liv_id: self.changer_statut_liv(lid, "Incident")
                                  ).pack(pady=2)
        except Exception as e:
            print(e)

    def changer_statut_liv(self, liv_id, nouveau):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.cursor().execute("UPDATE livraisons SET statut=? WHERE id=?", (nouveau, liv_id))
            conn.commit()
            conn.close()
            self.charger_livraisons()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # =========================================================
    # ─── 4. STATISTIQUES ──────────────────────────────────────
    # =========================================================
    def afficher_statistiques(self):
        self._nav("Statistiques", lambda: None)
        self.nettoyer_contenu()
        self._entete_section("Statistiques", "Vue d'ensemble de votre activité")

        def fetch(q, params=()):
            try:
                conn = sqlite3.connect(DB_PATH)
                cur  = conn.cursor()
                cur.execute(q, params)
                v = cur.fetchone()
                conn.close()
                return v[0] if v else 0
            except Exception:
                return 0

        total_produits  = fetch("SELECT COUNT(*) FROM catalogue_fournisseur WHERE fournisseur_id=?", (self.four_id,))
        stock_total     = fetch("SELECT SUM(stock_dispo) FROM catalogue_fournisseur WHERE fournisseur_id=?", (self.four_id,))
        ca_estime       = fetch("SELECT SUM(prix_unitaire * stock_dispo) FROM catalogue_fournisseur WHERE fournisseur_id=?", (self.four_id,))
        cmds_total      = fetch("SELECT COUNT(*) FROM commandes WHERE fournisseur_id=?", (self.four_id,))
        cmds_attente    = fetch("SELECT COUNT(*) FROM commandes WHERE fournisseur_id=? AND statut='En attente'", (self.four_id,))
        cmds_livrees    = fetch("SELECT COUNT(*) FROM commandes WHERE fournisseur_id=? AND statut='Livrée'", (self.four_id,))
        livs_total      = fetch("SELECT COUNT(*) FROM livraisons WHERE fournisseur_id=?", (self.four_id,))
        produits_bas    = fetch("SELECT COUNT(*) FROM catalogue_fournisseur WHERE fournisseur_id=? AND stock_dispo < 10", (self.four_id,))

        # KPI grid
        tuiles = [
            ("📦 Produits catalogue", str(total_produits), COULEURS["bleu_fournisseur"]),
            ("🗄️ Unités en stock",    str(stock_total or 0), COULEURS["vert_primaire"]),
            ("💰 Valeur catalogue",   f"{ca_estime or 0:,.0f} DA", "#8E44AD"),
            ("🛒 Commandes reçues",   str(cmds_total), COULEURS["warning"]),
            ("⏳ En attente",         str(cmds_attente), COULEURS["danger"]),
            ("✅ Livrées",            str(cmds_livrees), COULEURS["vert_accent"]),
            ("🚚 Livraisons totales", str(livs_total), COULEURS["bleu_clair"]),
            ("⚠ Stock bas (<10)",    str(produits_bas), COULEURS["warning"]),
        ]

        grille = ctk.CTkFrame(self.zone_contenu, fg_color="transparent")
        grille.pack(fill="x", padx=30, pady=(20, 8))
        grille.columnconfigure(0, weight=1)
        grille.columnconfigure(1, weight=1)
        grille.columnconfigure(2, weight=1)
        grille.columnconfigure(3, weight=1)

        for i, (label, val, couleur) in enumerate(tuiles):
            outer2, c2 = creer_carte(grille)
            outer2.grid(row=i // 4, column=i % 4, padx=8, pady=8, sticky="nsew")
            ctk.CTkLabel(c2, text=val, font=("Segoe UI", 30, "bold"),
                         text_color=couleur).pack(pady=(20, 2))
            ctk.CTkLabel(c2, text=label, font=FONT_PETIT,
                         text_color=COULEURS["texte_gris"]).pack(pady=(0, 18))

        # Tableau top 5 produits les plus commandés
        outer3, card_top = creer_carte(self.zone_contenu)
        outer3.pack(fill="x", padx=30, pady=(8, 24))
        ctk.CTkLabel(card_top, text="🏆  Top 5 produits les plus commandés",
                     font=("Segoe UI", 13, "bold"),
                     text_color=COULEURS["texte_principal"]).pack(anchor="w", padx=24, pady=(16, 8))
        try:
            conn = sqlite3.connect(DB_PATH)
            cur  = conn.cursor()
            cur.execute(
                "SELECT produit, SUM(quantite) as total FROM commandes WHERE fournisseur_id=? GROUP BY produit ORDER BY total DESC LIMIT 5",
                (self.four_id,)
            )
            top5 = cur.fetchall()
            conn.close()
            if top5:
                for rank, (prod, total) in enumerate(top5, 1):
                    r = ctk.CTkFrame(card_top, fg_color=COULEURS["fond_input"], corner_radius=8)
                    r.pack(fill="x", padx=24, pady=3)
                    ctk.CTkLabel(r, text=f"#{rank}", font=("Segoe UI", 12, "bold"),
                                 text_color=COULEURS["bleu_fournisseur"], width=36).pack(side="left", padx=12, pady=10)
                    ctk.CTkLabel(r, text=prod, font=("Segoe UI", 12),
                                 text_color=COULEURS["texte_principal"]).pack(side="left", fill="x", expand=True)
                    ctk.CTkLabel(r, text=f"{total} unités commandées", font=("Segoe UI", 11),
                                 text_color=COULEURS["texte_gris"]).pack(side="right", padx=16)
            else:
                ctk.CTkLabel(card_top, text="Pas encore de données de commandes.",
                             font=FONT_NORMAL, text_color=COULEURS["texte_gris"]).pack(pady=20)
        except Exception as e:
            ctk.CTkLabel(card_top, text=f"Erreur : {e}",
                         font=FONT_PETIT, text_color=COULEURS["danger"]).pack(pady=20)
        ctk.CTkFrame(card_top, height=1, fg_color="transparent").pack(pady=8)
    def deconnexion(self):
        self.quit()

# =========================================================
if __name__ == "__main__":
    login_app = LoginFournisseur()
    login_app.mainloop()

    if login_app.connexion_reussie:
        dash = DashboardFournisseur(login_app.fournisseur_data)
        dash.mainloop()