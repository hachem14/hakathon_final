import customtkinter as ctk
from PIL import Image
import sqlite3
from tkinter import messagebox, filedialog
import tkinter as tk

import sys
import os

def get_resource_path(filename):
    """Retourne le chemin absolu vers une ressource (fonctionne aussi en .exe PyInstaller)."""
    if getattr(sys, 'frozen', False):
        # Mode .exe PyInstaller : les fichiers sont dans le dossier du .exe
        base = os.path.dirname(sys.executable)
    else:
        # Mode script Python normal
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)

DB_PATH = get_resource_path('medsafe_cabinet.db')
LOGO_PATH = get_resource_path('mokkt.jpg')


# =========================================================
# THÈME GLOBAL MEDSAFE — Design System
# =========================================================
COULEURS = {
    "fond_principal":   "#F0F4F3",
    "fond_sidebar":     "#0D2B28",
    "fond_carte":       "#FFFFFF",
    "vert_primaire":    "#1A6B55",
    "vert_clair":       "#2C9970",
    "vert_accent":      "#3EBF8A",
    "teal_doux":        "#A8D5C8",
    "texte_principal":  "#0D2B28",
    "texte_clair":      "#FFFFFF",
    "texte_gris":       "#6B7F7D",
    "danger":           "#C0392B",
    "warning":          "#E67E22",
    "bordure":          "#D4E8E2",
    "fond_input":       "#EEF5F3",
    "sidebar_active":   "#1A6B55",
    "sidebar_hover":    "#1A4A40",
    "fond_entete":      "#0D2B28",
}

# Police plus élégante
FONT_TITRE    = ("Segoe UI", 26, "bold")
FONT_SOUS     = ("Segoe UI", 14, "bold")
FONT_NORMAL   = ("Segoe UI", 13)
FONT_PETIT    = ("Segoe UI", 11)
FONT_BTN      = ("Segoe UI", 13, "bold")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


# =========================================================
# COMPOSANTS RÉUTILISABLES
# =========================================================
def creer_carte(parent, **kwargs):
    """Carte blanche avec ombre simulée"""
    outer = ctk.CTkFrame(parent, fg_color=COULEURS["bordure"], corner_radius=14)
    inner = ctk.CTkFrame(outer, fg_color=COULEURS["fond_carte"], corner_radius=12, **kwargs)
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    return outer, inner

def creer_badge(parent, texte, couleur_fond, couleur_texte, taille=11):
    badge = ctk.CTkLabel(
        parent, text=texte,
        fg_color=couleur_fond, text_color=couleur_texte,
        font=("Segoe UI", taille, "bold"),
        corner_radius=8, padx=10, pady=3
    )
    return badge

def creer_separateur(parent, couleur=None):
    c = couleur or COULEURS["bordure"]
    sep = ctk.CTkFrame(parent, height=1, fg_color=c)
    sep.pack(fill="x", padx=20, pady=8)
    return sep


# =========================================================
# 1. FENÊTRE DE CONNEXION
# =========================================================
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MEDSAFE — Authentification")
        self.geometry("480x720")
        self.resizable(False, False)
        self.configure(fg_color=COULEURS["fond_principal"])
        self.connexion_reussie = False
        self.medecin_data = None
        self.afficher_login()

    def nettoyer(self):
        for w in self.winfo_children():
            w.destroy()

    def ajouter_logo(self, taille=(110, 110)):
        """Logo MEDSAFE + titre"""
        try:
            img = ctk.CTkImage(
                light_image=Image.open(LOGO_PATH),
                dark_image=Image.open(LOGO_PATH),
                size=taille
            )
            ctk.CTkLabel(self, image=img, text="").pack(pady=(45, 6))
        except Exception:
            # Fallback élégant si logo absent
            logo_frame = ctk.CTkFrame(self, fg_color=COULEURS["vert_primaire"], corner_radius=55,
                                       width=taille[0], height=taille[1])
            logo_frame.pack(pady=(45, 6))
            logo_frame.pack_propagate(False)
            ctk.CTkLabel(logo_frame, text="⚕", font=("Segoe UI", 42), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

    def afficher_login(self):
        self.nettoyer()
        self.ajouter_logo()

        ctk.CTkLabel(self, text="MEDSAFE", font=("Segoe UI", 28, "bold"),
                     text_color=COULEURS["fond_entete"]).pack()
        ctk.CTkLabel(self, text="Espace Médecin", font=("Segoe UI", 13),
                     text_color=COULEURS["texte_gris"]).pack(pady=(2, 28))

        # Carte formulaire
        card_outer, card = creer_carte(self)
        card_outer.pack(padx=40, fill="x")

        ctk.CTkLabel(card, text="Connexion", font=("Segoe UI", 15, "bold"),
                     text_color=COULEURS["texte_principal"]).pack(anchor="w", padx=24, pady=(20, 12))

        self.entry_email = ctk.CTkEntry(
            card, placeholder_text="Adresse email",
            height=44, corner_radius=10,
            fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"],
            border_width=1, text_color=COULEURS["texte_principal"],
            font=FONT_NORMAL
        )
        self.entry_email.pack(fill="x", padx=24, pady=6)

        self.entry_mdp = ctk.CTkEntry(
            card, placeholder_text="Mot de passe", show="●",
            height=44, corner_radius=10,
            fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"],
            border_width=1, text_color=COULEURS["texte_principal"],
            font=FONT_NORMAL
        )
        self.entry_mdp.pack(fill="x", padx=24, pady=6)

        ctk.CTkButton(
            card, text="Se connecter", height=46,
            fg_color=COULEURS["vert_primaire"], hover_color=COULEURS["vert_clair"],
            font=FONT_BTN, corner_radius=10,
            command=self.verifier_login
        ).pack(fill="x", padx=24, pady=(14, 20))

        # Lien inscription
        lien_frame = ctk.CTkFrame(self, fg_color="transparent")
        lien_frame.pack(pady=16)
        ctk.CTkLabel(lien_frame, text="Pas encore de compte ?",
                     font=FONT_PETIT, text_color=COULEURS["texte_gris"]).pack(side="left")
        ctk.CTkButton(
            lien_frame, text=" Créer un compte", fg_color="transparent",
            text_color=COULEURS["vert_primaire"], hover_color=COULEURS["fond_principal"],
            font=("Segoe UI", 11, "bold"), command=self.afficher_inscription
        ).pack(side="left")

    def afficher_inscription(self):
        self.nettoyer()
        self.ajouter_logo((90, 90))
        ctk.CTkLabel(self, text="Nouveau compte médecin", font=("Segoe UI", 18, "bold"),
                     text_color=COULEURS["fond_entete"]).pack(pady=(4, 18))

        card_outer, card = creer_carte(self)
        card_outer.pack(padx=40, fill="x")

        champs = [
            ("reg_nom", "Nom complet (ex : Dr. Benali)", False),
            ("reg_spec", "Spécialité (ex : Cardiologue)", False),
            ("reg_email", "Adresse email", False),
            ("reg_mdp", "Mot de passe", True),
        ]
        for attr, ph, is_pass in champs:
            entry = ctk.CTkEntry(
                card, placeholder_text=ph, height=42, corner_radius=10,
                fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"],
                border_width=1, text_color=COULEURS["texte_principal"],
                font=FONT_NORMAL, show="●" if is_pass else ""
            )
            entry.pack(fill="x", padx=24, pady=5)
            setattr(self, attr, entry)

        ctk.CTkButton(
            card, text="Créer le compte", height=44,
            fg_color=COULEURS["vert_primaire"], hover_color=COULEURS["vert_clair"],
            font=FONT_BTN, corner_radius=10, command=self.enregistrer_medecin
        ).pack(fill="x", padx=24, pady=(12, 20))

        ctk.CTkButton(
            self, text="← Retour à la connexion",
            fg_color="transparent", text_color=COULEURS["texte_gris"],
            hover_color=COULEURS["fond_principal"], font=FONT_PETIT,
            command=self.afficher_login
        ).pack(pady=8)

    def verifier_login(self):
        email, mdp = self.entry_email.get(), self.entry_mdp.get()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM medecins WHERE email = ? AND mot_de_passe = ?", (email, mdp))
            medecin = cursor.fetchone()
            conn.close()
            if medecin:
                self.medecin_data = medecin
                self.connexion_reussie = True
                self.destroy()
            else:
                messagebox.showerror("Erreur d'authentification", "Email ou mot de passe incorrect.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Problème de base de données : {e}")

    def enregistrer_medecin(self):
        nom = self.reg_nom.get()
        spec = self.reg_spec.get()
        email = self.reg_email.get()
        mdp = self.reg_mdp.get()
        if not nom or not email or not mdp:
            messagebox.showwarning("Champs manquants", "Veuillez remplir tous les champs obligatoires.")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS medecins
                (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, specialite TEXT, email TEXT UNIQUE, mot_de_passe TEXT)''')
            cursor.execute("INSERT INTO medecins (nom, specialite, email, mot_de_passe) VALUES (?, ?, ?, ?)",
                           (nom, spec, email, mdp))
            conn.commit()
            conn.close()
            messagebox.showinfo("Compte créé ✓", "Votre compte a été créé avec succès. Connectez-vous.")
            self.afficher_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Email existant", "Cet email est déjà associé à un compte.")
        except Exception as e:
            print(f"Erreur : {e}")


# =========================================================
# 2. TABLEAU DE BORD PRINCIPAL
# =========================================================
class DashboardMedecin(ctk.CTk):
    def __init__(self, medecin_connecte):
        super().__init__()
        self.medecin_info = medecin_connecte
        self.title("MEDSAFE — Espace Médecin")
        self.geometry("1240x820")
        self.minsize(1000, 680)
        self.configure(fg_color=COULEURS["fond_principal"])

        self._construire_interface()
        self.afficher_profil()

    def _construire_interface(self):
        # ─── SIDEBAR ───────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COULEURS["fond_sidebar"])
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        try:
            img = ctk.CTkImage(light_image=Image.open(LOGO_PATH), dark_image=Image.open(LOGO_PATH), size=(120, 120))
            ctk.CTkLabel(self.sidebar, image=img, text="").pack(pady=(30, 4))
        except Exception:
            logo_frame = ctk.CTkFrame(self.sidebar, fg_color=COULEURS["vert_primaire"],
                                       corner_radius=40, width=80, height=80)
            logo_frame.pack(pady=(30, 4))
            logo_frame.pack_propagate(False)
            ctk.CTkLabel(logo_frame, text="⚕", font=("Segoe UI", 34), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.sidebar, text="MEDSAFE", font=("Segoe UI", 16, "bold"),
                     text_color=COULEURS["teal_doux"]).pack()
        ctk.CTkLabel(self.sidebar, text="Cabinet Médical", font=("Segoe UI", 10),
                     text_color="#7AAFA4").pack(pady=(0, 24))

        creer_separateur(self.sidebar, "#1A3D38")

        # Boutons navigation
        self.btns_nav = {}
        nav_items = [
            ("👤", "Mon Profil",       self.afficher_profil),
            ("🗂",  "Patients",         self.afficher_malades),
            ("📓", "Journal Médical",   self.afficher_journal),
            ("📝", "Ordonnance",        self.afficher_ordonnance),
            ("🩺", "Équipements",       self.afficher_equipement),
        ]
        for icone, label, cmd in nav_items:
            btn = self._creer_btn_nav(icone, label, cmd)
            self.btns_nav[label] = btn

        # Pied de sidebar — info médecin
        creer_separateur(self.sidebar, "#1A3D38")
        nom_md = self.medecin_info[1] if self.medecin_info else "Médecin"
        spec_md = self.medecin_info[2] if self.medecin_info else ""
        ctk.CTkLabel(self.sidebar, text=nom_md, font=("Segoe UI", 12, "bold"),
                     text_color=COULEURS["texte_clair"]).pack(pady=(10, 0))
        ctk.CTkLabel(self.sidebar, text=spec_md, font=("Segoe UI", 10),
                     text_color="#7AAFA4").pack(pady=(0, 8))
        ctk.CTkButton(
            self.sidebar, text="Déconnexion", height=34,
            fg_color="#1A3D38", hover_color=COULEURS["danger"],
            text_color="#7AAFA4", font=("Segoe UI", 11),
            command=self.destroy, corner_radius=8
        ).pack(padx=20, pady=(0, 20), fill="x")

        # ─── ZONE PRINCIPALE ───────────────────────────────────────
        self.zone_contenu = ctk.CTkScrollableFrame(self, fg_color=COULEURS["fond_principal"], corner_radius=0)
        self.zone_contenu.pack(side="right", fill="both", expand=True)

    def _creer_btn_nav(self, icone, label, cmd):
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", corner_radius=10)
        frame.pack(fill="x", padx=12, pady=2)
        btn = ctk.CTkButton(
            frame, text=f"  {icone}  {label}",
            anchor="w", height=44, corner_radius=10,
            fg_color="transparent", hover_color=COULEURS["sidebar_hover"],
            font=("Segoe UI", 13), text_color=COULEURS["texte_clair"],
            command=lambda: self._nav(label, cmd)
        )
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
        frame = ctk.CTkFrame(self.zone_contenu, fg_color="transparent")
        frame.pack(fill="x", padx=30, pady=(28, 0))
        ctk.CTkLabel(frame, text=titre, font=FONT_TITRE,
                     text_color=COULEURS["texte_principal"]).pack(anchor="w")
        if sous_titre:
            ctk.CTkLabel(frame, text=sous_titre, font=FONT_PETIT,
                         text_color=COULEURS["texte_gris"]).pack(anchor="w", pady=(2, 0))

    # ─── 0. PROFIL ─────────────────────────────────────────────────
    def afficher_profil(self):
        self._nav("Mon Profil", lambda: None)
        self.nettoyer_contenu()
        self._entete_section("Mon Profil", "Informations professionnelles")

        # Carte principale
        outer, card = creer_carte(self.zone_contenu)
        outer.pack(fill="x", padx=30, pady=20)

        header = ctk.CTkFrame(card, fg_color=COULEURS["vert_primaire"], corner_radius=0, height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        nom = self.medecin_info[1] if self.medecin_info else "Médecin"
        spec = self.medecin_info[2] if self.medecin_info else "—"
        email = self.medecin_info[3] if self.medecin_info else "—"

        ctk.CTkLabel(header, text=nom, font=("Segoe UI", 20, "bold"),
                     text_color="white").pack(anchor="w", padx=30, pady=(18, 0))
        ctk.CTkLabel(header, text=spec, font=("Segoe UI", 12),
                     text_color=COULEURS["teal_doux"]).pack(anchor="w", padx=30)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=30, pady=20)

        for label, valeur in [("Spécialité", spec), ("Email", email), ("Statut", "Actif ✓")]:
            row = ctk.CTkFrame(info_frame, fg_color=COULEURS["fond_input"], corner_radius=8)
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=label, font=("Segoe UI", 11), text_color=COULEURS["texte_gris"],
                         width=120, anchor="w").pack(side="left", padx=16, pady=12)
            ctk.CTkLabel(row, text=valeur, font=("Segoe UI", 12, "bold"),
                         text_color=COULEURS["texte_principal"]).pack(side="left", padx=8)

        # Stats rapides
        stats_frame = ctk.CTkFrame(self.zone_contenu, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=0)

        self._stat_card(stats_frame, "Patients", self._compter("patients"), "🧑‍🤝‍🧑", COULEURS["vert_accent"])
        self._stat_card(stats_frame, "Consultations", self._compter("consultations"), "📓", "#3D8EC4")
        self._stat_card(stats_frame, "Équipements", self._compter("equipements"), "🩺", "#C4873D")

    def _stat_card(self, parent, label, val, icone, couleur):
        outer, card = creer_carte(parent)
        outer.pack(side="left", expand=True, fill="x", padx=8, pady=8)

        ctk.CTkLabel(card, text=icone, font=("Segoe UI", 26)).pack(pady=(20, 4))
        ctk.CTkLabel(card, text=str(val), font=("Segoe UI", 28, "bold"),
                     text_color=couleur).pack()
        ctk.CTkLabel(card, text=label, font=FONT_PETIT,
                     text_color=COULEURS["texte_gris"]).pack(pady=(2, 18))

    def _compter(self, table):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(f"SELECT COUNT(*) FROM {table}")
            val = c.fetchone()[0]
            conn.close()
            return val
        except Exception:
            return "—"

    # ─── 1. PATIENTS ───────────────────────────────────────────────
    def afficher_malades(self):
        self._nav("Patients", lambda: None)
        self.nettoyer_contenu()
        self._entete_section("Gestion des Patients", "Dossiers médicaux et suivi")

        # Barre d'outils
        toolbar = ctk.CTkFrame(self.zone_contenu, fg_color="transparent")
        toolbar.pack(fill="x", padx=30, pady=16)

        self.entry_recherche = ctk.CTkEntry(
            toolbar, placeholder_text="🔍  Chercher par CNI, nom…",
            height=40, width=300, corner_radius=10,
            fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"],
            border_width=1, text_color=COULEURS["texte_principal"], font=FONT_NORMAL
        )
        self.entry_recherche.pack(side="left")

        ctk.CTkButton(
            toolbar, text="Rechercher", height=40, width=110, corner_radius=10,
            fg_color=COULEURS["fond_entete"], hover_color=COULEURS["vert_primaire"],
            font=FONT_BTN, command=self.rechercher_patients
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            toolbar, text="+ Nouveau Patient", height=40, corner_radius=10,
            fg_color=COULEURS["vert_primaire"], hover_color=COULEURS["vert_clair"],
            font=FONT_BTN, command=self.afficher_formulaire_patient
        ).pack(side="right")

        self.liste_patients_frame = ctk.CTkFrame(self.zone_contenu, fg_color="transparent")
        self.liste_patients_frame.pack(fill="both", expand=True, padx=30)
        self.charger_patients()

    def rechercher_patients(self):
        self.charger_patients(self.entry_recherche.get())

    def charger_patients(self, recherche=""):
        for w in self.liste_patients_frame.winfo_children():
            w.destroy()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            if recherche:
                cursor.execute("SELECT cni, nom, prenom, groupe_sanguin FROM patients WHERE nom LIKE ? OR cni LIKE ?",
                               (f'%{recherche}%', f'%{recherche}%'))
            else:
                cursor.execute("SELECT cni, nom, prenom, groupe_sanguin FROM patients")
            patients = cursor.fetchall()
            conn.close()

            if not patients:
                ctk.CTkLabel(self.liste_patients_frame, text="Aucun patient trouvé.",
                             font=FONT_NORMAL, text_color=COULEURS["texte_gris"]).pack(pady=40)
                return

            for p in patients:
                outer, card = creer_carte(self.liste_patients_frame)
                outer.pack(fill="x", pady=5)

                left = ctk.CTkFrame(card, fg_color="transparent")
                left.pack(side="left", fill="both", expand=True, padx=20, pady=16)

                nom_prenom = f"{p[1].upper()} {p[2].capitalize()}"
                ctk.CTkLabel(left, text=nom_prenom, font=("Segoe UI", 14, "bold"),
                             text_color=COULEURS["texte_principal"]).pack(anchor="w")

                info_row = ctk.CTkFrame(left, fg_color="transparent")
                info_row.pack(anchor="w", pady=(4, 0))
                ctk.CTkLabel(info_row, text=f"CNI : {p[0]}", font=FONT_PETIT,
                             text_color=COULEURS["texte_gris"]).pack(side="left")
                if p[3]:
                    creer_badge(info_row, f"  {p[3]}  ", "#FFF0E6", COULEURS["warning"]).pack(side="left", padx=8)

                ctk.CTkButton(
                    card, text="Ouvrir le dossier →", height=36, corner_radius=8,
                    fg_color=COULEURS["fond_input"], hover_color=COULEURS["teal_doux"],
                    text_color=COULEURS["vert_primaire"], font=("Segoe UI", 12, "bold"),
                    command=lambda pat=p: self.ouvrir_ordonnance_patient(pat)
                ).pack(side="right", padx=20, pady=16)

        except Exception as e:
            print(f"Erreur SQL : {e}")

    # ─── 2. FORMULAIRE NOUVEAU PATIENT ────────────────────────────
    def afficher_formulaire_patient(self):
        self.nettoyer_contenu()
        self._entete_section("Nouveau Dossier Patient", "Enregistrement dans le système")

        outer, card = creer_carte(self.zone_contenu)
        outer.pack(fill="x", padx=30, pady=20)

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=28, pady=20)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        def champ(parent, row, col, label, ph, show="", span=1):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.grid(row=row, column=col, columnspan=span, sticky="ew", padx=10, pady=8)
            ctk.CTkLabel(f, text=label, font=("Segoe UI", 11, "bold"),
                         text_color=COULEURS["texte_principal"]).pack(anchor="w")
            e = ctk.CTkEntry(f, placeholder_text=ph, height=42, corner_radius=10,
                             fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"],
                             border_width=1, text_color=COULEURS["texte_principal"],
                             font=FONT_NORMAL, show=show)
            e.pack(fill="x", pady=(4, 0))
            return e

        self.entry_cni    = champ(grid, 0, 0, "Numéro CNI *", "ex : 12345678")
        self.entry_sang   = champ(grid, 0, 1, "Groupe Sanguin", "ex : O+")
        self.entry_nom    = champ(grid, 1, 0, "Nom *", "Nom de famille")
        self.entry_prenom = champ(grid, 1, 1, "Prénom *", "Prénom")
        self.entry_date   = champ(grid, 2, 0, "Date de naissance", "JJ/MM/AAAA")

        ant_frame = ctk.CTkFrame(card, fg_color="transparent")
        ant_frame.pack(fill="x", padx=38, pady=(0, 16))
        ctk.CTkLabel(ant_frame, text="Antécédents médicaux", font=("Segoe UI", 11, "bold"),
                     text_color=COULEURS["texte_principal"]).pack(anchor="w")
        self.entry_antecedents = ctk.CTkTextbox(
            ant_frame, height=80, corner_radius=10,
            fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"],
            border_width=1, text_color=COULEURS["texte_principal"], font=FONT_NORMAL
        )
        self.entry_antecedents.pack(fill="x", pady=(4, 0))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=38, pady=(8, 24))

        ctk.CTkButton(btn_row, text="Annuler", height=42, corner_radius=10,
                      fg_color=COULEURS["fond_input"], hover_color=COULEURS["bordure"],
                      text_color=COULEURS["texte_gris"], font=FONT_BTN,
                      command=self.afficher_malades).pack(side="left")

        ctk.CTkButton(btn_row, text="💾  Enregistrer le patient", height=42, corner_radius=10,
                      fg_color=COULEURS["vert_primaire"], hover_color=COULEURS["vert_clair"],
                      font=FONT_BTN, command=self.sauvegarder_patient).pack(side="right")

    def sauvegarder_patient(self):
        cni   = self.entry_cni.get()
        nom   = self.entry_nom.get()
        prenom = self.entry_prenom.get()
        date_n = self.entry_date.get()
        sang  = self.entry_sang.get()
        ant   = self.entry_antecedents.get("0.0", "end").strip()

        if not cni or not nom or not prenom:
            messagebox.showwarning("Champs requis", "CNI, Nom et Prénom sont obligatoires.")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS patients
                (id INTEGER PRIMARY KEY AUTOINCREMENT, cni TEXT UNIQUE, nom TEXT, prenom TEXT,
                 date_naissance TEXT, groupe_sanguin TEXT, antecedents_medicaux TEXT)''')
            cursor.execute('''INSERT INTO patients (cni, nom, prenom, date_naissance, groupe_sanguin, antecedents_medicaux)
                              VALUES (?, ?, ?, ?, ?, ?)''', (cni, nom, prenom, date_n, sang, ant))
            conn.commit()
            conn.close()
            messagebox.showinfo("Patient enregistré ✓", f"{nom} {prenom} a été ajouté avec succès.")
            self.afficher_malades()
        except sqlite3.IntegrityError:
            messagebox.showerror("CNI déjà utilisé", f"Un patient avec la CNI {cni} existe déjà.")

    # ─── 3. JOURNAL MÉDICAL ────────────────────────────────────────
    def afficher_journal(self):
        self._nav("Journal Médical", lambda: None)
        self.nettoyer_contenu()

        if not hasattr(self, 'patient_actuel'):
            self._message_selection_requise()
            return

        p = self.patient_actuel
        self._entete_section("Journal Médical", f"Historique de {p[1].upper()} {p[2].capitalize()}")

        # Badge patient
        badge_outer, badge_card = creer_carte(self.zone_contenu)
        badge_outer.pack(fill="x", padx=30, pady=(12, 0))
        badge_inner = ctk.CTkFrame(badge_card, fg_color=COULEURS["vert_primaire"], corner_radius=12, height=56)
        badge_inner.pack(fill="x")
        badge_inner.pack_propagate(False)
        ctk.CTkLabel(badge_inner, text=f"Patient : {p[1].upper()} {p[2].capitalize()}   ·   CNI : {p[0]}",
                     font=("Segoe UI", 13, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        # Formulaire nouvelle consultation
        outer, form = creer_carte(self.zone_contenu)
        outer.pack(fill="x", padx=30, pady=12)
        ctk.CTkLabel(form, text="Nouvelle consultation", font=("Segoe UI", 13, "bold"),
                     text_color=COULEURS["texte_principal"]).pack(anchor="w", padx=24, pady=(16, 8))

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(0, 16))

        self.entry_date_cons = ctk.CTkEntry(row, placeholder_text="Date (ex : 29/04/2026)", height=40,
                                             width=180, corner_radius=10,
                                             fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"],
                                             border_width=1, text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.entry_date_cons.pack(side="left", padx=(0, 10))

        self.entry_diag = ctk.CTkEntry(row, placeholder_text="Diagnostic (ex : Angine bactérienne…)",
                                        height=40, corner_radius=10,
                                        fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"],
                                        border_width=1, text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.entry_diag.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(row, text="Enregistrer", height=40, width=130, corner_radius=10,
                      fg_color=COULEURS["vert_primaire"], hover_color=COULEURS["vert_clair"],
                      font=FONT_BTN, command=self.sauvegarder_consultation).pack(side="right")

        # Liste consultations
        ctk.CTkLabel(self.zone_contenu, text="Consultations précédentes",
                     font=("Segoe UI", 13, "bold"), text_color=COULEURS["texte_principal"]).pack(
                         anchor="w", padx=30, pady=(8, 4))

        self.liste_consultations = ctk.CTkScrollableFrame(
            self.zone_contenu, height=280, corner_radius=12,
            fg_color=COULEURS["fond_carte"], border_color=COULEURS["bordure"], border_width=1
        )
        self.liste_consultations.pack(fill="both", padx=30, pady=(0, 24))
        self.charger_historique_consultations()

    def sauvegarder_consultation(self):
        date_c = self.entry_date_cons.get()
        diag   = self.entry_diag.get()
        if not date_c or not diag:
            messagebox.showwarning("Incomplet", "Remplissez la date et le diagnostic.")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS consultations
                (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT,
                 date_consultation TEXT, diagnostic TEXT, observations TEXT)''')
            cursor.execute('''INSERT INTO consultations (patient_id, date_consultation, diagnostic, observations)
                              VALUES (?, ?, ?, ?)''', (self.patient_actuel[0], date_c, diag, ""))
            conn.commit()
            conn.close()
            self.afficher_journal()
        except Exception as e:
            print(f"Erreur SQL : {e}")

    def charger_historique_consultations(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT date_consultation, diagnostic FROM consultations WHERE patient_id = ? ORDER BY id DESC",
                           (self.patient_actuel[0],))
            consultations = cursor.fetchall()
            conn.close()

            if not consultations:
                ctk.CTkLabel(self.liste_consultations, text="Aucune consultation enregistrée pour ce patient.",
                             font=FONT_NORMAL, text_color=COULEURS["texte_gris"]).pack(pady=20)
                return

            for c in consultations:
                row = ctk.CTkFrame(self.liste_consultations, fg_color=COULEURS["fond_input"], corner_radius=10)
                row.pack(fill="x", pady=4, padx=10)

                ctk.CTkLabel(row, text=c[0], font=("Segoe UI", 11),
                             text_color=COULEURS["texte_gris"], width=120, anchor="w").pack(side="left", padx=16, pady=14)
                ctk.CTkLabel(row, text=c[1], font=("Segoe UI", 12, "bold"),
                             text_color=COULEURS["texte_principal"]).pack(side="left", padx=8)
        except Exception:
            pass

    # ─── 4. ORDONNANCE ────────────────────────────────────────────
    def ouvrir_ordonnance_patient(self, patient_data):
        self.patient_actuel = patient_data
        self.afficher_ordonnance()

    def afficher_ordonnance(self):
        self._nav("Ordonnance", lambda: None)
        self.nettoyer_contenu()

        if not hasattr(self, 'patient_actuel'):
            self._message_selection_requise()
            return

        p = self.patient_actuel
        self._entete_section("Rédaction d'Ordonnance", f"Pour {p[1].upper()} {p[2].capitalize()}")

        # Info patient
        outer, info_card = creer_carte(self.zone_contenu)
        outer.pack(fill="x", padx=30, pady=(12, 0))

        info_inner = ctk.CTkFrame(info_card, fg_color=COULEURS["fond_entete"], corner_radius=12, height=56)
        info_inner.pack(fill="x")
        info_inner.pack_propagate(False)
        infos = f"  {p[1].upper()} {p[2].capitalize()}   ·   CNI : {p[0]}   ·   Groupe : {p[3] or '—'}"
        ctk.CTkLabel(info_inner, text=infos, font=("Segoe UI", 12, "bold"),
                     text_color="white").place(relx=0.02, rely=0.5, anchor="w")

        # Zone de rédaction
        outer2, edit_card = creer_carte(self.zone_contenu)
        outer2.pack(fill="both", expand=True, padx=30, pady=16)

        ctk.CTkLabel(edit_card, text="Prescription", font=("Segoe UI", 13, "bold"),
                     text_color=COULEURS["texte_principal"]).pack(anchor="w", padx=24, pady=(16, 6))

        self.texte_ordonnance = ctk.CTkTextbox(
            edit_card, corner_radius=10,
            fg_color=COULEURS["fond_input"], border_color=COULEURS["bordure"],
            border_width=1, font=("Georgia", 14), text_color=COULEURS["texte_principal"]
        )
        self.texte_ordonnance.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        nom_med  = self.medecin_info[1] if self.medecin_info else "Médecin"
        spec_med = self.medecin_info[2] if self.medecin_info else ""
        entete   = f"Dr. {nom_med} — {spec_med}\n{'─' * 50}\n\nPatient : {p[1].upper()} {p[2].capitalize()}\n\nPrescription :\n\n  - "
        self.texte_ordonnance.insert("0.0", entete)

        ctk.CTkButton(
            edit_card, text="🖨  Exporter l'ordonnance (.txt)",
            height=42, corner_radius=10,
            fg_color=COULEURS["vert_primaire"], hover_color=COULEURS["vert_clair"],
            font=FONT_BTN, command=self.exporter_ordonnance
        ).pack(padx=24, pady=(0, 20), anchor="e")

    def exporter_ordonnance(self):
        if not hasattr(self, 'patient_actuel'):
            return
        p = self.patient_actuel
        nom_f = f"{p[1].upper()}_{p[2].capitalize()}"
        chemin = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"Ordonnance_{nom_f}.txt",
            title="Enregistrer l'ordonnance",
            filetypes=[("Fichiers Texte", "*.txt")]
        )
        if chemin:
            try:
                contenu = self.texte_ordonnance.get("0.0", "end").strip()
                with open(chemin, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("             CABINET MÉDICAL MEDSAFE\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"Patient  : {p[1].upper()} {p[2].capitalize()}\n")
                    f.write(f"CNI      : {p[0]}   |   Groupe : {p[3]}\n")
                    f.write("-" * 60 + "\n\n")
                    f.write(contenu + "\n\n")
                    f.write("=" * 60 + "\n")
                    f.write("Signature du médecin :\n\n")
                messagebox.showinfo("Exporté ✓", "L'ordonnance a été sauvegardée avec succès.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'exporter : {e}")

    # ─── 5. ÉQUIPEMENTS ───────────────────────────────────────────
    def afficher_equipement(self):
        self._nav("Équipements", lambda: None)
        self.nettoyer_contenu()
        self._entete_section("Gestion des Équipements", "Inventaire du cabinet")

        outer, form = creer_carte(self.zone_contenu)
        outer.pack(fill="x", padx=30, pady=(16, 8))

        ctk.CTkLabel(form, text="Ajouter un article", font=("Segoe UI", 13, "bold"),
                     text_color=COULEURS["texte_principal"]).pack(anchor="w", padx=24, pady=(16, 8))

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(0, 16))

        self.entry_nom_eq = ctk.CTkEntry(row, placeholder_text="Nom de l'article", height=40,
                                          corner_radius=10, fg_color=COULEURS["fond_input"],
                                          border_color=COULEURS["bordure"], border_width=1,
                                          text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.entry_nom_eq.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.entry_qte_eq = ctk.CTkEntry(row, placeholder_text="Quantité", height=40, width=100,
                                          corner_radius=10, fg_color=COULEURS["fond_input"],
                                          border_color=COULEURS["bordure"], border_width=1,
                                          text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.entry_qte_eq.pack(side="left", padx=(0, 8))

        self.entry_seuil_eq = ctk.CTkEntry(row, placeholder_text="Seuil alerte", height=40, width=120,
                                            corner_radius=10, fg_color=COULEURS["fond_input"],
                                            border_color=COULEURS["bordure"], border_width=1,
                                            text_color=COULEURS["texte_principal"], font=FONT_NORMAL)
        self.entry_seuil_eq.pack(side="left", padx=(0, 8))

        ctk.CTkButton(row, text="Ajouter", height=40, width=100, corner_radius=10,
                      fg_color=COULEURS["vert_primaire"], hover_color=COULEURS["vert_clair"],
                      font=FONT_BTN, command=self.sauvegarder_equipement).pack(side="right")

        self.liste_equipements = ctk.CTkScrollableFrame(
            self.zone_contenu, fg_color=COULEURS["fond_carte"],
            corner_radius=12, border_color=COULEURS["bordure"], border_width=1
        )
        self.liste_equipements.pack(fill="both", expand=True, padx=30, pady=(0, 24))
        self.charger_equipements()

    def sauvegarder_equipement(self):
        nom   = self.entry_nom_eq.get()
        qte   = self.entry_qte_eq.get()
        seuil = self.entry_seuil_eq.get()
        if not nom or not qte:
            messagebox.showwarning("Incomplet", "Remplissez le nom et la quantité.")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO equipements (nom_article, quantite, seuil_alerte)
                              VALUES (?, ?, ?)''', (nom, int(qte), int(seuil) if seuil else 5))
            conn.commit()
            conn.close()
            self.afficher_equipement()
        except ValueError:
            messagebox.showerror("Erreur", "La quantité doit être un nombre entier.")
        except Exception as e:
            print(f"Erreur SQL : {e}")

    def charger_equipements(self):
        for w in self.liste_equipements.winfo_children():
            w.destroy()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT nom_article, quantite, seuil_alerte FROM equipements ORDER BY nom_article ASC")
            equipements = cursor.fetchall()
            conn.close()

            if not equipements:
                ctk.CTkLabel(self.liste_equipements, text="L'inventaire est vide.",
                             font=FONT_NORMAL, text_color=COULEURS["texte_gris"]).pack(pady=30)
                return

            for nom, qte, seuil in equipements:
                en_alerte = qte <= seuil
                fond = "#FFF5F5" if en_alerte else COULEURS["fond_input"]

                row = ctk.CTkFrame(self.liste_equipements, fg_color=fond, corner_radius=10)
                row.pack(fill="x", pady=4, padx=10)

                left = ctk.CTkFrame(row, fg_color="transparent")
                left.pack(side="left", fill="both", expand=True, padx=16, pady=12)

                ctk.CTkLabel(left, text=nom, font=("Segoe UI", 13, "bold"),
                             text_color=COULEURS["texte_principal"]).pack(anchor="w")

                sub = ctk.CTkFrame(left, fg_color="transparent")
                sub.pack(anchor="w", pady=(3, 0))
                ctk.CTkLabel(sub, text=f"Quantité : {qte}   Seuil : {seuil}",
                             font=FONT_PETIT, text_color=COULEURS["texte_gris"]).pack(side="left")
                if en_alerte:
                    creer_badge(sub, "  ⚠  Rupture imminente  ", "#FFECEC", COULEURS["danger"]).pack(side="left", padx=8)

                btn_frame = ctk.CTkFrame(row, fg_color="transparent")
                btn_frame.pack(side="right", padx=12)

                ctk.CTkButton(btn_frame, text="Modifier", height=32, width=80, corner_radius=8,
                              fg_color=COULEURS["fond_input"], hover_color=COULEURS["bordure"],
                              text_color=COULEURS["vert_primaire"], font=("Segoe UI", 11, "bold"),
                              command=lambda n=nom: self.modifier_equipement(n)).pack(side="left", padx=4)

                ctk.CTkButton(btn_frame, text="Supprimer", height=32, width=90, corner_radius=8,
                              fg_color="#FFECEC", hover_color="#FFCDD2",
                              text_color=COULEURS["danger"], font=("Segoe UI", 11, "bold"),
                              command=lambda n=nom: self.supprimer_equipement(n)).pack(side="left", padx=4)

        except Exception as e:
            print(f"Erreur SQL : {e}")

    def supprimer_equipement(self, nom_article):
        if messagebox.askyesno("Confirmer", f"Supprimer « {nom_article} » du stock ?"):
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.cursor().execute("DELETE FROM equipements WHERE nom_article = ?", (nom_article,))
                conn.commit()
                conn.close()
                self.afficher_equipement()
            except Exception as e:
                print(f"Erreur SQL : {e}")

    def modifier_equipement(self, nom_article):
        dialog = ctk.CTkInputDialog(text=f"Nouvelle quantité pour « {nom_article} » :", title="Modifier stock")
        val = dialog.get_input()
        if val and val.isdigit():
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.cursor().execute("UPDATE equipements SET quantite = ? WHERE nom_article = ?", (int(val), nom_article))
                conn.commit()
                conn.close()
                self.afficher_equipement()
            except Exception as e:
                print(f"Erreur SQL : {e}")


    def _message_selection_requise(self):
        outer, card = creer_carte(self.zone_contenu)
        outer.pack(padx=30, pady=80, fill="x")
        ctk.CTkLabel(card, text="⚠  Aucun patient sélectionné",
                     font=("Segoe UI", 16, "bold"), text_color=COULEURS["warning"]).pack(pady=(30, 8))
        ctk.CTkLabel(card, text="Veuillez d'abord ouvrir un dossier depuis la section « Patients ».",
                     font=FONT_NORMAL, text_color=COULEURS["texte_gris"]).pack(pady=(0, 30))

    def deconnexion(self):
        self.destroy()


# =========================================================
# POINT D'ENTRÉE
# =========================================================
if __name__ == "__main__":
    login_app = LoginWindow()
    login_app.mainloop()

    if login_app.connexion_reussie:
        dash = DashboardMedecin(login_app.medecin_data)
        dash.mainloop()