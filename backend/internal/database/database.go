package database

import (
	"context"
	"fmt"
	"log"
	"strings"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/kodlooper/mail_english_story_backend/internal/config"
)

var DB *pgxpool.Pool

func ConnectDB(cfg config.Config) {
	dsn := cfg.DatabaseURL

	// Fallback planı: Parçalı verileri kontrol et
	if dsn == "" {
		// Eğer DBName veya DBHost içinde zaten bir protokol varsa (örn postgres://),
		// kullanıcı yanlışlıkla değişkeni böyle set etmiş olabilir.
		if strings.HasPrefix(cfg.DBName, "postgres") {
			dsn = cfg.DBName
		} else if strings.HasPrefix(cfg.DBHost, "postgres") {
			dsn = cfg.DBHost
		} else {
			dsn = fmt.Sprintf("postgres://%s:%s@%s:%s/%s?sslmode=disable",
				cfg.DBUser, cfg.DBPassword, cfg.DBHost, cfg.DBPort, cfg.DBName)
		}
	}

	// Logging (mask password)
	maskedDSN := dsn
	if strings.Contains(dsn, ":") && strings.Contains(dsn, "@") {
		// Basit bir maskeleme: @ öncesindeki şifreyi gizle
		parts := strings.Split(dsn, "@")
		userPass := strings.Split(parts[0], ":")
		if len(userPass) > 2 {
			maskedDSN = userPass[0] + ":" + userPass[1] + ":****@" + parts[1]
		}
	}
	log.Printf("Connecting to database with DSN: %s", maskedDSN)

	poolConfig, err := pgxpool.ParseConfig(dsn)
	if err != nil {
		log.Fatalf("Unable to parse connection string: %v | DSN was: %s", err, maskedDSN)
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
