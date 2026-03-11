package main

import (
	"log"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/kodlooper/mail_english_story_backend/internal/config"
	"github.com/kodlooper/mail_english_story_backend/internal/database"

	subscriberHandlers "github.com/kodlooper/mail_english_story_backend/internal/modules/subscriber/handlers"
	subscriberRepositories "github.com/kodlooper/mail_english_story_backend/internal/modules/subscriber/repositories"
	subscriberServices "github.com/kodlooper/mail_english_story_backend/internal/modules/subscriber/services"
)

func main() {
	// Load config and connect to DB
	cfg := config.LoadConfig()
	database.ConnectDB(cfg)

	app := fiber.New()

	// Middleware
	app.Use(logger.New())
	app.Use(cors.New()) // Allow frontend to call the API

	// Setup dependencies (Repository -> Service -> Handler)
	subscriberRepo := subscriberRepositories.NewSubscriberRepository(database.DB)
	subscriberServ := subscriberServices.NewSubscriberService(subscriberRepo)
	subscriberHand := subscriberHandlers.NewSubscriberHandler(subscriberServ)

	// Routing Module
	api := app.Group("/api")
	v1 := api.Group("/v1")

	// Subscription Routes
	subscriberRoutes := v1.Group("/subscribe")
	subscriberRoutes.Post("/", subscriberHand.Subscribe)

	log.Printf("Starting server on port %s...", cfg.ServerPort)
	err := app.Listen(":" + cfg.ServerPort)
	if err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
}
