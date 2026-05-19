package main

import (
	"encoding/json"
	"log"
	"net/http"
)

func main() {
	// Endpoint de santé pour l'UI
	http.HandleFunc("/api/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"status": "UP", "message": "Moteur Go opérationnel"}`))
	})

	// Endpoint Billing réclamé par le Dashboard de l'UI
	http.HandleFunc("/api/billing", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		// Renvoie un dictionnaire vide ou mocké pour parer les blocages graphiques
		_ = json.NewEncoder(w).Encode(map[string]interface{}{
			"status": "active",
		})
	})

	log.Println("🚀 Backend scw-core ultra-léger démarré sur le port :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatalf("Erreur serveur HTTP : %v", err)
	}
}