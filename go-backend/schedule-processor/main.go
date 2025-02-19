package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	"go-backend/schedule-processor/internal/parser"
	"go-backend/schedule-processor/internal/validator"

	"github.com/jackc/pgx/v5/pgxpool"
)

func main() {
	// Load database config from environment variables
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		log.Fatal("DATABASE_URL is not set. Ensure it is provided as an environment variable.")
	}

	// Establish database connection pool
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	dbpool, err := pgxpool.New(ctx, dbURL)
	if err != nil {
		log.Fatalf("Unable to create database pool: %v", err)
	}
	defer dbpool.Close()

	// Load courses from ICS file
	filePath := "/app/2024_Spring_calendar.ics" // inside Docker container
	takenCourses, err := parser.ParseICS(filePath)
	if err != nil {
		log.Fatalf("Error parsing ICS file: %v", err)
	}

	// Initialize validator
	validator := validator.NewValidator(dbpool)

	// Validate courses
	results := validator.ValidateCourses(ctx, takenCourses)

	// Print validation results
	fmt.Println("Course Validation Results:")
	for course, exists := range results {
		status := "✅ Exists"
		if !exists {
			status = "❌ Not Found"
		}
		fmt.Printf("Subject: %s, Course Number: %d -> %s\n", course.Subject, course.CourseNumber, status)
	}
}
