"""
MedSafe DDI — Application de test du modèle DistilBERT
Lancer : python medsafe_app.py
Requis  : pip install transformers torch tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import sys
import zipfile
from itertools import combinations

# ── Chemins ─────────────────────────────────────────────────
ZIP_PATH   = "medsafe_model.zip"  # zip téléchargé depuis Kaggle
MODEL_DIR  = "medsafe_model"  # dossier extrait

# ── Labels ──────────────────────────────────────────────────
LABEL_MAP   = {0: "MILD",    1: "CAUTION", 2: "DANGER"}
COLOR_MAP   = {0: "#2ecc71", 1: "#f39c12", 2: "#e74c3c"}
BG_MAP      = {0: "#eafaf1", 1: "#fef9e7", 2: "#fdf0ef"}
EMOJI_MAP   = {0: "🟢",      1: "🟡",      2: "🔴"}

# ════════════════════════════════════════════════════════════
class MedSafeApp:
    def __init__(self, root):
        self.root  = root
        self.model = None
        self.tokenizer = None
        self.model_loaded = False

        self._setup_window()
        self._setup_ui()
        self._load_model_async()

    # ── Setup fenêtre ────────────────────────────────────────
    def _setup_window(self):
        self.root.title("MedSafe DDI — Détecteur d'Interactions Médicamenteuses")
        self.root.geometry("900x700")
        self.root.minsize(700, 550)
        self.root.configure(bg="#0f1923")

        # Style ttk
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame",      background="#0f1923")
        style.configure("TLabel",      background="#0f1923", foreground="#e8f4fd", font=("Helvetica", 11))
        style.configure("TButton",     font=("Helvetica", 11, "bold"), padding=8)
        style.configure("TEntry",      font=("Helvetica", 12), padding=6)
        style.configure("Treeview",    font=("Helvetica", 11), rowheight=36, background="#1a2634", foreground="#e8f4fd", fieldbackground="#1a2634")
        style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"), background="#243447", foreground="#7ec8e3")
        style.map("Treeview", background=[("selected", "#2d4a6b")])

    # ── UI principale ────────────────────────────────────────
    def _setup_ui(self):
        # ── Header ──────────────────────────────────────────
        header = tk.Frame(self.root, bg="#0d1f2d", pady=16)
        header.pack(fill="x")

        tk.Label(header, text="💊 MedSafe DDI",
                 font=("Helvetica", 22, "bold"),
                 bg="#0d1f2d", fg="#7ec8e3").pack()
        tk.Label(header, text="Détecteur d'Interactions Médicamenteuses — DistilBERT",
                 font=("Helvetica", 11),
                 bg="#0d1f2d", fg="#5a8fa8").pack()

        # ── Status bar ──────────────────────────────────────
        self.status_var = tk.StringVar(value="⏳ Chargement du modèle...")
        status_bar = tk.Frame(self.root, bg="#0d1f2d", pady=4)
        status_bar.pack(fill="x")
        self.status_lbl = tk.Label(status_bar,
                                   textvariable=self.status_var,
                                   font=("Helvetica", 10),
                                   bg="#0d1f2d", fg="#f39c12")
        self.status_lbl.pack()

        # ── Corps principal ──────────────────────────────────
        body = tk.Frame(self.root, bg="#0f1923", padx=20, pady=10)
        body.pack(fill="both", expand=True)

        # ── Panel gauche : entrée médicaments ───────────────
        left = tk.Frame(body, bg="#1a2634", padx=16, pady=16,
                        relief="flat", bd=0)
        left.pack(side="left", fill="y", padx=(0,12))

        tk.Label(left, text="Médicaments à analyser",
                 font=("Helvetica", 13, "bold"),
                 bg="#1a2634", fg="#7ec8e3").pack(anchor="w", pady=(0,8))

        tk.Label(left, text="Ajouter un médicament :",
                 font=("Helvetica", 10),
                 bg="#1a2634", fg="#8aabb8").pack(anchor="w")

        entry_frame = tk.Frame(left, bg="#1a2634")
        entry_frame.pack(fill="x", pady=4)

        self.drug_entry = tk.Entry(entry_frame,
                                   font=("Helvetica", 12),
                                   bg="#243447", fg="#e8f4fd",
                                   insertbackground="#7ec8e3",
                                   relief="flat", bd=6, width=18)
        self.drug_entry.pack(side="left", fill="x", expand=True)
        self.drug_entry.bind("<Return>", lambda e: self._add_drug())

        tk.Button(entry_frame, text="+",
                  font=("Helvetica", 13, "bold"),
                  bg="#1a6b8a", fg="white",
                  relief="flat", padx=10, cursor="hand2",
                  command=self._add_drug).pack(side="left", padx=(4,0))

        # Liste médicaments
        tk.Label(left, text="Liste :",
                 font=("Helvetica", 10),
                 bg="#1a2634", fg="#8aabb8").pack(anchor="w", pady=(10,2))

        list_frame = tk.Frame(left, bg="#1a2634")
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.drug_listbox = tk.Listbox(list_frame,
                                       font=("Helvetica", 12),
                                       bg="#0f1923", fg="#e8f4fd",
                                       selectbackground="#1a6b8a",
                                       relief="flat", bd=0,
                                       width=20, height=12,
                                       yscrollcommand=scrollbar.set)
        self.drug_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.drug_listbox.yview)

        # Boutons liste
        btn_frame = tk.Frame(left, bg="#1a2634")
        btn_frame.pack(fill="x", pady=(8,0))

        tk.Button(btn_frame, text="🗑 Supprimer",
                  font=("Helvetica", 10),
                  bg="#4a1f1f", fg="#e8a0a0",
                  relief="flat", padx=8, cursor="hand2",
                  command=self._remove_drug).pack(side="left")

        tk.Button(btn_frame, text="🔄 Vider",
                  font=("Helvetica", 10),
                  bg="#2a2a3a", fg="#8aabb8",
                  relief="flat", padx=8, cursor="hand2",
                  command=self._clear_drugs).pack(side="left", padx=(6,0))

        # Bouton analyser
        self.analyze_btn = tk.Button(left,
                                     text="⚡ Analyser les interactions",
                                     font=("Helvetica", 12, "bold"),
                                     bg="#1a6b8a", fg="white",
                                     relief="flat", pady=10,
                                     cursor="hand2",
                                     state="disabled",
                                     command=self._analyze)
        self.analyze_btn.pack(fill="x", pady=(12,0))

        # Exemples rapides
        tk.Label(left, text="Exemples rapides :",
                 font=("Helvetica", 10),
                 bg="#1a2634", fg="#8aabb8").pack(anchor="w", pady=(12,4))

        examples = [
            ("Warfarin + Aspirin", ["Warfarin", "Aspirin"]),
            ("Metformin + Insulin", ["Metformin", "Insulin"]),
            ("Pack complet", ["Aspirin", "Warfarin", "Ibuprofen", "Metformin", "Lisinopril"]),
        ]
        for label, drugs in examples:
            tk.Button(left, text=label,
                      font=("Helvetica", 9),
                      bg="#1e3344", fg="#7ec8e3",
                      relief="flat", padx=6, pady=3,
                      cursor="hand2",
                      command=lambda d=drugs: self._load_example(d)
                      ).pack(fill="x", pady=1)

        # ── Panel droit : résultats ──────────────────────────
        right = tk.Frame(body, bg="#0f1923")
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="Résultats",
                 font=("Helvetica", 13, "bold"),
                 bg="#0f1923", fg="#7ec8e3").pack(anchor="w", pady=(0,6))

        # Tableau résultats
        cols = ("Médicament 1", "Médicament 2", "Risque", "Confiance", "Gemini")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", height=12)

        for col in cols:
            self.tree.heading(col, text=col)
            width = 150 if col in ("Médicament 1", "Médicament 2") else 100
            self.tree.column(col, width=width, anchor="center")

        # Tags couleur
        self.tree.tag_configure("MILD",    background="#1a3a2a", foreground="#2ecc71")
        self.tree.tag_configure("CAUTION", background="#3a2e1a", foreground="#f39c12")
        self.tree.tag_configure("DANGER",  background="#3a1a1a", foreground="#e74c3c")

        tree_scroll = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="left", fill="y")

        # ── Résumé ──────────────────────────────────────────
        self.summary_frame = tk.Frame(self.root, bg="#0d1f2d", padx=20, pady=10)
        self.summary_frame.pack(fill="x")

        self.summary_var = tk.StringVar(value="")
        tk.Label(self.summary_frame,
                 textvariable=self.summary_var,
                 font=("Helvetica", 11),
                 bg="#0d1f2d", fg="#e8f4fd",
                 wraplength=860, justify="left").pack(anchor="w")

        # ── Log ─────────────────────────────────────────────
        log_frame = tk.Frame(self.root, bg="#0f1923", padx=20)
        log_frame.pack(fill="x", pady=(0,10))

        self.log = scrolledtext.ScrolledText(log_frame,
                                             height=4,
                                             font=("Courier", 9),
                                             bg="#080f16", fg="#4a8fa8",
                                             relief="flat", state="disabled")
        self.log.pack(fill="x")

    # ── Charger modèle en arrière-plan ──────────────────────
    def _load_model_async(self):
        def load():
            try:
                self._log("🔍 Recherche du modèle...")

                # Extraire le zip si nécessaire
                if not os.path.exists(MODEL_DIR):
                    if os.path.exists(ZIP_PATH):
                        self._log(f"📦 Extraction de {ZIP_PATH}...")
                        with zipfile.ZipFile(ZIP_PATH, 'r') as z:
                            z.extractall(MODEL_DIR)
                        self._log("✅ Extraction terminée")
                    else:
                        self._log(f"❌ Fichier introuvable : {ZIP_PATH}")
                        self._log(f"   Place medsafe_model.zip dans : {os.getcwd()}")
                        self._set_status("❌ Modèle introuvable — place medsafe_model.zip ici", "red")
                        return

                self._log("⏳ Chargement du tokenizer...")
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                import torch

                self.tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
                self._log("✅ Tokenizer chargé")

                self._log("⏳ Chargement du modèle DistilBERT...")
                self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
                self.model.eval()
                self._log("✅ Modèle chargé — prêt !")

                self.model_loaded = True
                self._set_status("✅ Modèle prêt — entrez vos médicaments", "#2ecc71")
                self.root.after(0, lambda: self.analyze_btn.config(state="normal"))

            except Exception as e:
                self._log(f"❌ Erreur : {e}")
                self._set_status(f"❌ Erreur chargement : {e}", "#e74c3c")

        threading.Thread(target=load, daemon=True).start()

    # ── Prédiction ──────────────────────────────────────────
    def _predict(self, drug1: str, drug2: str) -> dict:
        import torch
        import numpy as np

        text = f"{drug1.lower()} interacts with {drug2.lower()}"
        enc  = self.tokenizer(
            text,
            return_tensors='pt',
            max_length=64,
            truncation=True,
            padding='max_length'
        )
        with torch.no_grad():
            logits = self.model(**enc).logits
            proba  = torch.softmax(logits, dim=1).numpy()[0]
            pred   = int(np.argmax(proba))

        return {
            'drug1':      drug1,
            'drug2':      drug2,
            'label':      pred,
            'risk':       LABEL_MAP[pred],
            'confidence': round(float(proba[pred]) * 100, 1),
            'p_mild':     round(float(proba[0]) * 100, 1),
            'p_caution':  round(float(proba[1]) * 100, 1),
            'p_danger':   round(float(proba[2]) * 100, 1),
            'gemini':     pred > 0
        }

    # ── Actions UI ──────────────────────────────────────────
    def _add_drug(self):
        name = self.drug_entry.get().strip().title()
        if not name:
            return
        existing = list(self.drug_listbox.get(0, "end"))
        if name in existing:
            messagebox.showwarning("Doublon", f"{name} est déjà dans la liste")
            return
        self.drug_listbox.insert("end", name)
        self.drug_entry.delete(0, "end")
        self._log(f"+ Ajouté : {name}")

    def _remove_drug(self):
        sel = self.drug_listbox.curselection()
        if sel:
            name = self.drug_listbox.get(sel[0])
            self.drug_listbox.delete(sel[0])
            self._log(f"- Supprimé : {name}")

    def _clear_drugs(self):
        self.drug_listbox.delete(0, "end")
        self._clear_results()
        self._log("🔄 Liste vidée")

    def _load_example(self, drugs):
        self.drug_listbox.delete(0, "end")
        for d in drugs:
            self.drug_listbox.insert("end", d)
        self._log(f"📋 Exemple chargé : {', '.join(drugs)}")

    def _analyze(self):
        drugs = list(self.drug_listbox.get(0, "end"))
        if len(drugs) < 2:
            messagebox.showwarning("Attention", "Ajoute au moins 2 médicaments")
            return
        if not self.model_loaded:
            messagebox.showwarning("Attention", "Le modèle n'est pas encore chargé")
            return

        self.analyze_btn.config(state="disabled", text="⏳ Analyse en cours...")
        self._clear_results()
        self._set_status("⏳ Analyse en cours...", "#f39c12")

        def run():
            try:
                pairs = list(combinations(drugs, 2))
                results = []
                for i, (d1, d2) in enumerate(pairs):
                    self._log(f"🔍 [{i+1}/{len(pairs)}] {d1} + {d2}")
                    r = self._predict(d1, d2)
                    results.append(r)

                results.sort(key=lambda x: -x['label'])
                self.root.after(0, lambda: self._show_results(results))

            except Exception as e:
                self._log(f"❌ Erreur analyse : {e}")
                self._set_status(f"❌ Erreur : {e}", "#e74c3c")
                self.root.after(0, lambda: self.analyze_btn.config(
                    state="normal", text="⚡ Analyser les interactions"))

        threading.Thread(target=run, daemon=True).start()

    def _show_results(self, results):
        self._clear_results()
        counts = {0: 0, 1: 0, 2: 0}

        for r in results:
            counts[r['label']] += 1
            icon = EMOJI_MAP[r['label']]
            self.tree.insert("", "end",
                values=(
                    r['drug1'],
                    r['drug2'],
                    f"{icon} {r['risk']}",
                    f"{r['confidence']}%",
                    "✅ Oui" if r['gemini'] else "—"
                ),
                tags=(r['risk'],)
            )

        total = len(results)
        summary = (
            f"📊 {total} interaction(s) analysée(s) :  "
            f"🔴 {counts[2]} DANGER   "
            f"🟡 {counts[1]} CAUTION   "
            f"🟢 {counts[0]} MILD"
        )
        if counts[2] > 0:
            summary += f"  ⚠️  {counts[2]} interaction(s) dangereuse(s) détectée(s) !"

        self.summary_var.set(summary)
        self._log(f"✅ Analyse terminée — {total} paires")
        self._set_status("✅ Analyse terminée", "#2ecc71")
        self.analyze_btn.config(state="normal", text="⚡ Analyser les interactions")

    def _clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.summary_var.set("")

    def _set_status(self, msg, color="#f39c12"):
        self.root.after(0, lambda: (
            self.status_var.set(msg),
            self.status_lbl.config(fg=color)
        ))

    def _log(self, msg):
        def _write():
            self.log.config(state="normal")
            self.log.insert("end", msg + "\n")
            self.log.see("end")
            self.log.config(state="disabled")
        self.root.after(0, _write)


# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app  = MedSafeApp(root)
    root.mainloop()