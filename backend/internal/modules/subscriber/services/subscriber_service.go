package services

import (
	"context"

	"github.com/kodlooper/mail_english_story_backend/internal/modules/subscriber/models"
	"github.com/kodlooper/mail_english_story_backend/internal/modules/subscriber/repositories"
)

type SubscriberService interface {
	SubscribeUser(ctx context.Context, input models.SubscriberInput) error
}

type subscriberService struct {
	repo repositories.SubscriberRepository
}

func NewSubscriberService(repo repositories.SubscriberRepository) SubscriberService {
	return &subscriberService{repo: repo}
}

func (s *subscriberService) SubscribeUser(ctx context.Context, input models.SubscriberInput) error {
	// Add business logic if necessary, e.g. validate email format.
	return s.repo.CreateSubscriber(ctx, input)
}
