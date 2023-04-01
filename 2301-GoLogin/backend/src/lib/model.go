package lib

import "time"

type User struct {
	ID       string    `json:"id"`
	Password string    `json:"password"`
	CreateAt time.Time `json:"created_at"`
}

type DBHandler interface {
	GetAllUsers() []*User
	GetUser(id string) User
	AddNewUser(id string, password string) *User
	DeleteUser(id string) string
	Close()
}

func NewDBHandler(filepath string) DBHandler {
	return NewSqliteHandler(filepath)
}
