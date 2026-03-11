package models

import "time"

type Subscriber struct {
	ID        int       `json:"id"`
	Email     string    `json:"email"`
	Level     string    `json:"level"`
	CreatedAt time.Time `json:"created_at"`
}

type SubscriberInput struct {
	Email string `json:"email"`
	Level string `json:"level"`
}
