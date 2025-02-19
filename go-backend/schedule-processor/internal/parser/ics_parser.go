package parser

import (
	"fmt"
	"os"
	"strconv"
	"strings"

	"go-backend/schedule-processor/internal/models"

	ics "github.com/arran4/golang-ical"
)

func ParseICS(filePath string) ([]models.Course, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var TakenCourses []models.Course

	calendar, err := ics.ParseCalendar(file)
	if err != nil {
		return nil, err
	}

	// Iterate through events
	for _, event := range calendar.Events() {
		// Access SUMMARY field information
		summaryProperty := event.GetProperty(ics.ComponentPropertySummary)
		summary := ""
		if summaryProperty != nil {
			summary = strings.TrimSpace(summaryProperty.Value)
		} else {
			fmt.Println("Missing SUMMARY field for an event, skipping.")
			continue
		}

		// Parse subject and course number from SUMMARY field
		parts := strings.Fields(summary)
		if len(parts) != 2 {
			fmt.Printf("Invalid SUMMARY format: %s\n", summary)
			continue
		}

		subject := parts[0]
		courseNumber, err := strconv.Atoi(parts[1])
		if err != nil {
			fmt.Printf("Invalid course number in SUMMARY: %s\n", summary)
			continue
		}

		CurrentCourse := models.Course{Subject: subject, CourseNumber: courseNumber}
		TakenCourses = append(TakenCourses, CurrentCourse)

		fmt.Printf("Added Course: %s %d\n", subject, courseNumber)
	}

	return TakenCourses, nil
}
