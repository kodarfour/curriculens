package main

import (
	"fmt"
	"log"

	"go-backend/schedule-processor/internal/parser"
)

func main() {
	filePath := "/app/2024_Spring_calendar.ics" //inside docker container

	takenCourses, err := parser.ParseICS(filePath)
	if err != nil {
		log.Fatalf("Error parsing ICS file: %v", err)
	}

	fmt.Println("Parsed Courses:")
	for _, course := range takenCourses {
		fmt.Printf("Subject: %s, Course Number: %d\n", course.Subject, course.CourseNumber)
	}
}