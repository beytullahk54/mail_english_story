package models

import "time"

type Subscriber struct {
	ID        uint      `json:"id" gorm:"primaryKey"`
	Email     string    `json:"email" gorm:"uniqueIndex;not null"`
	Level     string    `json:"level" gorm:"size:10"`
	CreatedAt time.Time `json:"created_at"`
}

type SubscriberInput struct {
	Email string `json:"email"`
	Level string `json:"level"`
}
