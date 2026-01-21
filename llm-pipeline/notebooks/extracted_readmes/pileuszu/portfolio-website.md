# Portfolio Website

A sleek and modern portfolio website built with TypeScript, React, Next.js, and SCSS. Features a clean design with smooth animations and responsive layout.

## Tech Stack

- **Frontend**: React 18, Next.js 15, TypeScript
- **Styling**: SCSS, CSS Modules
- **Design**: Modern Gray & White Theme with Beige Accents
- **Animation**: CSS Animations, Smooth Transitions
- **Development**: ESLint 9, Modern Build Tools

## Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout with navigation
│   └── page.tsx           # Home page with all sections
├── data/                  # Static data files
│   ├── projects.json      # Featured projects data
│   ├── experience.json    # Professional experience
│   ├── study.json         # Learning & blog posts
│   └── contact.json       # Contact information
└── styles/               # Global styles
    └── globals.scss      # Global SCSS variables and base styles
```

## Installation & Setup

### Prerequisites
- Node.js 18 or higher
- npm or yarn

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The development server will start at [http://localhost:3000](http://localhost:3000).

### Build for Production
```bash
# Create production build
npm run build

# Start production server
npm start
```

## Content Management
Update data in the JSON files in `src/data/`:

- **projects.json**: Featured projects with descriptions and tech stacks
- **experience.json**: Professional experience and education
- **study.json**: Learning posts and blog articles
- **contact.json**: Contact methods and information

## Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Netlify
```bash
# Build
npm run build

# Upload the generated files to Netlify
```

## License

MIT License - Feel free to use and modify as needed.