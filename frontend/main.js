import "../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "../node_modules/bootstrap/dist/js/bootstrap.bundle.min.js";

// main.js
function loadPage(page) {
    const root = document.getElementById('root');
    root.innerHTML = ''; // Clear existing content
  
    switch (page) {
      case 'home':
        root.innerHTML = `<h1>Home Page</h1><p>Upload your file here.</p>`;
        break;
      case 'preferences':
        root.innerHTML = `<h1>Preferences Page</h1><p>Set your options here.</p>`;
        break;
      case 'results':
        root.innerHTML = `<h1>Results Page</h1><p>View your optimized schedule here.</p>`;
        break;
      default:
        root.innerHTML = `<h1>404</h1><p>Page not found.</p>`;
    }
  }
  
  // Initial Load
  loadPage('home');
  