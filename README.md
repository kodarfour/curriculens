# **CurricuLens ![CurricuLens Logo](https://github.com/kodarfour/curriculens/blob/main/images/curriculens.ico)<br/>The UVA Course Schedule Optimization Website**

A web application that helps UVA students optimize their course schedules for upcoming semesters by parsing existing enrolled schedules, filtering out previously taken courses, and allowing users to prioritize difficulty, course attributes, and preferred time slots.

---

## **Features**

- **Upload and Parse `.ics` Files**  
  Users can upload `.ics` files of their current enrolled schedules. The system extracts enrolled courses and excludes them from future suggestions.

- **Customizable Preferences**  
  Students can set preferences for:
  - Maximum/Minimum course difficulty (based on historical data from TheCourseForum).
  - Course attributes (e.g., Writing Requirement, Science & Technology).
  - Time constraints (e.g., avoid early morning classes).

- **Optimized Schedule Generation**  
  The backend generates an optimized schedule by:
  - Querying a database of UVA courses (scraped from TheCourseForum and UVA's SIS API).
  - Applying user-defined preferences to filter out unwanted courses.
  - Suggesting a schedule that maximizes convenience and meets user criteria.

- **Export Schedule as `.ics`**  
  The generated schedule can be exported as an `.ics` file to be imported into any calendar application. Class commute durations will also proividee for the top schedule reccomendations (powered by Google Maps API).

---

## **Technology Stack (WIP)**

### **Backend**
- **Language**: Go
- **Framework**: Gin or Echo for REST APIs (TBD)
- **Microservices**: Each core function is implemented as an independent microservice.
- **Database**: PostgreSQL (hosted on Google Cloud SQL, TBD)
- **Deployment**: Google Cloud Run (TBD)

### **Frontend**
- **Framework**: React (TBD, possibly BootStrap)
- **Styling**: Tailwind CSS (TBD)
- **Deployment**: Firebase Hosting (TBD)

### **Data Collection**
- **Web Scraping**: Python scripts using `requests` and `BeautifulSoup`
- **Sources**:
  - SIS API (for course data)
  - TheCourseForum (for difficulty ratings and grade distributions)
  - Google Maps API (for class commute times)
