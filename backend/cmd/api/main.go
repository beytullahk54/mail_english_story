package main

import (
	"log"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/kodlooper/mail_english_story_backend/internal/config"
	"github.com/kodlooper/mail_english_story_backend/internal/database"
	subscriberModels "github.com/kodlooper/mail_english_story_backend/internal/modules/subscriber/models"

	subscriberHandlers "github.com/kodlooper/mail_english_story_backend/internal/modules/subscriber/handlers"
	subscriberServices "github.com/kodlooper/mail_english_story_backend/internal/modules/subscriber/services"
)

func main() {
	// Load config and connect to DB
	cfg := config.LoadConfig()
	database.ConnectDB(cfg)

	// Auto migrate models
	if err := database.DB.AutoMigrate(&subscriberModels.Subscriber{}); err != nil {
		log.Fatalf("AutoMigrate failed: %v", err)
	}

	app := fiber.New()

	// Middleware
	app.Use(logger.New())
	app.Use(cors.New()) // Allow frontend to call the API

	// Setup dependencies (Service -> Handler)
	subscriberServ := subscriberServices.NewSubscriberService(database.DB)
	subscriberHand := subscriberHandlers.NewSubscriberHandler(subscriberServ)

	// Routing Module
	api := app.Group("/api")
	v1 := api.Group("/v1")

	// Subscription Routes
	subscriberRoutes := v1.Group("/subscribe")
	subscriberRoutes.Post("/", subscriberHand.Subscribe)

	// Health Check
	app.Get("/health", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{
			"status": "ok",
		})
	})

	log.Printf("Starting server on port %s...", cfg.ServerPort)
	err := app.Listen(":" + cfg.ServerPort)
	if err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
}
