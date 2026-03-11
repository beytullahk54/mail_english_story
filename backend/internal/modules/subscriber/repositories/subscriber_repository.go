package repositories

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/kodlooper/mail_english_story_backend/internal/modules/subscriber/models"
)

type SubscriberRepository interface {
	CreateSubscriber(ctx context.Context, input models.SubscriberInput) error
	GetSubscriberByEmail(ctx context.Context, email string) (*models.Subscriber, error)
}

type subscriberRepository struct {
	db *pgxpool.Pool
}

func NewSubscriberRepository(db *pgxpool.Pool) SubscriberRepository {
	return &subscriberRepository{db: db}
}

func (r *subscriberRepository) CreateSubscriber(ctx context.Context, input models.SubscriberInput) error {
	query := `INSERT INTO subscribers (email, level) VALUES ($1, $2)`
	_, err := r.db.Exec(ctx, query, input.Email, input.Level)
	return err
}

func (r *subscriberRepository) GetSubscriberByEmail(ctx context.Context, email string) (*models.Subscriber, error) {
	query := `SELECT id, email, level, created_at FROM subscribers WHERE email = $1`
	row := r.db.QueryRow(ctx, query, email)

	var s models.Subscriber
	err := row.Scan(&s.ID, &s.Email, &s.Level, &s.CreatedAt)
	if err != nil {
		return nil, err
	}

	return &s, nil
}
