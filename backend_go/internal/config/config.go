package config

import (
	"log"
	"os"
	"path/filepath"

	"github.com/joho/godotenv"
)

type Config struct {
	DBUser      string
	DBPassword  string
	DBHost      string
	DBPort      string
	DBName      string
	DatabaseURL string
	ServerPort  string
}

func LoadConfig() Config {
	err := godotenv.Load(filepath.Join(".", ".env"))
	if err != nil {
		log.Println("No .env file found, using OS env variables if available")
	}

	serverPort := os.Getenv("SERVER_PORT")
	if serverPort == "" {
		serverPort = os.Getenv("PORT") // Railway standard
	}
	if serverPort == "" {
		serverPort = "8000"
	}

	// Railway ve diğer platformlarda farklı isimlerle gelebilir
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		dbURL = os.Getenv("POSTGRES_URL")
	}
	if dbURL == "" {
		dbURL = os.Getenv("DATABASE_PRIVATE_URL")
	}

	return Config{
		DBUser:      os.Getenv("DB_USER"),
		DBPassword:  os.Getenv("DB_PASSWORD"),
		DBHost:      os.Getenv("DB_HOST"),
		DBPort:      os.Getenv("DB_PORT"),
		DBName:      os.Getenv("DB_NAME"),
		DatabaseURL: dbURL,
		ServerPort:  serverPort,
	}
}
