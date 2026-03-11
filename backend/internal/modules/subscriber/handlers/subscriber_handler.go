package handlers

import (
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/kodlooper/mail_english_story_backend/internal/modules/subscriber/models"
	"github.com/kodlooper/mail_english_story_backend/internal/modules/subscriber/services"
)

type SubscriberHandler struct {
	Service services.SubscriberService
}

func NewSubscriberHandler(service services.SubscriberService) *SubscriberHandler {
	return &SubscriberHandler{Service: service}
}

func (h *SubscriberHandler) Subscribe(c *fiber.Ctx) error {
	var input models.SubscriberInput

	if err := c.BodyParser(&input); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Cannot parse JSON",
		})
	}

	if input.Email == "" {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Email is required",
		})
	}

	err := h.Service.SubscribeUser(c.Context(), input)
	if err != nil {
		if strings.Contains(err.Error(), "duplicate key value") {
			return c.Status(fiber.StatusConflict).JSON(fiber.Map{
				"error": "Email already subscribed",
			})
		}
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Could not subscribe user: " + err.Error(),
		})
	}

	return c.Status(fiber.StatusCreated).JSON(fiber.Map{
		"message": "Successfully subscribed!",
	})
}
