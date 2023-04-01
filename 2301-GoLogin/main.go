package main

import (
	"net/http"
	"project-go/login-api/backend/src/api"
)

func main() {
	m := api.MakeHandler("./login-api/backend/test.db")
	http.ListenAndServe(":8080", m)
}
