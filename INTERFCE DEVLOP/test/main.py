import customtkinter as ctk
from PIL import Image
import sys
import os

# =========================================================
# PATCH GLOBAL — DOIT RESTER EN PREMIÈRE POSITION
# Bloque l'animation CTkButton avant qu'elle soit planifiée
# =========================================================
import safe_button  # noqa: F401

# =========================================================
# CHEMIN RESSOURCES (compatible PyInstaller .exe)
# =========================================================
def get_resource_path(filename):
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)

LOGO_PATH = get_resource_path('mokkt.jpg')

# =========================================================
# THÈME MEDSAFE
# =========================================================
COULEURS = {
    "fond_principal":    "#F0F4F3",
    "fond_sidebar":      "#0D2B28",
    "fond_carte":        "#FFFFFF",
    "vert_primaire":     "#1A6B55",
    "vert_clair":        "#2C9970",
    "vert_accent":       "#3EBF8A",
    "teal_doux":         "#A8D5C8",
    "texte_principal":   "#0D2B28",
    "texte_clair":       "#FFFFFF",
    "texte_gris":        "#6B7F7D",
    "danger":            "#C0392B",
    "warning":           "#E67E22",
    "bordure":           "#D4E8E2",
    "fond_input":        "#EEF5F3",
    "bleu_fournisseur":  "#1A3A6B",
    "bleu_clair":        "#2C5F9E",
    "violet_medecin":    "#5B2D8E",
    "violet_clair":      "#7D3FC1",
}

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


# =========================================================
# FENÊTRE D'ACCUEIL — Choix du profil
# =========================================================
class AccueilMedsafe(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MEDSAFE — Accueil")
        self.geometry("600x700")
        self.resizable(False, False)
        self.configure(fg_color=COULEURS["fond_principal"])
        self._en_transition = False
        self._construire()

    def _construire(self):
        # ── En-tête ──────────────────────────────────────────
        try:
            img = ctk.CTkImage(
                light_image=Image.open(LOGO_PATH),
                dark_image=Image.open(LOGO_PATH),
                size=(130, 130)
            )
            ctk.CTkLabel(self, image=img, text="").pack(pady=(40, 8))
        except Exception:
            logo_f = ctk.CTkFrame(self, fg_color=COULEURS["vert_primaire"],
                                  corner_radius=65, width=130, height=130)
            logo_f.pack(pady=(40, 8))
            logo_f.pack_propagate(False)
            ctk.CTkLabel(logo_f, text="⚕", font=("Segoe UI", 54),
                         text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self, text="MEDSAFE", font=("Segoe UI", 32, "bold"),
                     text_color=COULEURS["texte_principal"]).pack()
        ctk.CTkLabel(self, text="Système de gestion médicale intégré",
                     font=("Segoe UI", 13), text_color=COULEURS["texte_gris"]).pack(pady=(2, 36))

        # ── Séparateur ───────────────────────────────────────
        ctk.CTkLabel(self, text="Choisissez votre espace",
                     font=("Segoe UI", 14, "bold"),
                     text_color=COULEURS["texte_principal"]).pack()
        ctk.CTkFrame(self, height=1, fg_color=COULEURS["bordure"]).pack(
            fill="x", padx=60, pady=(10, 24))

        # ── 3 cartes de choix ────────────────────────────────
        profils = [
            {
                "icone":      "⚕️",
                "titre":      "Médecin",
                "sous_titre": "Patients · Ordonnances · Dossiers",
                "couleur":    COULEURS["violet_medecin"],
                "cmd":        self.ouvrir_medecin,
            },
            {
                "icone":      "💊",
                "titre":      "Pharmacien",
                "sous_titre": "Stocks · Contrôle IA · Panneaux",
                "couleur":    COULEURS["vert_primaire"],
                "cmd":        self.ouvrir_pharmacien,
            },
            {
                "icone":      "🏭",
                "titre":      "Fournisseur",
                "sous_titre": "Catalogue · Commandes · Livraisons",
                "couleur":    COULEURS["bleu_fournisseur"],
                "cmd":        self.ouvrir_fournisseur,
            },
        ]

        for p in profils:
            self._creer_carte_profil(**p)

        # ── Pied de page ─────────────────────────────────────
        ctk.CTkLabel(self, text="© 2025 MEDSAFE — Tous droits réservés",
                     font=("Segoe UI", 10), text_color=COULEURS["texte_gris"]).pack(
            side="bottom", pady=16)

    def _creer_carte_profil(self, icone, titre, sous_titre, couleur, cmd):
        outer = ctk.CTkFrame(self, fg_color=COULEURS["bordure"], corner_radius=14)
        outer.pack(fill="x", padx=60, pady=7)

        inner = ctk.CTkFrame(outer, fg_color=COULEURS["fond_carte"], corner_radius=12)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        btn = ctk.CTkButton(
            inner,
            text="",
            fg_color="transparent",
            hover_color=COULEURS["fond_input"],
            corner_radius=12,
            height=80,
            command=cmd,
            cursor="hand2",
        )
        btn.pack(fill="both", expand=True)

        content = ctk.CTkFrame(inner, fg_color="transparent")
        content.place(relx=0, rely=0, relwidth=1, relheight=1)
        content.bind("<Button-1>", lambda e: cmd())

        bande = ctk.CTkFrame(content, fg_color=couleur, corner_radius=10, width=8)
        bande.pack(side="left", fill="y", padx=(12, 0), pady=10)
        bande.bind("<Button-1>", lambda e: cmd())

        ic = ctk.CTkLabel(content, text=icone, font=("Segoe UI", 36),
                          text_color=couleur, width=60)
        ic.pack(side="left", padx=16)
        ic.bind("<Button-1>", lambda e: cmd())

        txt_f = ctk.CTkFrame(content, fg_color="transparent")
        txt_f.pack(side="left", fill="both", expand=True)
        txt_f.bind("<Button-1>", lambda e: cmd())

        t = ctk.CTkLabel(txt_f, text=titre, font=("Segoe UI", 17, "bold"),
                         text_color=couleur, anchor="w")
        t.pack(anchor="w", pady=(16, 0))
        t.bind("<Button-1>", lambda e: cmd())

        s = ctk.CTkLabel(txt_f, text=sous_titre, font=("Segoe UI", 11),
                         text_color=COULEURS["texte_gris"], anchor="w")
        s.pack(anchor="w", pady=(2, 16))
        s.bind("<Button-1>", lambda e: cmd())

        fl = ctk.CTkLabel(content, text="›", font=("Segoe UI", 32),
                          text_color=COULEURS["bordure"])
        fl.pack(side="right", padx=20)
        fl.bind("<Button-1>", lambda e: cmd())

    # ── Helper navigation ─────────────────────────────────────

    def _lancer(self, callback):
        if self._en_transition:
            return
        self._en_transition = True
        self.update_idletasks()
        self.withdraw()
        try:
            callback()
        except Exception as e:
            import tkinter.messagebox as mb
            mb.showerror("Erreur", str(e))
        finally:
            self.deiconify()
            self._en_transition = False

    # ── Ouverture des espaces ─────────────────────────────────

    def ouvrir_medecin(self):
        def _run():
            from dashboard_medecin import LoginWindow, DashboardMedecin
            login = LoginWindow()
            login.mainloop()
            if hasattr(login, 'connexion_reussie') and login.connexion_reussie:
                DashboardMedecin(login.medecin_data).mainloop()
        self._lancer(_run)

    def ouvrir_pharmacien(self):
        def _run():
            from dashboard_pharmacien_AI import LoginPharmacien, DashboardPharmacien
            login = LoginPharmacien()
            login.mainloop()
            if hasattr(login, 'connexion_reussie') and login.connexion_reussie:
                DashboardPharmacien(login.pharmacien_data).mainloop()
        self._lancer(_run)

    def ouvrir_fournisseur(self):
        def _run():
            from ashboard_fournisseur import LoginFournisseur, DashboardFournisseur
            login = LoginFournisseur()
            login.mainloop()
            if hasattr(login, 'connexion_reussie') and login.connexion_reussie:
                DashboardFournisseur(login.fournisseur_data).mainloop()
        self._lancer(_run)


# =========================================================
if __name__ == "__main__":
    app = AccueilMedsafe()
    app.mainloop()