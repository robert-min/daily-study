package api

import (
	"encoding/json"
	"io/ioutil"
	"net/http"
	"os"
	"project-go/login-api/backend/src/lib"

	"github.com/dgrijalva/jwt-go"
)

type Config struct {
	Secret_key string `json:"secret_key"`
}

func setConfig() *Config {
	path, _ := os.Getwd()

	var config Config
	file, err := os.Open(path + "/login-api/backend/conf/conf.json")
	errorHandler(err)
	defer file.Close()
	jsonParser := json.NewDecoder(file)
	jsonParser.Decode(&config)
	return &config
}

func newClaim(userID string) *jwt.StandardClaims {
	return &jwt.StandardClaims{
		ExpiresAt: 15000,
		Issuer:    userID,
	}
}

func creatToken(id string) string {
	at := newClaim(id)
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, at)
	config := setConfig()

	key := []byte(config.Secret_key)
	signedToken, err := token.SignedString(key)
	errorHandler(err)

	return signedToken
}

func (a *AppHandler) loginHandler(w http.ResponseWriter, r *http.Request) {
	vars, err := ioutil.ReadAll(r.Body)
	errorHandler(err)
	var user lib.User
	err = json.Unmarshal(vars, &user)
	errorHandler(err)
	rst := a.db.GetUser(user.ID)
	if user.Password != rst.Password {
		rd.JSON(w, http.StatusForbidden, "No Match password")
	}
	token := creatToken(user.ID)
	rd.JSON(w, http.StatusOK, token)

}
