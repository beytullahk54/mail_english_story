package database

import (
	"context"
	"fmt"
	"log"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/kodlooper/mail_english_story_backend/internal/config"
)

var DB *pgxpool.Pool

func ConnectDB(cfg config.Config) {
	dsn := fmt.Sprintf("postgres://%s:%s@%s:%s/%s?sslmode=disable",
		cfg.DBUser, cfg.DBPassword, cfg.DBHost, cfg.DBPort, cfg.DBName)

	poolConfig, err := pgxpool.ParseConfig(dsn)
	if err != nil {
		log.Fatalf("Unable to parse connection string: %v", err)
	}

	pool, err := pgxpool.NewWithConfig(context.Background(), poolConfig)
	if err != nil {
		log.Fatalf("Unable to create connection pool: %v", err)
	}

	pingErr := pool.Ping(context.Background())
	if pingErr != nil {
		log.Fatalf("Unable to ping database: %v", pingErr)
	}

	log.Println("Database connection established")
	DB = pool

	createTables()
}

func createTables() {
	query := `
	CREATE TABLE IF NOT EXISTS subscribers (
		id SERIAL PRIMARY KEY,
		email VARCHAR(255) UNIQUE NOT NULL,
		level VARCHAR(10),
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);`

	_, err := DB.Exec(context.Background(), query)
	if err != nil {
		log.Fatalf("Unable to create tables: %v", err)
	}
	log.Println("Tables created or verified successfully")
}
