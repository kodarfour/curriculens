package main

import (
	"fmt"
	"log"

	"go-backend/schedule-processor/internal/parser"
)

func main() {
	filePath := "internal/parser/ics_files/2024_Fall_calendar.ics" 

	takenCourses, err := parser.ParseICS(filePath)
	if err != nil {
		log.Fatalf("Error parsing ICS file: %v", err)
	}

	fmt.Println("Parsed Courses:")
	for _, course := range takenCourses {
		fmt.Printf("Subject: %s, Course Number: %d\n", course.Subject, course.CourseNumber)
	}
}