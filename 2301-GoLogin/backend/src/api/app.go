package api

import (
	"encoding/json"
	"io/ioutil"
	"net/http"
	"os"
	"project-go/login-api/backend/src/lib"

	"github.com/gorilla/mux"
	"github.com/unrolled/render"
	"github.com/urfave/negroni"
)

var rd *render.Render = render.New()

type AppHandler struct {
	http.Handler
	db lib.DBHandler
}

func (a *AppHandler) getAllUsersHandler(w http.ResponseWriter, r *http.Request) {
	users := a.db.GetAllUsers()
	rd.JSON(w, http.StatusOK, users)
	lib.LogInfo("200 | GET /user")
}

func (a *AppHandler) addNewUserHandler(w http.ResponseWriter, r *http.Request) {
	vars, err := ioutil.ReadAll(r.Body)
	errorHandler(err)
	var user lib.User
	err = json.Unmarshal(vars, &user)
	errorHandler(err)
	ok := a.db.AddNewUser(user.ID, user.Password)
	rd.JSON(w, http.StatusOK, ok)
	lib.LogInfo("200 | POST /user")
}

func (a *AppHandler) deleteUserHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := a.db.DeleteUser(vars["id"])
	rd.JSON(w, http.StatusOK, id)
	lib.LogInfo("200 | DELETE /user/" + vars["id"])
}

func MakeHandler(filepath string) *AppHandler {
	lib.LogInit(os.Stdout, os.Stderr)

	mux := mux.NewRouter()
	n := negroni.New(
		negroni.NewLogger(),
		negroni.NewRecovery(),
	)
	n.UseHandler(mux)

	a := &AppHandler{
		Handler: n,
		db:      lib.NewDBHandler(filepath),
	}
	mux.HandleFunc("/user", a.getAllUsersHandler).Methods("GET")
	mux.HandleFunc("/user", a.addNewUserHandler).Methods("POST")
	mux.HandleFunc("/user/{id}", a.deleteUserHandler).Methods("DELETE")
	mux.HandleFunc("/login", a.loginHandler).Methods("POST")

	return a
}

func errorHandler(err error) {
	if err != nil {
		lib.LogError(err.Error())
		panic(err)
	}
}
