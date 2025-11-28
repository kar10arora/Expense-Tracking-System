# Expense Tracker with Charts and Graphs

A Django-based expense tracking application with dynamic charts and graphs that connect to the backend data.

## Features

### Charts and Graphs
- **Dashboard Charts**: 
  - Monthly expenses bar chart showing spending trends
  - Category-wise expenses pie chart showing spending distribution
- **Reports Charts**: 
  - Dynamic bar charts for different time ranges (daily, weekly, quarterly, etc.)
- **Real-time Updates**: Charts automatically refresh every 30 seconds
- **Responsive Design**: Charts adapt to different screen sizes

### Backend Integration
- **API Endpoints**: RESTful APIs for chart data
  - `/api/chart-data/` - Dashboard chart data
  - `/api/reports-chart-data/` - Reports chart data
  - `/api/test/` - Test endpoint for API verification
- **Dynamic Data**: Charts pull real data from the database
- **User-specific Data**: Each user sees only their own expense data

### Technical Features
- **Chart.js Integration**: Modern, responsive charts
- **Auto-refresh**: Charts update automatically when new data is added
- **Error Handling**: Graceful handling of empty data and API errors
- **Mobile Responsive**: Charts work well on all devices

## File Structure

```
Tracker/
├── static/
│   ├── css/
│   │   └── chart-fixes.css      # Chart styling and responsiveness
│   └── js/
│       └── charts.js            # Chart initialization and data handling
├── templates/
│   ├── dashboard.html           # Dashboard with bar and pie charts
│   └── reports.html             # Reports page with dynamic charts
├── views.py                     # API endpoints and view logic
└── urls.py                      # URL routing for API endpoints
```

## API Endpoints

### Dashboard Chart Data
- **URL**: `/api/chart-data/`
- **Method**: GET
- **Authentication**: Required (login_required)
- **Response**: JSON with monthly and category data

### Reports Chart Data
- **URL**: `/api/reports-chart-data/?range=<range_type>`
- **Method**: GET
- **Parameters**: 
  - `range`: daily, weekly, quarterly, half_yearly, yearly
- **Authentication**: Required (login_required)
- **Response**: JSON with category data for specified range

## Usage

1. **Dashboard**: Visit the dashboard to see monthly and category charts
2. **Add Expenses**: Add new expenses through the "Add Expense" form
3. **View Reports**: Use the reports page to analyze spending by different time ranges
4. **Real-time Updates**: Charts automatically update when new data is added

## Chart Features

### Bar Charts
- Show monthly expense trends
- Display category-wise spending in reports
- Include currency formatting (₹)
- Responsive to screen size changes

### Pie Charts
- Visualize spending distribution by category
- Color-coded segments
- Legend display at bottom
- Automatic color assignment

### Responsive Design
- Charts maintain aspect ratio on different devices
- Mobile-friendly touch interactions
- Print-friendly styling
- Loading and error states

## Technical Implementation

### Frontend (JavaScript)
- Uses Chart.js library for rendering
- Async/await for API calls
- Event listeners for range changes
- Auto-refresh functionality
- Error handling and fallbacks

### Backend (Django)
- Django ORM for data aggregation
- JSON responses for API endpoints
- User-specific data filtering
- Proper authentication and authorization

### Styling (CSS)
- Custom chart styling
- Responsive breakpoints
- Loading and error states
- Print media queries

## Troubleshooting

### Charts Not Loading
1. Check browser console for JavaScript errors
2. Verify API endpoints are accessible
3. Ensure user is logged in
4. Check network connectivity

### No Data Displayed
1. Verify expenses exist in database
2. Check API response in browser dev tools
3. Ensure proper date filtering
4. Verify user permissions

### Charts Not Updating
1. Check auto-refresh interval (30 seconds)
2. Verify page visibility detection
3. Check for JavaScript errors
4. Ensure API endpoints are working

## Future Enhancements

- Export charts as images
- More chart types (line charts, area charts)
- Interactive tooltips with detailed information
- Chart animations and transitions
- Real-time WebSocket updates
- Chart customization options 