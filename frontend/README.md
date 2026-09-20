# LeadBot AI — Frontend

Animated React frontend for the AI-powered lead generation system.

## Tech Stack

| Library | Version | Purpose |
|---|---|---|
| React | 19 | UI framework |
| Vite | 8 | Build tool |
| Tailwind CSS | 3 | Styling |
| Framer Motion | latest | Animations |
| React Router | 6 | Routing |
| Lucide React | latest | Icons |

## Pages

| Route | Description |
|---|---|
| `/` | Landing page — Hero, Stats, Services, How It Works, Testimonials, FAQ, Contact |
| `/dashboard` | Lead dashboard — filterable, searchable lead cards with score bars |
| `/run` | Run Automation — trigger lead generation jobs with live terminal output |
| `*` | 404 Not Found page |

## Project Structure

```
frontend/
├── index.html
├── vite.config.js
├── tailwind.config.js
├── src/
│   ├── App.jsx              # Router + layout
│   ├── main.jsx             # Entry point
│   ├── index.css            # Tailwind + global styles
│   ├── components/
│   │   ├── Navbar.jsx       # Sticky glass navbar
│   │   ├── Footer.jsx       # Footer with social links
│   │   ├── ParticleBackground.jsx  # Canvas particle network
│   │   ├── AnimatedCounter.jsx     # Count-up on scroll
│   │   └── GlowOrb.jsx     # Ambient glow blobs
│   ├── sections/
│   │   ├── Hero.jsx         # Full-screen hero with animations
│   │   ├── Stats.jsx        # Animated stat grid
│   │   ├── Services.jsx     # 3 service cards
│   │   ├── HowItWorks.jsx   # 4-step pipeline
│   │   ├── Testimonials.jsx # Carousel with client reviews
│   │   ├── FAQ.jsx          # Accordion FAQ
│   │   └── Contact.jsx      # Contact form + info
│   ├── pages/
│   │   ├── LandingPage.jsx  # Composes all sections
│   │   ├── Dashboard.jsx    # Lead dashboard
│   │   ├── RunAutomation.jsx # Job runner UI
│   │   └── NotFound.jsx     # 404 page
│   └── data/
│       └── mockLeads.js     # Sample lead data for dashboard
```

## Getting Started

```bash
# Install dependencies
cd frontend
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

## Key Animations

- **Particle network** — canvas-based floating dots with connecting lines
- **Framer Motion** — scroll-triggered entrance animations on every section
- **Score bars** — spring-eased progress bars on lead cards
- **Testimonials carousel** — smooth slide transitions
- **FAQ accordion** — animated height expansion
- **Counter** — count-up on scroll into view
- **Gradient borders** — animated `background-position` borders on key CTAs
- **Hover effects** — lift, glow, and scale on all interactive cards

## Environment

No environment variables needed for the frontend.  
The backend API URL can be configured in `src/api/` (to be added when connecting to live backend).

## Backend Connection

Connect to the Python backend by pointing fetch calls at:
```
http://localhost:8000/api/leads
http://localhost:8000/api/run
```

See `backend/` for the FastAPI server (add as needed).
