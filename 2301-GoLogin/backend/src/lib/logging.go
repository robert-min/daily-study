package lib

import (
	"io"
	"log"
	"os"
	"time"
)

type Logger struct {
	InfoFile    *log.Logger
	InfoSystem  *log.Logger
	ErrorFile   *log.Logger
	ErrorSystem *log.Logger
}

var logger Logger

func logging(logfile *os.File, handler io.Writer, logType string) (filelogger *log.Logger, systemlogger *log.Logger) {
	filelogger = log.New(logfile, logType+" ", log.Ldate|log.Ltime|log.Lshortfile)
	systemlogger = log.New(handler, logType+" ", log.Ldate|log.Ltime|log.Lshortfile)
	return
}

func LogInit(infoHandler io.Writer, errorHandler io.Writer) {
	now := time.Now().UTC()
	path := "./login-api/logs/" + now.Format("2006-01-01")
	logfile, _ := os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	logger.InfoFile, logger.InfoSystem = logging(logfile, infoHandler, "[INFO]")
	logger.ErrorFile, logger.ErrorSystem = logging(logfile, errorHandler, "[ERROR]")
}

func LogInfo(infoMessage string) {
	logger.InfoFile.Println(infoMessage)
	logger.InfoSystem.Println(infoMessage)
}

func LogError(ErrorMessage string) {
	logger.ErrorFile.Println(ErrorMessage)
	logger.ErrorSystem.Println(ErrorMessage)
}
