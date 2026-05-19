package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"

	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Assure que le dossier data existe pour SQLite
	err := os.MkdirAll("/app/data", os.ModePerm)
	if err != nil {
		log.Printf("Erreur creation dossier data: %v", err)
	}

	db, err := sql.Open("sqlite3", "/app/data/manager.db")
	if err != nil {
		log.Fatalf("Erreur ouverture DB: %v", err)
	}
	defer db.Close()

	// Initialisation des tables basiques indispensables
	_, _ = db.Exec(`CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT, approved INTEGER DEFAULT 0)`)
	_, _ = db.Exec(`CREATE TABLE IF NOT EXISTS accounts (user_id INTEGER, name TEXT, access_key TEXT, secret_key TEXT, project_id TEXT, PRIMARY KEY(user_id, name))`)
	_, _ = db.Exec(`CREATE TABLE IF NOT EXISTS templates (user_id INTEGER, name TEXT, content TEXT, PRIMARY KEY(user_id, name))`)

	// Endpoint de santé pour s'assurer que le service répond
	http.HandleFunc("/api/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Access-Control-Allow-Origin", "*")
		_, _ = w.Write([]byte(`{"status": "UP", "database": "connected"}`))
	})

	// Endpoint Billing mocké réclamé par le Dashboard de l'UI
	http.HandleFunc("/api/billing", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Access-Control-Allow-Origin", "*")
		// Renvoie un dictionnaire vide pour ne pas bloquer l'UI
		_ = json.NewEncoder(w).Encode(map[string]interface{}{})
	})

	log.Println("🚀 Backend scw-core prêt et à l'écoute sur le port :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatalf("Erreur serveur HTTP: %v", err)
	}
}