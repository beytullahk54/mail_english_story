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
		serverPort = os.Getenv("PORT") // Railway uses PORT
	}
	if serverPort == "" {
		serverPort = "8000" // Default
	}

	return Config{
		DBUser:      os.Getenv("DB_USER"),
		DBPassword:  os.Getenv("DB_PASSWORD"),
		DBHost:      os.Getenv("DB_HOST"),
		DBPort:      os.Getenv("DB_PORT"),
		DBName:      os.Getenv("DB_NAME"),
		DatabaseURL: os.Getenv("DATABASE_URL"),
		ServerPort:  serverPort,
	}
}
