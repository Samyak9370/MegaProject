# AI Debate Partner - Frontend

A React-based frontend for the AI Debate Partner application that provides real-time speech analysis and feedback for debaters.

## Features

- 🎤 Real-time speech recording and analysis
- 📊 Interactive feedback dashboard
- 📈 Performance metrics and visualizations
- 🔄 WebSocket integration for live updates
- 📱 Responsive design for all devices

## Prerequisites

- Node.js 16+ and npm/yarn
- Backend server running (see backend README for setup)

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-debate-partner.git
   cd ai-debate-partner/ai-debate-partner-ui
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Create a `.env` file in the project root with the following content:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   VITE_WS_URL=ws://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. Open [http://localhost:5173](http://localhost:5173) in your browser.

## Project Structure

```
src/
├── assets/           # Static assets (images, styles, etc.)
├── components/       # Reusable React components
├── hooks/            # Custom React hooks
├── pages/            # Page components
├── services/         # API and service functions
├── utils/            # Utility functions
├── App.jsx           # Main application component
└── main.jsx          # Application entry point
```

## Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build for production
- `npm run preview` - Preview the production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Base URL for API requests | `http://localhost:8000` |
| `VITE_WS_URL` | WebSocket server URL | `ws://localhost:8000` |

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
