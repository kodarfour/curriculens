package parser

import (
	"fmt"
	"os"
	"strconv"
	"strings"

	ics "github.com/arran4/golang-ical"
)

type Course struct {
	Subject      string
	CourseNumber int
}

func ParseICS(filePath string) ([]Course, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var TakenCourses []Course

	calendar, err := ics.ParseCalendar(file)
	if err != nil {
		return nil, err
	}

	// Iterate through events
	for _, event := range calendar.Events() {
		// Extract the SUMMARY field
		summaryProperty := event.GetProperty(ics.ComponentPropertySummary)
		summary := ""
		if summaryProperty != nil {
			summary = strings.TrimSpace(summaryProperty.Value)
		} else {
			fmt.Println("Missing SUMMARY field for an event, skipping.")
			continue
		}

		// Parse subject and course number from SUMMARY
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

		// Create the course struct and append to the list
		CurrentCourse := Course{Subject: subject, CourseNumber: courseNumber}
		TakenCourses = append(TakenCourses, CurrentCourse)

		fmt.Printf("Added Course: %s %d\n", subject, courseNumber)
	}

	return TakenCourses, nil
}
