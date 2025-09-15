# Sauti Helpline Wallboard

A modern Vue.js wallboard application for monitoring counsellors and displaying real-time statistics for the Sauti Helpline.

## Features

- **Counsellors Online**: Real-time display of active counsellors with their extension, phone number, and time online
- **Bento Grid Statistics**: 6 interactive cards showing key metrics including:
  - Active Calls
  - Calls Today
  - Average Wait Time
  - Resolution Rate
  - Satisfaction Score
  - Peak Hours
- **Search & Filter**: Search functionality and filter buttons with 30px border radius
- **Responsive Design**: Optimized for different screen sizes
- **Real-time Updates**: Simulated live data updates

## Design

- **Fonts**: SF Compact Display (primary) and Roboto Sans (fallback)
- **Styling**: Modern dark theme with gradient backgrounds
- **Border Radius**: 30px for buttons and input fields
- **Color Scheme**: Professional blue and cyan gradients

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm run dev
   ```

3. **Build for Production**:
   ```bash
   npm run build
   ```

4. **Preview Production Build**:
   ```bash
   npm run preview
   ```

## Project Structure

```
wallboard/
├── index.html          # Main HTML file
├── package.json        # Dependencies and scripts
├── vite.config.js      # Vite configuration
└── src/
    ├── main.js         # Vue app entry point
    ├── App.vue         # Main application component
    └── style.css       # Global styles
```

## Technologies Used

- **Vue 3** - Progressive JavaScript framework
- **Vite** - Fast build tool and development server
- **CSS3** - Modern styling with CSS Grid and Flexbox
- **Google Fonts** - SF Compact Display and Roboto Sans

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Customization

The application is built with modularity in mind. You can easily:
- Add new counsellors by updating the `counsellors` array in `App.vue`
- Modify statistics by updating the `stats` array
- Change colors by updating CSS custom properties in `style.css`
- Add new filter categories by updating the `filters` array

