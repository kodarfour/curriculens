package validator

import (
	"context"
	"log"

	"go-backend/schedule-processor/internal/models"

	"github.com/jackc/pgx/v5/pgxpool"
)

type Validator struct {
	DB *pgxpool.Pool
}

// NewValidator initializes a new Validator with a database pool
func NewValidator(db *pgxpool.Pool) *Validator {
	return &Validator{DB: db}
}

// CourseExists checks if a course exists in the database
func (v *Validator) CourseExists(ctx context.Context, course models.Course) bool {
	query := `SELECT EXISTS(SELECT 1 FROM courses WHERE subject = $1 AND course_number = $2)`
	var exists bool

	err := v.DB.QueryRow(ctx, query, course.Subject, course.CourseNumber).Scan(&exists)
	if err != nil {
		log.Printf("Error checking course %s %d: %v", course.Subject, course.CourseNumber, err)
		return false
	}

	return exists
}

// ValidateCourses checks multiple courses and returns a map of validation results
func (v *Validator) ValidateCourses(ctx context.Context, courses []models.Course) map[models.Course]bool {
	results := make(map[models.Course]bool)
	for _, course := range courses {
		results[course] = v.CourseExists(ctx, course)
	}
	return results
}
