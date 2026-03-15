package services

import (
	"context"

	"gorm.io/gorm"

	"github.com/kodlooper/mail_english_story_backend/internal/modules/subscriber/models"
)

type SubscriberService interface {
	SubscribeUser(ctx context.Context, input models.SubscriberInput) error
}

type subscriberService struct {
	db *gorm.DB
}

func NewSubscriberService(db *gorm.DB) SubscriberService {
	return &subscriberService{db: db}
}

func (s *subscriberService) SubscribeUser(ctx context.Context, input models.SubscriberInput) error {
	subscriber := models.Subscriber{
		Email: input.Email,
		Level: input.Level,
	}
	return s.db.WithContext(ctx).Create(&subscriber).Error
}
